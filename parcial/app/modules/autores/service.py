"""Reglas del módulo autores.

Cada función recibe el Unit of Work y lo abre con `async with uow:`. Un
IntegrityError sale del bloque, el Unit of Work revierte y el router lo traduce.
"""
from fastapi import HTTPException, status

from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate
from app.modules.autores.unit_of_work import AutoresUnitOfWork

MENSAJE_NO_ENCONTRADO = "Autor no encontrado"


async def listar(uow: AutoresUnitOfWork, page: int, size: int) -> Pagina[AutorRead]:
    async with uow:
        total = await uow.autores.count()
        validar_pagina(total, page, size)
        items = await uow.autores.get_all(offset=(page - 1) * size, limit=size)
        return construir_pagina([AutorRead.model_validate(a) for a in items], total, page, size)


async def obtener(uow: AutoresUnitOfWork, autor_id: int) -> Autor:
    async with uow:
        return await _buscar(uow, autor_id)


async def crear(uow: AutoresUnitOfWork, datos: AutorCreate) -> Autor:
    async with uow:
        return await uow.autores.add(Autor.model_validate(datos))


async def actualizar(uow: AutoresUnitOfWork, autor_id: int, datos: AutorUpdate) -> Autor:
    async with uow:
        autor = await _buscar(uow, autor_id)
        return await uow.autores.update(autor, datos.model_dump(exclude_unset=True))


async def _buscar(uow: AutoresUnitOfWork, autor_id: int) -> Autor:
    autor = await uow.autores.get_by_id(autor_id)
    if autor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MENSAJE_NO_ENCONTRADO)
    return autor

