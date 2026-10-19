import asyncio
import os

from loguru import logger

from dao.late_reports import LateReportsDAO
from sheets.late_reports import LateReportsSheet


async def upload_late_reports() -> None:
    sheet = LateReportsSheet(
        os.getenv("SPREADSHEET_ID_MANAGEMENT"),
        os.getenv("SHEET_ID_LATE_COMMENTS"),
    )
    dao = LateReportsDAO

    while True:
        try:
            await asyncio.sleep(15)

            report = await dao.get_one_unuploaded()
            if not report:
                continue

            uploaded = await asyncio.to_thread(sheet.upload_report, report)

            if uploaded:
                await dao.mark_report_uploaded(report.id)

        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(120)
