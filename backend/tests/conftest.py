"""Shared pytest fixtures for ILMA backend tests."""
import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Use SQLite in-memory for tests — register JSONB as JSON for SQLite compat
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models.profile import Profile
from app.models.user import User, UserRole

_orig_process = SQLiteTypeCompiler.process

def _patched_process(self, type_, **kw):
    if isinstance(type_, JSONB):
        from sqlalchemy import JSON
        return _orig_process(self, JSON(), **kw)
    return _orig_process(self, type_, **kw)

SQLiteTypeCompiler.process = _patched_process  # type: ignore

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    """Function-scoped engine: fresh DB per test."""
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_student(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="student@test.com",
        full_name="Test Student",
        hashed_password=get_password_hash("Test1234!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_parent(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="parent@test.com",
        full_name="Test Parent",
        hashed_password=get_password_hash("Test1234!"),
        role=UserRole.PARENT,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        full_name="Test Admin",
        hashed_password=get_password_hash("Test1234!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_student_profile(db_session: AsyncSession, test_student: User) -> Profile:
    """Create a Profile for the test student (auto-select since it's the only one)."""
    profile = Profile(
        id=uuid.uuid4(),
        user_id=test_student.id,
        display_name=test_student.full_name,
        is_active=True,
    )
    db_session.add(profile)
    await db_session.flush()
    return profile


@pytest_asyncio.fixture
async def test_parent_profiles(db_session: AsyncSession, test_parent: User) -> list[Profile]:
    """Create two child profiles under the test parent."""
    p1 = Profile(
        id=uuid.uuid4(),
        user_id=test_parent.id,
        display_name="Aïcha",
        is_active=True,
    )
    p2 = Profile(
        id=uuid.uuid4(),
        user_id=test_parent.id,
        display_name="Kofi",
        is_active=True,
    )
    db_session.add_all([p1, p2])
    await db_session.flush()
    return [p1, p2]


def auth_header(user: User, profile: Profile | None = None) -> dict:
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    if profile:
        headers["X-Profile-Id"] = str(profile.id)
    return headers
