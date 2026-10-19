from loguru import logger

from sheets.sheet_manager import SheetManager


class PayoutsSheetManager(SheetManager):
    """
    Название таблицы: Управление ПВЗ 2.0
    Название листа: -- детализация зп (бот)
    """

    def __init__(self, spreadsheet_id, worksheet_id, time_to_live=900):
        super().__init__(spreadsheet_id, worksheet_id, time_to_live)

    async def get_date_ranges(self):
        try:
            await self.get_sheet_values()
        except Exception as e:
            logger.exception(e)

        return f"{self._cached_values[0][0]}: {self._cached_values[0][1]}", f"{self._cached_values[0][2]}: {self._cached_values[0][3]}"

    async def get_previous_payroll(self, uid):
        try:
            await self.get_sheet_values()
        except Exception as e:
            logger.exception(e)

        uid_str = str(uid)

        row_index = None
        for i, row in enumerate(self._cached_values):
            if row[0] == uid_str:
                row_index = i
                break

        return self._cached_values[row_index][1] if row_index else None

    async def get_current_payroll(self, uid):
        try:
            await self.get_sheet_values()
        except Exception as e:
            logger.exception(e)

        uid_str = str(uid)

        row_index = None
        for i, row in enumerate(self._cached_values):
            if row[2] == uid_str:
                row_index = i
                break

        return self._cached_values[row_index][3] if row_index else None
