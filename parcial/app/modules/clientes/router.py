"""Rutas HTTP del módulo clientes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.clientes import service
from app.modules.clientes.schemas import (
    ClienteCreate, ClienteRead, ClienteUpdate, PerfilCreate, PerfilRead,
)
from app.modules.ventas.schemas import VentaRead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
async def create(data: ClienteCreate, session: AsyncSession = Depends(get_session)):
    return await service.create_cliente(session, data)


@router.get("/", response_model=list[ClienteRead])
async def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await service.list_clientes(session, limit, offset)


@router.get("/{cliente_id}", response_model=ClienteRead)
async def get_one(cliente_id: int, session: AsyncSession = Depends(get_session)):
    return await service.get_cliente(session, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteRead)
async def update(
    cliente_id: int, data: ClienteUpdate, session: AsyncSession = Depends(get_session),
):
    return await service.update_cliente(session, cliente_id, data)


@router.post("/{cliente_id}/perfil", response_model=PerfilRead, status_code=status.HTTP_201_CREATED)
async def create_perfil(
    cliente_id: int, data: PerfilCreate, session: AsyncSession = Depends(get_session),
):
    return await service.create_perfil(session, cliente_id, data)


@router.get("/{cliente_id}/ventas", response_model=list[VentaRead])
async def list_ventas(
    cliente_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await service.list_ventas_cliente(session, cliente_id, limit, offset)
