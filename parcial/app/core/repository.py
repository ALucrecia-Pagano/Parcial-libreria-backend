"""Clases base de los repositorios: acceso a datos sin confirmar transacciones.

Hay dos jerarquías porque un único genérico que filtrara borrado_en daría error
de SQL sobre las tablas que no tienen esa columna.

Ningún repositorio hace commit: add, update, delete y soft_delete solo hacen
flush(). Confirmar o revertir es tarea del UnitOfWork.

Estas clases no reciben `where` ni `options`: cada repositorio hijo declara sus
métodos con nombre propio, con la precarga adentro (D7, consigna pág. 12).
"""
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        # El genérico T no existe en ejecución: la clase se pasa como dato.
        self.model = model

    async def get_by_id(self, entity_id: int) -> T | None:
        return await self.session.get(self.model, entity_id)

    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:
        consulta = (
            select(self.model).order_by(self.model.id).offset(offset).limit(limit)
        )
        return (await self.session.scalars(consulta)).all()

    async def count(self) -> int:
        consulta = select(func.count()).select_from(self.model)
        return await self.session.scalar(consulta)

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T, cambios: dict[str, Any] | None = None) -> T:
        if cambios is not None:
            for campo, valor in cambios.items():
                setattr(entity, campo, valor)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()


class SoftDeleteRepository(BaseRepository[T]):
    """Para modelos con columna borrado_en: las lecturas normales ocultan las bajas."""

    async def get_by_id(self, entity_id: int) -> T | None:
        consulta = select(self.model).where(
            self.model.id == entity_id,
            self.model.borrado_en.is_(None),
        )
        return await self.session.scalar(consulta)

    async def get_by_id_including_deleted(self, entity_id: int) -> T | None:
        """Lectura sin filtrar: la usan las lecturas históricas y las validaciones."""
        return await self.session.get(self.model, entity_id)

    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:
        consulta = (
            select(self.model)
            .where(self.model.borrado_en.is_(None))
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.scalars(consulta)).all()

    async def count(self) -> int:
        consulta = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.borrado_en.is_(None))
        )
        return await self.session.scalar(consulta)

    async def soft_delete(self, entity: T) -> T:
        entity.borrado_en = datetime.now(timezone.utc)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
