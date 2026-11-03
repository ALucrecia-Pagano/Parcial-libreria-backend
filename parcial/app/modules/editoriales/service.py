"""Lógica del módulo editoriales y traducción de errores de la base."""

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate


async def list_editoriales(
    session: AsyncSession, limit: int, offset: int
) -> Sequence[Editorial]:
    consulta = select(Editorial).order_by(Editorial.id).limit(limit).offset(offset)
    result = await session.execute(consulta)
    return result.scalars().all()


async def get_editorial(session: AsyncSession, editorial_id: int) -> Editorial:
    editorial = await session.get(Editorial, editorial_id)
    if editorial is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Editorial no encontrada",
        )
    return editorial


async def create_editorial(session: AsyncSession, data: EditorialCreate) -> Editorial:
    editorial = Editorial.model_validate(data)
    session.add(editorial)
    await _guardar(session, "Ya existe una editorial con ese nombre")
    return editorial


async def update_editorial(
    session: AsyncSession, editorial_id: int, data: EditorialUpdate
) -> Editorial:
    editorial = await get_editorial(session, editorial_id)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(editorial, campo, valor)
    await _guardar(session, "Ya existe una editorial con ese nombre")
    return editorial


async def delete_editorial(session: AsyncSession, editorial_id: int) -> None:
    editorial = await get_editorial(session, editorial_id)
    await session.delete(editorial)
    await _guardar(
        session, "No se puede borrar la editorial porque tiene libros asociados"
    )


async def _guardar(session: AsyncSession, mensaje_conflicto: str) -> None:
    """Hace commit; si la base rechaza la escritura, responde 409 con mensaje propio."""
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_conflicto,
        ) from None