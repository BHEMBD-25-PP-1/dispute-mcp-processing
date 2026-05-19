from sqlalchemy import select

from app.core.auth import hash_password
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logger import logger
from app.models.user import User


async def seed_operator_user() -> None:
    if not settings.seed_operator_username or not settings.seed_operator_password:
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == settings.seed_operator_username)
        )
        user = result.scalar_one_or_none()
        password_hash = hash_password(settings.seed_operator_password)

        if user:
            user.password_hash = password_hash
            user.role = "OPERATOR"
            logger.info("Seed operator updated: username=%s", user.username)
        else:
            db.add(
                User(
                    username=settings.seed_operator_username,
                    password_hash=password_hash,
                    role="OPERATOR",
                )
            )
            logger.info("Seed operator created: username=%s", settings.seed_operator_username)

        await db.commit()
