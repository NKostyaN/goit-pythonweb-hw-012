import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Клас для управління асинхронними сесіями бази даних.

    Цей клас створює асинхронний двигун і фабрику сесій для роботи з базою даних.

    Атрибути:
    - _engine: Асинхронний двигун для підключення до бази даних.
    - _session_maker: Фабрика для створення сесій.

    Методи:
    - session: Контекстний менеджер для роботи з сесією бази даних.
    """

    def __init__(self, url: str):
        """
        Ініціалізує двигун і фабрику сесій для бази даних.

        Параметри:
        - url: URL для підключення до бази даних.
        """

        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Контекстний менеджер для створення і управління сесією бази даних.

        Піднімає:
        - Exception: Якщо фабрика сесій не ініціалізована.
        - SQLAlchemyError: У разі виникнення помилок під час роботи із сесією.
        """

        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Генератор для отримання сесії бази даних у залежностях FastAPI.
    """

    async with sessionmanager.session() as session:
        yield session
