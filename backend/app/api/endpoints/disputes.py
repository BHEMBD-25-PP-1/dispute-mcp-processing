import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import VALIDATION_ERROR
from app.api.schemas import (
    DisputeClaimRequest,
    DisputeProcessRequest,
    DisputeProcessResponse,
    DisputeStateResponse,
    DisputeStatusUpdateRequest,
)
from app.core.logger import logger
from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.dispute_errors import (
    DisputeConflictError,
    DisputeNotFoundError,
    InvalidDisputeTransitionError,
)
from app.services.dispute_repository import change_dispute_status, claim_dispute
from app.services.dispute_workflow import submit_dispute


router = APIRouter(tags=["disputes"])


def _correlation_id(value: str | None) -> str:
    return value or str(uuid.uuid4())


def _operator_id(current_user: dict) -> str:
    return str(current_user["sub"])


def _to_state_response(dispute) -> DisputeStateResponse:
    return DisputeStateResponse(
        dispute_id=dispute.id,
        status=dispute.status,
        version=dispute.version,
        assigned_to=dispute.assigned_to,
        locked_until=dispute.locked_until,
    )


def _raise_dispute_error(exc: Exception):
    error_map = {
        DisputeNotFoundError: (status.HTTP_404_NOT_FOUND, "NOT_FOUND"),
        InvalidDisputeTransitionError: (status.HTTP_422_UNPROCESSABLE_ENTITY, "INVALID_TRANSITION"),
        DisputeConflictError: (status.HTTP_409_CONFLICT, "VERSION_CONFLICT"),
    }
    for error_type, (status_code, code) in error_map.items():
        if isinstance(exc, error_type):
            logger.warning("Dispute API error: code=%s message=%s", code, exc)
            raise HTTPException(
                status_code=status_code,
                detail={"message": str(exc), "code": code},
            )
    raise exc


@router.post(
    "/disputes/process",
    response_model=DisputeProcessResponse,
    responses={400: VALIDATION_ERROR},
)
async def process_dispute_message(
    body: DisputeProcessRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.get("sub")
    if not body.text.strip():
        logger.warning(
            "Dispute submit rejected: reason=empty_text correlation_id=%s user_id=%s",
            correlation_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Текст диспута не может быть пустым",
                "code": "VALIDATION_ERROR",
                "details": [{"field": "text", "msg": "required"}],
            },
        )
    effective_correlation_id = _correlation_id(correlation_id)
    logger.info(
        "Dispute submit request accepted by API: user_id=%s correlation_id=%s idempotency_key_present=%s",
        user_id,
        effective_correlation_id,
        bool(idempotency_key),
    )
    return await submit_dispute(
        db,
        text=body.text,
        idempotency_key=idempotency_key,
        producer=f"user:{user_id}",
        correlation_id=effective_correlation_id,
    )


@router.post(
    "/disputes/{dispute_id}/claim",
    response_model=DisputeStateResponse,
    responses={409: {"description": "Конфликт версии или блокировки"}},
)
async def claim_dispute_for_operator(
    dispute_id: str,
    body: DisputeClaimRequest,
    correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    operator_id = _operator_id(current_user)
    effective_correlation_id = _correlation_id(correlation_id)
    logger.info(
        "Dispute claim request accepted by API: dispute_id=%s user_id=%s expected_version=%s correlation_id=%s",
        dispute_id,
        operator_id,
        body.expected_version,
        effective_correlation_id,
    )
    try:
        dispute = await claim_dispute(
            db,
            dispute_id=dispute_id,
            operator_id=operator_id,
            expected_version=body.expected_version,
            correlation_id=effective_correlation_id,
            lock_minutes=body.lock_minutes,
        )
        return _to_state_response(dispute)
    except (DisputeConflictError, DisputeNotFoundError, InvalidDisputeTransitionError) as exc:
        _raise_dispute_error(exc)


@router.patch(
    "/disputes/{dispute_id}/status",
    response_model=DisputeStateResponse,
    responses={409: {"description": "Конфликт версии или блокировки"}},
)
async def update_dispute_status(
    dispute_id: str,
    body: DisputeStatusUpdateRequest,
    correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    operator_id = _operator_id(current_user)
    effective_correlation_id = _correlation_id(correlation_id)
    logger.info(
        "Dispute status request accepted by API: dispute_id=%s user_id=%s status=%s expected_version=%s correlation_id=%s",
        dispute_id,
        operator_id,
        body.status,
        body.expected_version,
        effective_correlation_id,
    )
    try:
        dispute = await change_dispute_status(
            db,
            dispute_id=dispute_id,
            operator_id=operator_id,
            new_status=body.status,
            expected_version=body.expected_version,
            correlation_id=effective_correlation_id,
        )
        return _to_state_response(dispute)
    except (DisputeConflictError, DisputeNotFoundError, InvalidDisputeTransitionError) as exc:
        _raise_dispute_error(exc)
