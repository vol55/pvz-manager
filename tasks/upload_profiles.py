import asyncio
import os

from loguru import logger

from dao.profiles import ProfilesDAO
from sheets.profiles import ProfilesSheet


async def upload_profiles() -> None:
    sheet = ProfilesSheet(
        os.getenv("SPREADSHEET_ID_MANAGEMENT"),
        os.getenv("SHEET_ID_EMPLOYEES"),
    )
    dao = ProfilesDAO

    while True:
        try:
            await asyncio.sleep(45)

            profile = await dao.get_one_unuploaded()
            if not profile:
                continue

            uploaded = await asyncio.to_thread(sheet.upload_profile, profile)

            if uploaded:
                await dao.mark_uploaded(profile.telegram_id)

        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(300)
