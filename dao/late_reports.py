from datetime import datetime

from sqlalchemy import select, update

from db.db import SessionLocal
from db.models import LateReport


class LateReportsDAO:
    # Таблица отчётов об опозданиях
    model = LateReport

    @classmethod
    async def save(
            cls,
            telegram_id: int,
            comment: str,
            occurred_at: datetime,
            uploaded: bool = False,
    ) -> None:
        async with SessionLocal() as session:
            report = cls.model(
                telegram_id=telegram_id,
                comment=comment,
                occurred_at=occurred_at,
                uploaded=uploaded,
            )
            session.add(report)
            await session.commit()

    @classmethod
    async def get_one_unuploaded(cls) -> LateReport | None:
        # Получаем первый необработанный отчёт по возрастанию ID
        async with SessionLocal() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.uploaded == False)
                .order_by(cls.model.id.asc())
                .limit(1)
            )
            return result.scalars().first()

    @classmethod
    async def mark_report_uploaded(cls, report_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                update(cls.model)
                .where(cls.model.id == report_id)
                .values(uploaded=True)
            )
            await session.commit()
