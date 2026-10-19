import os

from sheets.alerts import AlertSheetManager
from sheets.employee_statistics import EmployeeStatistics
from sheets.fines import FinesSheetManager
from sheets.payouts import PayoutsSheetManager

PAYOUTS_SHEET_MANAGER = PayoutsSheetManager(
    os.getenv("SPREADSHEET_ID_MANAGEMENT"),
    os.getenv("SHEET_ID_PAYOUTS"),
    900
)

ALERTS_SHEET_MANAGER = AlertSheetManager(
    os.getenv("SPREADSHEET_ID_MANAGEMENT"),
    os.getenv("SHEET_ID_ALERTS"),
    900
)

FINES_SHEET_MANAGER = FinesSheetManager(
    os.getenv("SPREADSHEET_ID_MANAGEMENT"),
    os.getenv("SHEET_ID_FINES"),
    900
)

EMPLOYEE_STATISTICS = EmployeeStatistics(
    os.getenv("SPREADSHEET_ID_MANAGEMENT"),
    os.getenv("SHEET_ID_EMPLOYEES_RATING"),
    900
)
