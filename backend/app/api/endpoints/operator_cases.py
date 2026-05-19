from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import CaseActionRequest, CaseResultUpdateRequest
from app.core.auth import get_current_user
from app.services import operator_cases


router = APIRouter(prefix="/operator/cases", tags=["operator-cases"])


def _case_or_404(action):
    try:
        return action()
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Кейс {exc.args[0]} не найден", "code": "NOT_FOUND"},
        )


@router.get("")
async def list_operator_cases(_: dict = Depends(get_current_user)) -> list[dict[str, Any]]:
    return operator_cases.list_cases()


@router.post("/{case_id}/parse")
async def parse_operator_case(
    case_id: str,
    body: CaseActionRequest,
    _: dict = Depends(get_current_user),
) -> dict[str, Any]:
    return _case_or_404(lambda: operator_cases.parse_case(case_id, body.message))


@router.post("/{case_id}/mcp")
async def run_operator_case_mcp(
    case_id: str,
    body: CaseActionRequest,
    _: dict = Depends(get_current_user),
) -> dict[str, Any]:
    return _case_or_404(lambda: operator_cases.run_mcp(case_id, body.message))


@router.post("/{case_id}/result")
async def generate_operator_case_result(
    case_id: str,
    body: CaseActionRequest,
    _: dict = Depends(get_current_user),
) -> dict[str, Any]:
    return _case_or_404(lambda: operator_cases.generate_result(case_id, body.message))


@router.patch("/{case_id}/result")
async def update_operator_case_result(
    case_id: str,
    body: CaseResultUpdateRequest,
    _: dict = Depends(get_current_user),
) -> dict[str, Any]:
    return _case_or_404(lambda: operator_cases.update_result(case_id, body.result))
