from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.models.dispute import Dispute  # noqa: F401
from app.models.dispute_event import DisputeEvent  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.bootstrap import seed_operator_user
from app.services.event_publisher import close_kafka_producer


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await seed_operator_user()
    yield
    await close_kafka_producer()


app = FastAPI(title="Dispute Processing API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)