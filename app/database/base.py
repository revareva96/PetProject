from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.config.config import Settings, get_settings

settings: Settings = get_settings()
db = settings.db
db_user = settings.db_user
db_password = settings.db_password
db_host = settings.db_host
db_port = settings.db_port

DATABASE_URL = f'postgresql+asyncpg://' \
               f'{db_user}:' \
               f'{db_password}' \
               f'@{db_host}:' \
               f'{db_port}/' \
               f'{db}'

engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()


class AsyncSession(_AsyncSession):
    instance = None

    def __new__(cls, *args, **kwargs) -> 'AsyncSession':  # type: ignore
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance


async def get_session() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False, autocommit=False) as session:
        return session
