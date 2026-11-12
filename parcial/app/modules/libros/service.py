"""Reglas del módulo libros.

Las funciones nuevas (CH-05) reciben el Unit of Work y lo abren con
`async with uow:`; nunca lo construyen ni reciben la sesión.

- La baja es lógica (RN-13): DELETE pone borrado_en y la fila queda, así las
  ventas viejas siguen mostrando el título y el ISBN se puede volver a usar.
- El PATCH solo toca título y precio: el stock no se edita por PATCH (RN-11).
- Los libros dados de baja no aparecen en el catálogo, ni en el detalle, ni en
  los «libros de» una editorial, un género o un autor.
- El stock solo cambia por `stock.aplicar_movimiento` (alta y reposición, CH-06).
"""
from collections.abc import Sequence

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.libros.models import Libro, LibroAutor, MovimientoStock
from app.modules.libros.schemas import LibroCreate, LibroRead, LibroUpdate
from app.modules.libros.stock import aplicar_movimiento
from app.modules.libros.unit_of_work import LibrosUnitOfWork

LIBRO_NO_ENCONTRADO = "Libro no encontrado"


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
            raise NoEncontrado(LIBRO_NO_ENCONTRADO)
        return libro


async def actualizar(uow: LibrosUnitOfWork, libro_id: int, datos: LibroUpdate) -> Libro:
    async with uow:
        libro = await uow.libros.get_by_id(libro_id)  # no ve los dados de baja
        if libro is None:
            raise NoEncontrado(LIBRO_NO_ENCONTRADO)
        # exclude_unset: solo título y/o precio, lo que vino en el cuerpo (consigna §2.6).
        await uow.libros.update(libro, datos.model_dump(exclude_unset=True))
        return await uow.libros.obtener_detalle(libro_id)


async def dar_de_baja(uow: LibrosUnitOfWork, libro_id: int) -> None:
    async with uow:
        libro = await uow.libros.get_by_id(libro_id)
        if libro is None:  # inexistente o ya dado de baja
            raise NoEncontrado(LIBRO_NO_ENCONTRADO)
        await uow.libros.soft_delete(libro)


async def libros_de_editorial(uow: LibrosUnitOfWork, editorial_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.editoriales.get_by_id(editorial_id) is None:
            raise NoEncontrado("Editorial no encontrada")
        return await uow.libros.listar_vigentes_de_editorial(editorial_id)


async def libros_de_genero(uow: LibrosUnitOfWork, genero_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.generos.get_by_id(genero_id) is None:
            raise NoEncontrado("Género no encontrado")
        return await uow.libros.listar_vigentes_de_genero(genero_id)


async def libros_de_autor(uow: LibrosUnitOfWork, autor_id: int) -> Sequence[Libro]:
    async with uow:
        if await uow.autores.get_by_id(autor_id) is None:
            raise NoEncontrado("Autor no encontrado")
        return await uow.libros.listar_vigentes_de_autor(autor_id)


async def crear(uow: LibrosUnitOfWork, datos: LibroCreate, usuario_id: int) -> Libro:
    """Alta atómica: libro + autorías + movimiento «Stock inicial» en una transacción.

    El libro nace con stock 0 y el stock inicial entra por el punto único de
    escritura. Con stock_inicial 0 no hay movimiento (CHECK cantidad <> 0).
    ISBN repetido entre vigentes o FK inexistente → IntegrityError → 409 en el router.
    """
    async with uow:
        libro = Libro(**datos.model_dump(exclude={"autores", "stock_inicial"}))  # stock arranca en 0 (default)
        libro.autorias = [LibroAutor(**autoria.model_dump()) for autoria in datos.autores]
        await uow.libros.add(libro)
        if datos.stock_inicial > 0:
            await aplicar_movimiento(uow, libro, datos.stock_inicial, "Stock inicial", usuario_id)
        return await uow.libros.obtener_detalle(libro.id)


async def reponer(
    uow: LibrosUnitOfWork, libro_id: int, cantidad: int, usuario_id: int
) -> MovimientoStock:
    async with uow:
        libro = await uow.libros.get_by_id_including_deleted(libro_id)
        if libro is None:
            raise NoEncontrado(LIBRO_NO_ENCONTRADO)
        if libro.borrado_en is not None:
            # RN-13: el libro existe pero está dado de baja → conflicto, no «no encontrado».
            raise Conflicto("No se puede reponer un libro dado de baja")
        return await aplicar_movimiento(uow, libro, cantidad, "Reposición", usuario_id)


async def movimientos(uow: LibrosUnitOfWork, libro_id: int) -> Sequence[MovimientoStock]:
    """Historial de stock del libro; también para libros dados de baja (auditoría)."""
    async with uow:
        if await uow.libros.get_by_id_including_deleted(libro_id) is None:
            raise NoEncontrado(LIBRO_NO_ENCONTRADO)
        return await uow.movimientos.listar_de_libro(libro_id)
