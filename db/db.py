import os

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


def get_database_url():
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        database=os.getenv("POSTGRES_DB"),
    )


engine = create_async_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False,
)


class Base(DeclarativeBase):
    pass


SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
