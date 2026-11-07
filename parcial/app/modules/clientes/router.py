"""Rutas de clientes para VENDEDOR o ADMIN.

El router construye el Unit of Work y no lo abre. La guarda de rol la pone
main.py al montar router_staff. Las ventas del cliente viven en el módulo ventas.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.errores import traducir_integrity_error
from app.modules.clientes import service
from app.modules.clientes.schemas import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilCreate,
    PerfilRead,
)
from app.modules.clientes.unit_of_work import ClientesUnitOfWork


def get_uow(session: SessionDep) -> ClientesUnitOfWork:
    return ClientesUnitOfWork(session)


UowDep = Annotated[ClientesUnitOfWork, Depends(get_uow)]

router_staff = APIRouter(prefix="/clientes", tags=["clientes"])


@router_staff.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: ClienteCreate, uow: UowDep):
    try:
        return await service.crear(uow, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_staff.get("/{cliente_id}", response_model=ClienteRead)
async def obtener(cliente_id: int, uow: UowDep):
    return await service.obtener(uow, cliente_id)


@router_staff.patch("/{cliente_id}", response_model=ClienteRead)
async def actualizar(cliente_id: int, datos: ClienteUpdate, uow: UowDep):
    try:
        return await service.actualizar(uow, cliente_id, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_staff.post(
    "/{cliente_id}/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_201_CREATED,
)
async def crear_perfil(cliente_id: int, datos: PerfilCreate, uow: UowDep):
    try:
        return await service.crear_perfil(uow, cliente_id, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None

