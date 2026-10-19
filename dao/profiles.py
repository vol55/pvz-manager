from datetime import datetime
from typing import Optional

from sqlalchemy import select, update

from db.db import SessionLocal
from db.models import Profile


class ProfilesDAO:
    # Таблица профилей сотрудников
    model = Profile

    @classmethod
    async def get(cls, telegram_id: int) -> Profile | None:
        async with SessionLocal() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.telegram_id == telegram_id)
                .limit(1)
            )
            return result.scalars().first()

    @classmethod
    async def save(
            cls,
            telegram_id: int,
            last_name: str,
            first_name: str,
            position: str,
            phone: str,
            pvz: str,
            payment_method: str = "",
            salary_card: str = "",
            salary_phone: str = "",
            recipient: str = "",
            bank: str = "",
            left_at: Optional[datetime] = None,
            active: bool = True,
            uploaded: bool = False,
    ) -> None:
        async with SessionLocal() as session:
            profile = cls.model(
                telegram_id=telegram_id,
                last_name=last_name,
                first_name=first_name,
                position=position,
                phone=phone,
                pvz=pvz,
                payment_method=payment_method,
                salary_card=salary_card,
                salary_phone=salary_phone,
                recipient=recipient,
                bank=bank,
                left_at=left_at,
                active=active,
                uploaded=uploaded,
            )
            session.add(profile)
            await session.commit()

    @classmethod
    async def update(cls, telegram_id: int, **fields) -> None:
        allowed = {
            "last_name", "first_name", "position", "phone", "pvz", "payment_method",
            "salary_card", "salary_phone", "recipient", "bank", "left_at", "active", "uploaded",
        }
        fields = {k: v for k, v in fields.items() if k in allowed}
        if not fields:
            return

        async with SessionLocal() as session:
            await session.execute(
                update(cls.model)
                .where(cls.model.telegram_id == telegram_id)
                .values(**fields)
                .execution_options(synchronize_session=False)
            )
            await session.commit()

    @classmethod
    async def get_one_unuploaded(cls) -> Profile | None:
        async with SessionLocal() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.uploaded == False)
                .order_by(cls.model.id.asc())
                .limit(1)
            )
            return result.scalars().first()

    @classmethod
    async def mark_uploaded(cls, telegram_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                update(cls.model)
                .where(cls.model.telegram_id == telegram_id)
                .values(uploaded=True)
            )
            await session.commit()
