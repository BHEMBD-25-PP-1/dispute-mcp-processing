from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    role: UserRole
    createdAt: datetime


class DisputeProcessRequest(BaseModel):
    text: str


class DisputeProcessResponse(BaseModel):
    dispute_id: str | None = None
    idempotency_key: str | None = None
    replayed: bool = False
    version: int | None = None
    assigned_to: str | None = None
    locked_until: datetime | None = None
    status: str
    parsed: dict[str, Any]
    nlu: dict[str, Any]
    mcp: dict[str, Any]
    result: str


class DisputeClaimRequest(BaseModel):
    expected_version: int
    lock_minutes: int = 15


class DisputeStatusUpdateRequest(BaseModel):
    status: str
    expected_version: int


class DisputeStateResponse(BaseModel):
    dispute_id: str
    status: str
    version: int
    assigned_to: str | None = None
    locked_until: datetime | None = None


class CaseActionRequest(BaseModel):
    message: str


class CaseResultUpdateRequest(BaseModel):
    result: str
