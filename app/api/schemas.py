from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.OPERATOR


class UserResponse(BaseModel):
    id: str
    username: str
    role: UserRole
    createdAt: datetime

    class Config:
        from_attributes = True
