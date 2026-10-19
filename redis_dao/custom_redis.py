import json
from typing import Any

from redis.asyncio import Redis


class CustomRedis(Redis):
    async def save_json(self, key: str, value: dict | list) -> bool:
        return bool(
            await self.set(
                key,
                json.dumps(value, ensure_ascii=False),
            )
        )

    async def get_json(self, key: str) -> Any | None:
        value = await self.get(key)
        if value is None:
            return None
        return json.loads(value)
