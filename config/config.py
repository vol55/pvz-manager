import os
from pathlib import Path
from zoneinfo import ZoneInfo

from loguru import logger


class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASS = os.getenv("REDIS_PASS", "")
    REDIS_PREFIX = os.getenv("REDIS_PREFIX", "")

    REDIS_KEY_EMPLOYEE_STATISTICS = "employee_statistics"


def setup_logging():
    logger.remove()
    logger.configure(patcher=tz_patcher)
    logger.add(
        str(LOG_DIR / f"{os.getenv('SERVICE_NAME', 'app')}.log"),
        level="ERROR",
        rotation="10 MB",
        retention="60 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {name}:{function}:{line} - {message}",
    )


def tz_patcher(record):
    record["time"] = record["time"].astimezone(TIMEZONE)


settings = Settings()

BASE_DIR = Path(__file__).resolve().parents[1]

SERVICE_ACCOUNT = BASE_DIR / "service-account.json"

TIMEZONE = ZoneInfo("Europe/Moscow")

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
