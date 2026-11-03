"""Altas atómicas y lecturas con carga anticipada del catálogo."""
from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroUpdate


def _catalogo():
    return select(Libro).options(joinedload(Libro.editorial), joinedload(Libro.genero))


async def list_libros(session: AsyncSession, limit: int = 20, offset: int = 0,
                      titulo: str | None = None, genero_id: int | None = None,
                      editorial_id: int | None = None):
    consulta = _catalogo()
    if titulo is not None:
        consulta = consulta.where(Libro.titulo.icontains(titulo, autoescape=True))
    if genero_id is not None:
        consulta = consulta.where(Libro.genero_id == genero_id)
    if editorial_id is not None:
        consulta = consulta.where(Libro.editorial_id == editorial_id)
    result = await session.execute(consulta.order_by(Libro.id).limit(limit).offset(offset))
    return result.scalars().all()


async def get_libro(session: AsyncSession, libro_id: int) -> Libro:
    consulta = _catalogo().where(Libro.id == libro_id).options(
        selectinload(Libro.autorias).joinedload(LibroAutor.autor)
    ).execution_options(populate_existing=True)
    result = await session.execute(consulta)
    libro = result.scalars().first()
    if libro is None:
        raise HTTPException(404, "Libro no encontrado")
    libro.autorias.sort(key=lambda autoria: (autoria.orden, autoria.autor_id))
    return libro


async def create_libro(session: AsyncSession, data: LibroCreate) -> Libro:
    libro = Libro(**data.model_dump(exclude={"autores"}))
    libro.autorias = [LibroAutor(**autoria.model_dump()) for autoria in data.autores]
    session.add(libro)
    # La base verifica las FK y la unicidad; no se consulta antes si existen.
    await _guardar(session)
    return await get_libro(session, libro.id)


async def update_libro(session: AsyncSession, libro: Libro, data: LibroUpdate) -> Libro:
    cambios = data.model_dump(exclude_unset=True)
    autores = cambios.pop("autores", None)
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    try:
        if autores is not None:
            await session.execute(delete(LibroAutor).where(LibroAutor.libro_id == libro.id))
            session.add_all([LibroAutor(libro_id=libro.id, **autoria) for autoria in autores])
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se pudo actualizar el libro: ISBN, relaciones o datos en conflicto") from None
    return await get_libro(session, libro.id)


async def delete_libro(session: AsyncSession, libro: Libro) -> None:
    try:
        await session.execute(delete(LibroAutor).where(LibroAutor.libro_id == libro.id))
        await session.execute(delete(Libro).where(Libro.id == libro.id))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se puede borrar un libro utilizado en ventas") from None


async def list_libros_autor(session: AsyncSession, autor_id: int, limit: int, offset: int):
    from app.modules.autores.service import get_autor
    await get_autor(session, autor_id)
    consulta = select(LibroAutor).where(LibroAutor.autor_id == autor_id).options(
        joinedload(LibroAutor.libro).joinedload(Libro.editorial),
        joinedload(LibroAutor.libro).joinedload(Libro.genero),
    ).order_by(LibroAutor.libro_id).limit(limit).offset(offset)
    result = await session.execute(consulta)
    return result.scalars().all()


async def _guardar(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se pudo guardar el libro: ISBN, relaciones o datos en conflicto") from None
