import asyncio
import signal

from config.config import setup_logging
from redis_dao.manager import redis_manager
from tasks.cache_sheet_values import cache_sheet_values
from tasks.upload_late_reports import upload_late_reports
from tasks.upload_profiles import upload_profiles


def cancel_all(tasks: list[asyncio.Task]) -> None:
    for task in tasks:
        task.cancel()


async def main() -> None:
    await redis_manager.connect()
    tasks: list[asyncio.Task] = []

    try:
        tasks = [
            asyncio.create_task(upload_late_reports(), name="upload_late_reports"),
            asyncio.create_task(upload_profiles(), name="upload_profiles"),
            asyncio.create_task(cache_sheet_values(), name="cache_sheet_values"),
        ]

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, cancel_all, tasks)

        await asyncio.gather(*tasks, return_exceptions=True)

    finally:
        cancel_all(tasks)
        await redis_manager.close()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
