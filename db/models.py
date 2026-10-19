from sqlalchemy import BigInteger, DateTime, String, func, Boolean
from sqlalchemy.orm import mapped_column

from db.db import Base


class LateReport(Base):
    __tablename__ = "late_reports"

    id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = mapped_column(BigInteger, nullable=False)
    comment = mapped_column(String(4000))
    occurred_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    uploaded = mapped_column(Boolean, nullable=False, server_default="false")

class Profile(Base):
    __tablename__ = "profiles"

    id = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    telegram_id = mapped_column(BigInteger, nullable=False, unique=True)
    last_name = mapped_column(String(100))
    first_name = mapped_column(String(100))
    position = mapped_column(String(100))
    phone = mapped_column(String(100))
    pvz = mapped_column(String(100))

    payment_method = mapped_column(String(100))
    salary_card = mapped_column(String(100))
    salary_phone = mapped_column(String(100))
    recipient = mapped_column(String(100))
    bank = mapped_column(String(100))

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    left_at = mapped_column(DateTime(timezone=True))

    active = mapped_column(Boolean, nullable=False, server_default="true")
    uploaded = mapped_column(Boolean, nullable=False, server_default="false")
