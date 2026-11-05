"""Rutas HTTP del módulo géneros.

router_abierto: lecturas públicas. router_admin: alta (requiere_rol("ADMIN") con CH-10).
No hay PATCH ni DELETE de géneros en el parcial (CH-04).
GET /generos/{id}/libros vive en libros/router.py (CH-05).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead
from app.modules.generos.unit_of_work import GenerosUnitOfWork


def get_uow(session: SessionDep) -> GenerosUnitOfWork:
    return GenerosUnitOfWork(session)


UowDep = Annotated[GenerosUnitOfWork, Depends(get_uow)]

router_abierto = APIRouter(prefix="/generos", tags=["generos"])
router_admin = APIRouter(prefix="/generos", tags=["generos"])


@router_abierto.get("", response_model=Pagina[GeneroRead])
async def listar(uow: UowDep, paginacion: PaginacionDep):
    return await service.listar(uow, paginacion.page, paginacion.size)


@router_abierto.get("/{genero_id}", response_model=GeneroRead)
async def obtener(genero_id: int, uow: UowDep):
    return await service.obtener(uow, genero_id)


@router_admin.post("", response_model=GeneroRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: GeneroCreate, uow: UowDep):
    try:
        return await service.crear(uow, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None
