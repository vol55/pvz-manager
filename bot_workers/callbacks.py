from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from bot_workers.utils import on_callback_error
from sheets.bootstrap import PAYOUTS_SHEET_MANAGER, FINES_SHEET_MANAGER


def callbacks_router_setup():
    router = Router()
    payouts_sheet = PAYOUTS_SHEET_MANAGER
    fines_sheet = FINES_SHEET_MANAGER

    @router.callback_query(F.data == "cancel")
    async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
        """
        Обрабатывает нажатие кнопки отмена
        Удаляет сообщение и очищает стейт бота
        """

        await state.clear()
        await callback.message.delete()

    @router.callback_query(F.data.startswith("date_"))
    async def handle_payroll_callback(callback: CallbackQuery, state: FSMContext):
        """
        Обрабатывает нажатие кнопок выбора периода выплат.
        Отправляет пользователю сообщение с результатом
        """
        try:
            previous, current = await payouts_sheet.get_date_ranges()
            if callback.data == "date_previous":
                text = await payouts_sheet.get_previous_payroll(callback.from_user.id)
                callback_text = previous
            else:
                text = await payouts_sheet.get_current_payroll(callback.from_user.id)
                callback_text = current

            if not text:
                text = "Пока нет данных 🥺"

            await callback.message.edit_text(f"{callback.message.text}\n\n✅ {callback_text}")
            await state.clear()
            await callback.message.answer(text)
        except Exception as e:
            await on_callback_error(callback.message, state)
            logger.exception(e)

    @router.callback_query(F.data.startswith("fines_"))
    async def handle_fines_callback(callback: CallbackQuery, state: FSMContext):
        """
        Обрабатывает нажатие кнопок выбора периода штрафов.
        Отправляет пользователю сообщение с результатом
        """
        try:
            previous, current = await fines_sheet.get_date_ranges()
            if callback.data == "fines_previous":
                text = await fines_sheet.get_previous_fines(callback.from_user.id)
                callback_text = previous
            else:
                text = await fines_sheet.get_current_fines(callback.from_user.id)
                callback_text = current

            if not text:
                text = "Пока нет данных 🥺"

            await callback.message.edit_text(f"{callback.message.text}\n\n✅ {callback_text}")
            await state.clear()
            await callback.message.answer(text)
        except Exception as e:
            await on_callback_error(callback.message, state)
            logger.exception(e)

    return router
