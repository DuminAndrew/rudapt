from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_keys as api_keys_router
from app.api import auth as auth_router
from app.api import reports as reports_router
from app.api import startups as startups_router
from app.api import v1 as v1_router
from app.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="RuDapt API",
        version="0.1.0",
        description="Startup Localization AI — генерация бизнес-планов локализации стартапов в РФ.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router.router)
    app.include_router(startups_router.router)
    app.include_router(reports_router.router)
    app.include_router(api_keys_router.router)
    app.include_router(v1_router.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
