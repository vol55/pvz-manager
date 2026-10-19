from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def on_callback_error(message: Message, state: FSMContext) -> None:
    await message.answer("❌ Произошла ошибка на сервере. Пожалуйста, повторите попытку позже.")
    await message.delete()
    await state.clear()


async def on_message_error(message: Message, state: FSMContext) -> None:
    await message.answer("❌ Произошла ошибка на сервере. Пожалуйста, повторите попытку позже.")
    await state.clear()


async def safe_remove_markup(bot, chat_id: int, message_id: int):
    """
    Удаляет клавиатуру сообщения
    """
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
    except Exception:
        pass
