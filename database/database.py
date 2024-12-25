from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from models.models import Base

engine = create_async_engine("postgresql+asyncpg://postgres:1111@localhost:5432/hhru", echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

