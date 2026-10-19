from datetime import datetime
import time

from config.config import TIMEZONE
from sheets.sheet_manager import SheetManager


class AlertSheetManager(SheetManager):
    """
    Название таблицы: Управление ПВЗ 2.0
    Название листа: -- отметки (бот)
    """

    def __init__(self, spreadsheet_id, worksheet_id, time_to_live=900):
        super().__init__(spreadsheet_id, worksheet_id, time_to_live)

    async def get_alert_times(self):
        # Возвращает список времен отправки уведомлений в минутах
        await self.get_sheet_values()
        if time.time() - self._cache_timestamp > 10:
            sheet = self._client.open_by_key(self._spreadsheet_id).get_worksheet_by_id(self._worksheet_id)
            self._cached_values = sheet.get_all_values()
            self._cache_timestamp = time.time()
        rows = self._cached_values

        alerts = [row[10] for row in rows[2:] if row and row[10]]
        alerts.extend([row[13] for row in rows[2:] if row and row[13]])
        alerts.extend([row[0] for row in rows[2:] if row and row[0]])
        # alerts.extend([row[2] for row in rows[2:] if row and row[2]])

        alerts_minutes = [(int(s.split(':')[0]) * 60) + int(s.split(':')[1]) for s in set(alerts)]

        current_time = datetime.now(TIMEZONE)
        current_minutes = (current_time.hour * 60) + current_time.minute

        return [alert for alert in alerts_minutes if alert > current_minutes]

    async def get_alerts_by_time(self, alert_time):
        # Возвращает сообщения для общего чата и сотрудников на указанное время
        if time.time() - self._cache_timestamp > 10:
            sheet = self._client.open_by_key(self._spreadsheet_id).get_worksheet_by_id(self._worksheet_id)
            self._cached_values = sheet.get_all_values()
            self._cache_timestamp = time.time()
        rows = self._cached_values

        alerts = {
            "Сообщения в общий чат": [],
            "Сообщения сотрудникам": [],
        }

        for row in rows:
            if alert_time in row:
                indexes = [i for i, x in enumerate(row) if i == 0 and x == alert_time]
                for index in indexes:
                    alerts["Сообщения в общий чат"].append(row[index + 1])

                indexes = [i for i, x in enumerate(row) if i in [10, 13] and x == alert_time]
                for index in indexes:
                    alerts["Сообщения сотрудникам"].append({"user_id": int(row[index + 1]), "text": row[index + 2]})

        return alerts

    async def get_missing_alerts(self):
        # Возвращает время пропущенных уведомлений из таблицы
        await self.get_sheet_values()
        rows = self._cached_values
        return rows[2][16]
