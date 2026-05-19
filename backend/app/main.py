from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.core.database import engine
from app.models.base import Base
from app.models.dispute import Dispute  # noqa: F401
from app.models.dispute_event import DisputeEvent  # noqa: F401
from app.models.user import User  # noqa: F401


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title="Dispute Processing API", lifespan=lifespan)

app.include_router(router)