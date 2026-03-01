import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy import delete

from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.models.book import Book


TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(test_engine):
    SessionLocal = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with SessionLocal() as s:
        # ✅ очищаємо таблицю перед кожним тестом
        await s.execute(delete(Book))
        await s.commit()
        yield s


@pytest.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()