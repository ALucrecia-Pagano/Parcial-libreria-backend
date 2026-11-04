"""Motor asincrónico + fábrica de sesiones (SQLModel + SQLAlchemy + asyncpg).

Los recursos se crean en el lifespan de la aplicación (``app/main.py``) y se
guardan en ``app.state``: nada se crea al importar el módulo. El motor se
cierra al apagar el servidor. ``get_session`` entrega una sesión por petición,
tomada de la fábrica de ``app.state``; la fábrica usa ``expire_on_commit=False``.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, settings


def crear_motor(config: Settings = settings) -> AsyncEngine:
    """Crea el motor. No conecta: la conexión se abre al primer uso."""
    return create_async_engine(
        config.DATABASE_URL,
        pool_size=config.DB_POOL_SIZE,
        echo=config.SQL_ECHO,
    )


def crear_fabrica(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Crea la fábrica de sesiones (``expire_on_commit=False``)."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def init_resources() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Crea motor y fábrica (llamado desde el lifespan)."""
    engine = crear_motor()
    return engine, crear_fabrica(engine)


async def dispose_resources(engine: AsyncEngine) -> None:
    """Cierra el motor (llamado al apagar la aplicación)."""
    await engine.dispose()


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI: una sesión por petición, siempre cerrada."""
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with fabrica() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
