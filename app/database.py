
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.config import DATABASE_URL

# pool_recycle stays under MySQL's default wait_timeout so idle connections aren't dropped.
engine = create_async_engine(
    DATABASE_URL, connect_args={"charset": "utf8mb4"}, pool_pre_ping=True, pool_recycle=3600
)
# expire_on_commit=False: async sessions can't lazy-load attributes after a commit.
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        yield db
