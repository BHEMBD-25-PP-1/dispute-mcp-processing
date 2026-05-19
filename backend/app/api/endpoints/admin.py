from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import AUTH_ERROR, FORBIDDEN_ERROR, VALIDATION_ERROR
from app.api.schemas import UserCreateRequest, UserResponse
from app.core.auth import hash_password, require_admin
from app.core.database import get_db
from app.services import users


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users",
    response_model=list[UserResponse],
    responses={401: AUTH_ERROR, 403: FORBIDDEN_ERROR},
)
async def list_users(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await users.get_all_users(db)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: VALIDATION_ERROR, 401: AUTH_ERROR, 403: FORBIDDEN_ERROR},
)
async def create_user(
    body: UserCreateRequest,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await users.get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Пользователь с таким username уже существует",
                "code": "VALIDATION_ERROR",
                "details": [{"field": "username", "msg": "already exists"}],
            },
        )
    return await users.create_user(
        db,
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
    )
