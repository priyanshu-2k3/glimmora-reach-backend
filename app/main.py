"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, connect_db, get_database
from app.api.v1.router import api_router
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.repositories.google_ads_connection import GoogleAdsConnectionRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    db = await get_database()
    await UserRepository(db).create_indexes()
    await OrganizationRepository(db).create_indexes()
    await InvitationRepository(db).create_indexes()
    await GoogleAdsConnectionRepository(db).create_indexes()
    yield
    await close_db()


app = FastAPI(
    title="Glimmora Reach API",
    description="Campaign Engine — Auth & API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

_origins = settings.cors_origins_list or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
