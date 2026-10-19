from typing import Optional

from redis_dao.custom_redis import CustomRedis


class RedisClient:

    def __init__(
            self,
            host: str,
            port: int,
            db: int,
            password: str | None = None,
            user: str = "default",
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.user = user
        self._client: Optional[CustomRedis] = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = CustomRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password or None,
                username=self.user,
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self._client.ping()

    def get_client(self) -> CustomRedis:
        if self._client is None:
            raise RuntimeError("Redis client is not initialized. Call connect() first.")
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
