import threading
import time

from sheets.gspread_client import client


class SheetManager:
    def __init__(self, spreadsheet_id, worksheet_id, time_to_live, redis_key=None):
        self._spreadsheet_id = spreadsheet_id
        self._worksheet_id = worksheet_id
        self._client = client

        self._cache_timestamp = 0.0
        self._time_to_live = time_to_live

        self._sheet_lock = threading.Lock()
        self._cached_values = []

        self.redis_key = redis_key
        self._redis_timestamp = 0.0

    async def get_sheet_values(self):
        if self._cached_values:
            if time.time() - self._cache_timestamp > self._time_to_live:
                await self._refresh_cache()
        else:
            await self._refresh_cache()

    async def _refresh_cache(self):
        with self._sheet_lock:
            if time.time() - self._cache_timestamp < self._time_to_live:
                return
            sheet = self._client.open_by_key(self._spreadsheet_id).get_worksheet_by_id(self._worksheet_id)
            self._cached_values = sheet.get_all_values()
            self._cache_timestamp = time.time()

    async def save_to_redis(self):
        pass
