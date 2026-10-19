import asyncio

from loguru import logger

from sheets.bootstrap import (
    PAYOUTS_SHEET_MANAGER,
    ALERTS_SHEET_MANAGER,
    FINES_SHEET_MANAGER
)


async def get_sheet_values():
    sheets = [
        PAYOUTS_SHEET_MANAGER,
        ALERTS_SHEET_MANAGER,
        FINES_SHEET_MANAGER
    ]

    while True:
        try:
            for sheet in sheets:
                await sheet.get_sheet_values()
                await asyncio.sleep(5)
            await asyncio.sleep(45)

        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(600)
