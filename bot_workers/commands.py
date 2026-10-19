import asyncio
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from loguru import logger

from bot_workers.filters import is_in_group, is_in_private_chat
from bot_workers.states import LateReport
from bot_workers.utils import on_message_error
from sheets.bootstrap import PAYOUTS_SHEET_MANAGER, ALERTS_SHEET_MANAGER, FINES_SHEET_MANAGER


def commands_router_setup():
    router = Router()
    payouts_sheet = PAYOUTS_SHEET_MANAGER
    alerts_sheet = ALERTS_SHEET_MANAGER
    fines_sheet = FINES_SHEET_MANAGER
    webapp_url = f'{os.getenv("MINI_APP_URL")}/{os.getenv("MINI_APP_PREFIX")}'

    @router.message(Command("start"), is_in_group, is_in_private_chat)
    async def start_command(message: Message, state: FSMContext):
        """
        Очищает текущее состояние пользователя и предлагает
        открыть мини-приложение для заполнения профиля.
        """
        try:
            await state.clear()

            inline_keyboard = [
                [InlineKeyboardButton(text="Заполнить профиль 🚀",
                                      web_app=WebAppInfo(url=f'{webapp_url}/edit-profile'))],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )

            await message.answer(
                "Привет 👋\n"
                "Чтобы начать работу, пожалуйста, откройте мини-приложение и заполните данные профиля.\n\n"
                "Нажмите кнопку ниже",
                reply_markup=keyboard,
            )
        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("profile"), is_in_group, is_in_private_chat)
    async def profile_command(message: Message, state: FSMContext):
        """
        Предлагает пользователю открыть мини-приложение
        для просмотра или обновления профиля.
        """
        try:
            await state.clear()

            inline_keyboard = [
                [InlineKeyboardButton(text="Перейти в приложение 🚀",
                                      web_app=WebAppInfo(url=f'{webapp_url}/edit-profile'))],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )

            await message.answer("Откройте мини-приложение, чтобы посмотреть или обновить данные",
                                 reply_markup=keyboard,
                                 )
        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("rating"), is_in_group, is_in_private_chat)
    async def rating_command(message: Message, state: FSMContext):
        """
        Предлагает пользователю перейти в раздел рейтинга сотрудников
        внутри мини-приложения.
        """
        try:
            await state.clear()

            inline_keyboard = [
                [InlineKeyboardButton(text="Перейти в приложение 🚀", web_app=WebAppInfo(url=f'{webapp_url}/rating'))],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )

            await message.answer("Откройте мини-приложение, чтобы посмотреть рейтинг сотрудников",
                                 reply_markup=keyboard,
                                 )
        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("check"), is_in_group, is_in_private_chat)
    async def check_command(message: Message, state: FSMContext):
        """
        Получает названия доступных периодов выплат
        и предлагает пользователю выбрать нужный период.
        """
        try:
            await state.clear()
            previous, current = await payouts_sheet.get_date_ranges()

            inline_keyboard = [
                [InlineKeyboardButton(text=previous, callback_data=f"date_previous")],
                [InlineKeyboardButton(text=current, callback_data=f"date_current")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )
            await message.answer("Какой промежуток времени", reply_markup=keyboard)

        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("alerts"), is_in_group, is_in_private_chat)
    async def alerts_command(message: Message, state: FSMContext):
        """
        Получает отчёт о пропущенных отметках и отправляет его пользователю.
        Разбивает отчёт на несколько сообщений.
        """
        try:
            await state.clear()
            report = await alerts_sheet.get_missing_alerts()
            if not report or not report.strip():
                await message.answer("✅ Пропущенных отметок нет.")
                return

            max_len = 3500
            blocks = [b.strip() for b in report.split("\n\n") if b.strip()]
            parts: list[str] = []
            buf = ""

            for b in blocks:
                chunk = b + "\n\n"

                if len(chunk) > max_len:
                    if buf:
                        parts.append(buf.rstrip())
                        buf = ""
                    s = b
                    while s:
                        parts.append(s[:max_len])
                        s = s[max_len:]
                    continue

                if buf and (len(buf) + len(chunk) > max_len):
                    parts.append(buf.rstrip())
                    buf = chunk
                else:
                    buf += chunk

            if buf:
                parts.append(buf.rstrip())

            total = len(parts)
            for i, part in enumerate(parts, start=1):
                prefix = f"⚠️ Сообщение {i} из {total}\n\n" if total > 1 else ""
                await message.answer(prefix + part)
                await asyncio.sleep(1)

        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("fines"), is_in_group, is_in_private_chat)
    async def fines_command(message: Message, state: FSMContext):
        """
        Получает названия предыдущего и текущего периодов штрафов
        и предлагает пользователю выбрать нужный период.
        """
        try:
            await state.clear()
            previous, current = await fines_sheet.get_date_ranges()

            inline_keyboard = [
                [InlineKeyboardButton(text=previous, callback_data=f"fines_previous")],
                [InlineKeyboardButton(text=current, callback_data=f"fines_current")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )
            await message.answer("Какой промежуток времени", reply_markup=keyboard)

        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    @router.message(Command("late"), is_in_group, is_in_private_chat)
    async def late_command(message: Message, state: FSMContext):
        """
        Переводит пользователя в состояние ввода комментария
        для ответственного сотрудника.
        """
        try:
            await state.clear()

            inline_keyboard = [
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )

            await state.set_state(LateReport.comment)
            await message.answer("Напишите комментарий для ответственного", reply_markup=keyboard)

        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    return router
