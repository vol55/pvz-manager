from gspread import Worksheet

from config.config import TIMEZONE
from db.models import Profile
from sheets.gspread_client import client
from sheets.utils import sanitize_cell


class ProfilesSheet:
    """
    Название таблицы: Управление ПВЗ 2.0
    Название листа: -- сотрудники
    """

    def __init__(self, spreadsheet_id, worksheet_id):
        self._spreadsheet_id = spreadsheet_id
        self._worksheet_id = worksheet_id
        self._client = client

    def upload_profile(self, profile: Profile) -> bool:
        sheet = self._client.open_by_key(self._spreadsheet_id).get_worksheet_by_id(self._worksheet_id)
        row_index = find_row(sheet, profile.telegram_id)
        row = [
            sanitize_cell(f"{profile.last_name} {profile.first_name}"),
            profile.telegram_id,
            profile.position,
            profile.pvz,
            profile.phone,
            profile.payment_method,
            sanitize_cell(profile.salary_card),
            profile.salary_phone,
            sanitize_cell(profile.recipient),
            sanitize_cell(profile.bank),
            profile.created_at.astimezone(TIMEZONE).strftime("%d.%m.%Y"),
        ]
        if row_index:
            sheet.update(
                f"A{row_index}",
                [row],  # update expects a 2D array
                value_input_option="USER_ENTERED",
            )
        else:
            sheet.append_row(
                row,
                value_input_option="USER_ENTERED",
                insert_data_option="INSERT_ROWS",
            )
        return True


def find_row(sheet: Worksheet, telegram_id: int) -> int | None:
    column_b = sheet.col_values(2)

    target = str(telegram_id)
    for row_index, value in enumerate(column_b, start=1):
        if str(value).strip() == target:
            return row_index
    return None
