"""Reglas del módulo libros.

Las funciones nuevas (CH-05) reciben el Unit of Work y lo abren con
`async with uow:`; nunca lo construyen ni reciben la sesión.

- La baja es lógica (RN-13): DELETE pone borrado_en y la fila queda, así las
  ventas viejas siguen mostrando el título y el ISBN se puede volver a usar.
- El PATCH solo toca título y precio: el stock no se edita por PATCH (RN-11).
- Los libros dados de baja no aparecen en el catálogo, ni en el detalle, ni en
  los «libros de» una editorial, un género o un autor.
"""
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroRead, LibroUpdate
from app.modules.libros.unit_of_work import LibrosUnitOfWork

LIBRO_NO_ENCONTRADO = "Libro no encontrado"


def _no_encontrado(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detalle)


async def listar(
    uow: LibrosUnitOfWork, page: int, size: int,
    titulo: str | None = None, genero_id: int | None = None,
) -> Pagina[LibroRead]:
    async with uow:
        total = await uow.libros.contar_catalogo(titulo, genero_id)
        validar_pagina(total, page, size)  # 422 antes de traer una página que no existe
        items = await uow.libros.listar_catalogo((page - 1) * size, size, titulo, genero_id)
        return construir_pagina([LibroRead.model_validate(lib) for lib in items], total, page, size)


async def obtener(uow: LibrosUnitOfWork, libro_id: int) -> Libro:
    async with uow:
        libro = await uow.libros.obtener_detalle(libro_id)
        if libro is None:
            raise _no_encontrado(LIBRO_NO_ENCONTRADO)
        return libro


async def actualizar(uow: LibrosUnitOfWork, libro_id: int, datos: LibroUpdate) -> Libro:
    async with uow:
        libro = await uow.libros.get_by_id(libro_id)  # no ve los dados de baja
        if libro is None:
            raise _no_encontrado(LIBRO_NO_ENCONTRADO)
        # exclude_unset: solo título y/o precio, lo que vino en el cuerpo (consigna §2.6).
        await uow.libros.update(libro, datos.model_dump(exclude_unset=True))
        return await uow.libros.obtener_detalle(libro_id)


async def dar_de_baja(uow: LibrosUnitOfWork, libro_id: int) -> None:
    async with uow:
        libro = await uow.libros.get_by_id(libro_id)
        if libro is None:  # inexistente o ya dado de baja
            raise _no_encontrado(LIBRO_NO_ENCONTRADO)
        await uow.libros.soft_delete(libro)


async def libros_de_editorial(uow: LibrosUnitOfWork, editorial_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.editoriales.get_by_id(editorial_id) is None:
            raise _no_encontrado("Editorial no encontrada")
        return await uow.libros.listar_vigentes_de_editorial(editorial_id)


async def libros_de_genero(uow: LibrosUnitOfWork, genero_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.generos.get_by_id(genero_id) is None:
            raise _no_encontrado("Género no encontrado")
        return await uow.libros.listar_vigentes_de_genero(genero_id)


async def libros_de_autor(uow: LibrosUnitOfWork, autor_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.autores.get_by_id(autor_id) is None:
            raise _no_encontrado("Autor no encontrado")
        return await uow.libros.listar_vigentes_de_autor(autor_id)


# ---------------------------------------------------------------------------
# LEGADO del TP: alta de libros con `stock` directo. Queda sin cambios hasta
# CH-06, que la reescribe con stock_inicial, el Unit of Work y el punto único
# de escritura del stock (con su movimiento «Stock inicial»).
# ---------------------------------------------------------------------------

async def create_libro(session: AsyncSession, data: LibroCreate) -> Libro:
    libro = Libro(**data.model_dump(exclude={"autores"}))
    libro.autorias = [LibroAutor(**autoria.model_dump()) for autoria in data.autores]
    session.add(libro)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "No se pudo guardar el libro: ISBN, relaciones o datos en conflicto") from None
    consulta = (
        select(Libro)
        .where(Libro.id == libro.id)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).joinedload(LibroAutor.autor),
        )
        .execution_options(populate_existing=True)
    )
    return (await session.execute(consulta)).scalars().first()
