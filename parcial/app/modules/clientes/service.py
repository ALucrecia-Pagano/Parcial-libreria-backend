"""Lógica del módulo clientes y traducción de errores de la base."""

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, PerfilCreate
from app.modules.ventas.models import Venta


async def list_clientes(session: AsyncSession, limit: int, offset: int) -> Sequence[Cliente]:
    consulta = (
        select(Cliente).options(joinedload(Cliente.perfil))
        .order_by(Cliente.id).limit(limit).offset(offset)
    )
    result = await session.execute(consulta)
    return result.scalars().all()


async def get_cliente(session: AsyncSession, cliente_id: int) -> Cliente:
    consulta = (
        select(Cliente).where(Cliente.id == cliente_id)
        .options(joinedload(Cliente.perfil))
    )
    result = await session.execute(consulta)
    cliente = result.scalars().first()
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente


async def create_cliente(session: AsyncSession, data: ClienteCreate) -> Cliente:
    cliente = Cliente.model_validate(data)
    session.add(cliente)
    await _guardar(session, "Ya existe un cliente con ese email")
    return await get_cliente(session, cliente.id)


async def update_cliente(session: AsyncSession, cliente_id: int, data: ClienteUpdate) -> Cliente:
    cliente = await get_cliente(session, cliente_id)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    await _guardar(session, "No se pudo actualizar el cliente: email repetido o datos inválidos")
    return cliente


async def create_perfil(session: AsyncSession, cliente_id: int, data: PerfilCreate) -> PerfilCliente:
    await get_cliente(session, cliente_id)
    perfil = PerfilCliente(cliente_id=cliente_id, **data.model_dump())
    session.add(perfil)
    await _guardar(session, "El cliente ya tiene un perfil")
    return perfil


async def list_ventas_cliente(
    session: AsyncSession, cliente_id: int, limit: int, offset: int
) -> Sequence[Venta]:
    await get_cliente(session, cliente_id)
    consulta = (
        select(Venta).where(Venta.cliente_id == cliente_id)
        .order_by(Venta.id).limit(limit).offset(offset)
    )
    result = await session.execute(consulta)
    return result.scalars().all()


async def _guardar(session: AsyncSession, mensaje_conflicto: str) -> None:
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=mensaje_conflicto
        ) from None
