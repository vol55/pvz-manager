import asyncio
import os
from datetime import datetime

from loguru import logger

from config.config import TIMEZONE
from sheets.bootstrap import ALERTS_SHEET_MANAGER

TELEGRAM_GROUP = os.getenv("WORKERS_GROUP")


async def monitor_alerts(bot):
    sheet = ALERTS_SHEET_MANAGER

    try:
        alerts = await sheet.get_alert_times()
    except Exception:
        alerts = []

    while True:
        try:
            await asyncio.sleep(10)
            now = get_time_in_minutes()
            while now > 420:  # 7 утра
                if not alerts:
                    await asyncio.sleep(2400)
                    alerts = await sheet.get_alert_times()
                    break
                now = get_time_in_minutes()
                if now in alerts:
                    alert_time = f"{now // 60}:{now % 60:02d}"
                    await send_alerts(bot, alert_time)
                    alerts = await sheet.get_alert_times()
                    break
                await asyncio.sleep(10)
        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(300)


def get_time_in_minutes():
    current_time = datetime.now(TIMEZONE)
    return (current_time.hour * 60) + current_time.minute


async def send_alerts(bot, alert_time):
    sheet = ALERTS_SHEET_MANAGER
    alerts = await sheet.get_alerts_by_time(alert_time)

    for alert in alerts["Сообщения в общий чат"]:
        try:
            await bot.send_message(
                chat_id=TELEGRAM_GROUP,
                text=alert
            )
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(1)

    for alert in alerts["Сообщения сотрудникам"]:
        try:
            await bot.send_message(chat_id=alert["user_id"], text=alert["text"])
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(1)
