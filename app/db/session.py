from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.settings import settings


engine = create_async_engine(settings.database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
