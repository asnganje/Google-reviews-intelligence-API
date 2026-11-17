import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    logger.info("application started", extra={"env": settings.app_env})
    yield
    logger.info("application stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "A SerpApi-style platform that returns structured, real-time "
            "data from Google Maps: businesses, place details, and reviews."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "msg": f"{settings.app_name} is running!",
            "docs": "/docs",
        }

    return app


app = create_app()
