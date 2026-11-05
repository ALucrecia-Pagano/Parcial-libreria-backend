"""Rutas HTTP del módulo editoriales.

El router construye el Unit of Work con una dependencia (misma sesión de la
petición), se lo pasa al servicio sin abrirlo y traduce el IntegrityError a 409.

Dos routers por convención del parcial:
- router_abierto: lecturas, no piden sesión (el catálogo es público).
- router_admin: escrituras; la guarda requiere_rol("ADMIN") llega con CH-10.
No hay DELETE: el catálogo auxiliar no se borra (decisión del grupo, CH-04).
GET /editoriales/{id}/libros vive en libros/router.py (CH-05).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.editoriales import service
from app.modules.editoriales.schemas import EditorialCreate, EditorialRead, EditorialUpdate
from app.modules.editoriales.unit_of_work import EditorialesUnitOfWork


def get_uow(session: SessionDep) -> EditorialesUnitOfWork:
    return EditorialesUnitOfWork(session)


UowDep = Annotated[EditorialesUnitOfWork, Depends(get_uow)]

router_abierto = APIRouter(prefix="/editoriales", tags=["editoriales"])
router_admin = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router_abierto.get("", response_model=Pagina[EditorialRead])
async def listar(uow: UowDep, paginacion: PaginacionDep):
    return await service.listar(uow, paginacion.page, paginacion.size)


@router_abierto.get("/{editorial_id}", response_model=EditorialRead)
async def obtener(editorial_id: int, uow: UowDep):
    return await service.obtener(uow, editorial_id)


@router_admin.post("", response_model=EditorialRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: EditorialCreate, uow: UowDep):
    try:
        return await service.crear(uow, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_admin.patch("/{editorial_id}", response_model=EditorialRead)
async def actualizar(editorial_id: int, datos: EditorialUpdate, uow: UowDep):
    try:
        return await service.actualizar(uow, editorial_id, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None
