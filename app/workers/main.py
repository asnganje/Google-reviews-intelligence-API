import logging

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)

QUEUE_NAME = "arq:queue"
# arq refreshes this key every health-check interval; the API's health
# endpoint treats its presence as proof that at least one worker is alive.
WORKER_HEALTH_KEY = f"{QUEUE_NAME}:health-check"


async def ping(ctx: dict) -> str:
    """Smoke-test job used to verify the queue end to end."""
    return "pong"


async def startup(ctx: dict) -> None:
    configure_logging(settings.log_level)
    logger.info("worker started", extra={"env": settings.app_env})


async def shutdown(ctx: dict) -> None:
    logger.info("worker stopped")


class WorkerSettings:
    """Run with: arq app.workers.main.WorkerSettings"""

    functions = [ping]
    queue_name = QUEUE_NAME
    health_check_key = WORKER_HEALTH_KEY
    health_check_interval = 30
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
