from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import AUTH_ERROR, VALIDATION_ERROR
from app.api.schemas import ChangePasswordRequest, LoginRequest, LoginResponse
from app.core.auth import create_access_token, get_current_user, hash_password, verify_password
from app.core.database import get_db
from app.services import users


router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: AUTH_ERROR},
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await users.get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid credentials", "code": "AUTH_ERROR"},
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return LoginResponse(access_token=token, token_type="bearer")


@router.patch(
    "/change-password",
    responses={400: VALIDATION_ERROR, 401: AUTH_ERROR},
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users.get_user_by_id(db, current_user["sub"])
    if not user or not verify_password(body.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Неверный текущий пароль",
                "code": "VALIDATION_ERROR",
                "details": [],
            },
        )
    await users.update_password(db, user, hash_password(body.new_password))
    return {"message": "Password changed successfully"}
