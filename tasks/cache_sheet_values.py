import asyncio

from loguru import logger

from sheets.bootstrap import EMPLOYEE_STATISTICS


async def cache_sheet_values():
    sheets = [
        EMPLOYEE_STATISTICS,
    ]

    while True:
        try:
            for sheet in sheets:
                await sheet.save_to_redis()
                await asyncio.sleep(5)
            await asyncio.sleep(45)

        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(600)
