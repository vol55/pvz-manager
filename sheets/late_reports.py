from config.config import TIMEZONE
from db.models import LateReport
from sheets.gspread_client import client
from sheets.utils import sanitize_cell


class LateReportsSheet:
    """
    Название таблицы: Управление ПВЗ 2.0
    Название листа: -- комментарии к опозданию (бот)
    """

    def __init__(self, spreadsheet_id, worksheet_id):
        self._spreadsheet_id = spreadsheet_id
        self._worksheet_id = worksheet_id
        self._client = client

    def upload_report(self, report: LateReport) -> bool:
        sheet = self._client.open_by_key(self._spreadsheet_id).get_worksheet_by_id(self._worksheet_id)
        row = [
            str(report.telegram_id),
            sanitize_cell(report.comment),
            report.occurred_at.astimezone(TIMEZONE).strftime("%d.%m.%Y"),
            report.occurred_at.astimezone(TIMEZONE).strftime("%H:%M:%S")
        ]
        sheet.append_row(
            row,
            value_input_option="USER_ENTERED",
            insert_data_option="INSERT_ROWS",
        )
        return True
