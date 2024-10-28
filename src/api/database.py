from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.api.settings import DATABASE_URL, DATABASE_ECHO


class BaseModel(DeclarativeBase):

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


async_engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
