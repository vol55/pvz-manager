from sqlalchemy import select

from db.db import SessionLocal
from db.models import LateReport


def get_late_report():
    """
    Возвращает все отчёты об опозданиях из базы данных
    """
    with SessionLocal() as db:
        return db.execute(select(LateReport)).scalars().all()
