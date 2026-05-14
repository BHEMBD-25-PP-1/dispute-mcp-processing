from fastapi import FastAPI

from app.api.routes import router
from app.core.database import engine
from app.models.base import Base
from app.models.user import User  # noqa: F401


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title="Dispute Processing API")

app.add_event_handler("startup", create_tables)
app.include_router(router)