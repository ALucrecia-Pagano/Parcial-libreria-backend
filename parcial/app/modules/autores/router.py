"""Rutas HTTP del módulo autores.

router_abierto: lecturas públicas. router_admin: alta y PATCH (requiere_rol("ADMIN") con CH-10).
No hay DELETE: el catálogo auxiliar no se borra (decisión del grupo, CH-04).
GET /autores/{id}/libros vive en libros/router.py (CH-05).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate
from app.modules.autores.unit_of_work import AutoresUnitOfWork


def get_uow(session: SessionDep) -> AutoresUnitOfWork:
    return AutoresUnitOfWork(session)


UowDep = Annotated[AutoresUnitOfWork, Depends(get_uow)]

router_abierto = APIRouter(prefix="/autores", tags=["autores"])
router_admin = APIRouter(prefix="/autores", tags=["autores"])


@router_abierto.get("", response_model=Pagina[AutorRead])
async def listar(uow: UowDep, paginacion: PaginacionDep):
    return await service.listar(uow, paginacion.page, paginacion.size)


@router_abierto.get("/{autor_id}", response_model=AutorRead)
async def obtener(autor_id: int, uow: UowDep):
    return await service.obtener(uow, autor_id)


@router_admin.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: AutorCreate, uow: UowDep):
    try:
        return await service.crear(uow, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_admin.patch("/{autor_id}", response_model=AutorRead)
async def actualizar(autor_id: int, datos: AutorUpdate, uow: UowDep):
    try:
        return await service.actualizar(uow, autor_id, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None
