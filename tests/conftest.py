import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.api.database import BaseModel, get_session
from main import app

DATABASE_TEST_URL = "postgresql+asyncpg://user:password@localhost/test_db"  # Измените параметры на свои

test_engine = create_async_engine(DATABASE_TEST_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)  # Создаём таблицы
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)  # Удаляем таблицы


@pytest.fixture(scope="function")
async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
