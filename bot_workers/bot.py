import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_workers.callbacks import callbacks_router_setup
from bot_workers.commands import commands_router_setup
from bot_workers.messages import messages_router_setup
from config.config import setup_logging
from tasks.bot_workers_tasks.get_sheet_values import get_sheet_values
from tasks.bot_workers_tasks.monitor_alerts import monitor_alerts

bot = Bot(token=os.getenv("BOT_WORKERS_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

routers = [
    commands_router_setup(),
    messages_router_setup(),
    callbacks_router_setup(),
]

for router in routers:
    dp.include_router(router)


async def clear_updates():
    """
    Пропуск обработки пропущеннцх сообщений при запуске
    """
    updates = await bot.get_updates(offset=None, timeout=0)
    if updates:
        last_update_id = updates[-1].update_id
        await bot.get_updates(offset=last_update_id + 1, timeout=0)


async def main():
    await clear_updates()
    await dp.start_polling(bot, skip_updates=True)


async def on_startup():
    asyncio.create_task(get_sheet_values())
    asyncio.create_task(monitor_alerts(bot))


if __name__ == "__main__":
    setup_logging()
    dp.startup.register(on_startup)
    asyncio.run(main())
