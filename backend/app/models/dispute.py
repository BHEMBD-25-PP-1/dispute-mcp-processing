import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    request_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_event_sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="accepted")
    service: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    assigned_to: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    order_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
