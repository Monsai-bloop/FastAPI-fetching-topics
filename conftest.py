from sqlmodel import SQLModel

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession 
from PersonalNews.main import app
from PersonalNews.database.db import get_session
from PersonalNews.cache_data.redis_cache import CacheData


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)

async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def get_database():
	async with engine.begin() as conn:
		await conn.run_sync(SQLModel.metadata.create_all)
	yield 
	async with engine.begin() as conn:
		await conn.run_sync(SQLModel.metadata.drop_all)


async def override_db(): # session use database so we actually override session
	async with async_session() as session:
		yield session 



@pytest_asyncio.fixture
async def client():
	app.dependency_overrides[get_session] = override_db
	async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
		yield c 

	app.dependency_overrides.clear()


