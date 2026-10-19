import os
from contextlib import asynccontextmanager
from pathlib import Path

from aiogram import Bot
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from mini_app.routes import router
from redis_dao.manager import redis_manager

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()

    bot = Bot(os.getenv("BOT_WORKERS_TOKEN", ""))
    app.state.bot = bot

    try:
        yield
    finally:
        await bot.session.close()
        await redis_manager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

#  404 для всех необработанных маршрутов
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def block_unused_routes(path: str):
    return Response(status_code=404)
