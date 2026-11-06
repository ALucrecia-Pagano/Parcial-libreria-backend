"""Reglas del módulo géneros.

Cada función recibe el Unit of Work y lo abre con `async with uow:`. El nombre
repetido (RN-01) lo rechaza la base (uq_genero_nombre): el IntegrityError sale
del bloque, el Unit of Work revierte y el router responde 409 con mensaje propio.
"""
from fastapi import HTTPException, status

from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate, GeneroRead
from app.modules.generos.unit_of_work import GenerosUnitOfWork


async def listar(uow: GenerosUnitOfWork, page: int, size: int) -> Pagina[GeneroRead]:
    async with uow:
        total = await uow.generos.count()
        validar_pagina(total, page, size)
        items = await uow.generos.get_all(offset=(page - 1) * size, limit=size)
        return construir_pagina([GeneroRead.model_validate(g) for g in items], total, page, size)


async def obtener(uow: GenerosUnitOfWork, genero_id: int) -> Genero:
    async with uow:
        genero = await uow.generos.get_by_id(genero_id)
        if genero is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Género no encontrado")
        return genero


async def crear(uow: GenerosUnitOfWork, datos: GeneroCreate) -> Genero:
    async with uow:
        return await uow.generos.add(Genero.model_validate(datos))
