"""Lógica del módulo generos y traducción de errores de la base."""

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate, GeneroUpdate


async def list_generos(
    session: AsyncSession, limit: int, offset: int
) -> Sequence[Genero]:
    consulta = select(Genero).order_by(Genero.id).limit(limit).offset(offset)
    result = await session.execute(consulta)
    return result.scalars().all()


async def get_genero(session: AsyncSession, genero_id: int) -> Genero:
    genero = await session.get(Genero, genero_id)
    if genero is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Género no encontrado",
        )
    return genero


async def create_genero(session: AsyncSession, data: GeneroCreate) -> Genero:
    genero = Genero.model_validate(data)
    session.add(genero)
    await _guardar(session, "Ya existe un género con ese nombre")
    return genero


async def update_genero(
    session: AsyncSession, genero_id: int, data: GeneroUpdate
) -> Genero:
    genero = await get_genero(session, genero_id)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(genero, campo, valor)
    await _guardar(session, "Ya existe un género con ese nombre")
    return genero


async def delete_genero(session: AsyncSession, genero_id: int) -> None:
    genero = await get_genero(session, genero_id)
    await session.delete(genero)
    await _guardar(
        session, "No se puede borrar el género porque tiene libros asociados"
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