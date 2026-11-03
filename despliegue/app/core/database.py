"""Motor asincrónico + fábrica de sesiones (SQLModel + SQLAlchemy + asyncpg).

Los recursos se crean en el lifespan de la aplicación (``app/main.py``),
se guardan en ``app.state`` y el motor se cierra al apagar el servidor.
``get_session`` entrega una sesión por petición, creada con
``expire_on_commit=False``.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_resources(database_url: str | None = None) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Crea el motor y la fábrica de sesiones (llamado desde el lifespan)."""
    global engine, async_session_factory
    engine = create_async_engine(
        database_url or settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return engine, async_session_factory


async def dispose_resources() -> None:
    """Cierra el motor (llamado al apagar la aplicación)."""
    global engine, async_session_factory
    if engine is not None:
        await engine.dispose()
    engine = None
    async_session_factory = None


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI: una sesión por petición."""
    if async_session_factory is None:
        init_resources()
    assert async_session_factory is not None
    async with async_session_factory() as session:
        yield session
