from aiogram.fsm.state import State, StatesGroup


class LateReport(StatesGroup):
    comment = State()
