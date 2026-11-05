"""Rutas HTTP del módulo autores.

router_abierto: lecturas públicas. router_admin: alta y PATCH (requiere_rol("ADMIN") con CH-10).
No hay DELETE: el catálogo auxiliar no se borra (decisión del grupo, CH-04).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate
from app.modules.autores.unit_of_work import AutoresUnitOfWork
from app.modules.libros.schemas import LibroDeAutorRead
from app.modules.libros.service import list_libros_autor


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


# Pendiente de CH-05 (fuera del alcance de CH-04): sin cambios de lógica.
@router_abierto.get("/{autor_id}/libros", response_model=list[LibroDeAutorRead])
async def libros_del_autor(
    autor_id: int,
    uow: UowDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await list_libros_autor(uow.session, autor_id, limit, offset)


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
