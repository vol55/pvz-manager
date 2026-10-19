from datetime import datetime

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from bot_workers.filters import is_in_group, is_in_private_chat
from bot_workers.states import LateReport
from bot_workers.utils import on_message_error, safe_remove_markup
from dao.late_reports import LateReportsDAO


def messages_router_setup():
    router = Router()

    @router.message(is_in_group, is_in_private_chat, StateFilter(LateReport.comment))
    async def handle_late_comment_message(message: Message, state: FSMContext):
        """
        Обрабатывает комментарий об опоздании.
        """
        try:
            await safe_remove_markup(message.bot, message.chat.id, message.message_id - 1)
            comment = message.text
            if not comment:
                inline_keyboard = [
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
                ]
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=inline_keyboard
                )
                await message.answer("Пожалуйста, отправьте текстовый комментарий.", reply_markup=keyboard)
                return

            if len(comment) > 3800:
                inline_keyboard = [
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
                ]
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=inline_keyboard
                )
                await message.answer(
                    "Комментарий не проходит по лимиту. Напишите, пожалуйста, покороче",
                    reply_markup=keyboard
                )
                return

            await state.clear()
            await LateReportsDAO.save(
                telegram_id=message.from_user.id,
                comment=comment,
                occurred_at=datetime.now(),
            )
            await message.react([ReactionTypeEmoji(emoji="👍")])
            await message.answer("Комментарий отправлен")
        except Exception as e:
            await on_message_error(message, state)
            logger.exception(e)

    return router
