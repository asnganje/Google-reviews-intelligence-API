import logging

from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.database.session import engine
from app.schemas.health import HealthResponse
from app.workers.main import WORKER_HEALTH_KEY

logger = logging.getLogger(__name__)

_REDIS_TIMEOUT_SECONDS = 2


def _redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=_REDIS_TIMEOUT_SECONDS,
        socket_timeout=_REDIS_TIMEOUT_SECONDS,
    )


def check_database() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        # Only the error type is exposed: the message may contain the DSN.
        logger.warning("database health check failed", exc_info=exc)
        return f"error: {type(exc).__name__}"


def check_redis() -> str:
    try:
        _redis_client().ping()
        return "ok"
    except Exception as exc:
        logger.warning("redis health check failed", exc_info=exc)
        return f"error: {type(exc).__name__}"


def check_workers() -> str:
    """A worker is alive if arq has refreshed its health key recently."""
    try:
        if _redis_client().exists(WORKER_HEALTH_KEY):
            return "ok"
        return "unavailable"
    except Exception as exc:
        logger.warning("worker health check failed", exc_info=exc)
        return f"error: {type(exc).__name__}"


def get_health() -> HealthResponse:
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "workers": check_workers(),
    }
    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return HealthResponse(
        status=status,
        version=settings.app_version,
        checks=checks,
    )
