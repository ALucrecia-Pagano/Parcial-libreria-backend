"""CRUD de autores y traducción de errores de integridad."""
from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorUpdate


async def list_autores(session: AsyncSession, limit: int = 20, offset: int = 0):
    result = await session.execute(select(Autor).order_by(Autor.id).limit(limit).offset(offset))
    return result.scalars().all()


async def get_autor(session: AsyncSession, autor_id: int) -> Autor:
    autor = await session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(404, "Autor no encontrado")
    return autor


async def create_autor(session: AsyncSession, data: AutorCreate) -> Autor:
    autor = Autor.model_validate(data)
    session.add(autor)
    await _guardar(session)
    return autor


async def update_autor(session: AsyncSession, autor: Autor, data: AutorUpdate) -> Autor:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(autor, campo, valor)
    await _guardar(session)
    return autor


async def delete_autor(session: AsyncSession, autor: Autor) -> None:
    # DELETE directo: la FK rechaza autores utilizados sin intentar anular su PK.
    try:
        await session.execute(delete(Autor).where(Autor.id == autor.id))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se puede borrar un autor con libros asociados") from None


async def _guardar(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se pudo guardar el autor: datos en conflicto") from None
