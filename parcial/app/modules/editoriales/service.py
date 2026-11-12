"""Reglas del módulo editoriales.

Cada función RECIBE el Unit of Work (nunca lo construye) y lo abre con
`async with uow:`. Si la base rechaza una escritura (nombre repetido, RN-01), el
IntegrityError sale del bloque, el Unit of Work revierte y el router lo traduce a
409 con mensaje propio. No se consulta antes si el nombre existe: lo garantiza
el UNIQUE uq_editorial_nombre.
"""
from app.core.errores import NoEncontrado
from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialRead, EditorialUpdate
from app.modules.editoriales.unit_of_work import EditorialesUnitOfWork


async def listar(uow: EditorialesUnitOfWork, page: int, size: int) -> Pagina[EditorialRead]:
    async with uow:
        total = await uow.editoriales.count()
        validar_pagina(total, page, size)  # 422 antes de traer una página que no existe
        items = await uow.editoriales.get_all(offset=(page - 1) * size, limit=size)
        return construir_pagina(
            [EditorialRead.model_validate(e) for e in items], total, page, size
        )


async def obtener(uow: EditorialesUnitOfWork, editorial_id: int) -> Editorial:
    async with uow:
        return await _buscar(uow, editorial_id)


async def crear(uow: EditorialesUnitOfWork, datos: EditorialCreate) -> Editorial:
    async with uow:
        return await uow.editoriales.add(Editorial.model_validate(datos))


async def actualizar(
    uow: EditorialesUnitOfWork, editorial_id: int, datos: EditorialUpdate
) -> Editorial:
    async with uow:
        editorial = await _buscar(uow, editorial_id)
        # exclude_unset: solo los campos que vinieron en el cuerpo (consigna §2.6).
        return await uow.editoriales.update(editorial, datos.model_dump(exclude_unset=True))


async def _buscar(uow: EditorialesUnitOfWork, editorial_id: int) -> Editorial:
    editorial = await uow.editoriales.get_by_id(editorial_id)
    if editorial is None:
        raise NoEncontrado("Editorial no encontrada")
    return editorial
