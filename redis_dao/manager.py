from config.config import settings
from redis_dao.custom_redis import CustomRedis
from redis_dao.redis_client import RedisClient

redis_manager = RedisClient(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASS,
)


async def get_redis() -> CustomRedis:
    return redis_manager.get_client()
