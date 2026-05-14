from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from app.core.database import get_db
from app.services import users_crud as crud
from app.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    UserCreateRequest,
    UserResponse,
)

AUTH_ERROR = {
    "description": "Не авторизован",
    "content": {"application/json": {"example": {"message": "Invalid token", "code": "AUTH_ERROR"}}},
}
FORBIDDEN_ERROR = {
    "description": "Доступ запрещён",
    "content": {"application/json": {"example": {"message": "Forbidden", "code": "FORBIDDEN_ERROR"}}},
}
VALIDATION_ERROR = {
    "description": "Ошибка валидации",
    "content": {"application/json": {"example": {"message": "Ошибка валидации", "code": "VALIDATION_ERROR", "details": []}}},
}

router = APIRouter(prefix="/api/v1")


@router.post(
    "/login",
    response_model=LoginResponse,
    tags=["auth"],
    responses={401: AUTH_ERROR},
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid credentials", "code": "AUTH_ERROR"},
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return LoginResponse(access_token=token, token_type="bearer")


@router.patch(
    "/change-password",
    tags=["auth"],
    responses={400: VALIDATION_ERROR, 401: AUTH_ERROR},
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud.get_user_by_id(db, current_user["sub"])
    if not user or not verify_password(body.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Неверный текущий пароль",
                "code": "VALIDATION_ERROR",
                "details": [],
            },
        )
    await crud.update_password(db, user, hash_password(body.new_password))
    return {"message": "Password changed successfully"}


@router.get(
    "/admin/users",
    response_model=list[UserResponse],
    tags=["admin"],
    responses={401: AUTH_ERROR, 403: FORBIDDEN_ERROR},
)
async def list_users(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_all_users(db)


@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["admin"],
    responses={400: VALIDATION_ERROR, 401: AUTH_ERROR, 403: FORBIDDEN_ERROR},
)
async def create_user(
    body: UserCreateRequest,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await crud.get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Пользователь с таким username уже существует",
                "code": "VALIDATION_ERROR",
                "details": [{"field": "username", "msg": "already exists"}],
            },
        )
    return await crud.create_user(
        db,
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
    )