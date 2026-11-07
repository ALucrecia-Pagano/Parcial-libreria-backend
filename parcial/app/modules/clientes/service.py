"""Reglas del módulo clientes.

Cada función recibe el Unit of Work y lo abre. El correo repetido y el perfil
duplicado los rechaza la base: el IntegrityError sale del bloque, el Unit of
Work revierte y el router lo traduce a 409. No hay consulta previa de unicidad.
"""
from fastapi import HTTPException, status

from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, PerfilCreate
from app.modules.clientes.unit_of_work import ClientesUnitOfWork


async def obtener(uow: ClientesUnitOfWork, cliente_id: int) -> Cliente:
    async with uow:
        return await _buscar(uow, cliente_id)


async def crear(uow: ClientesUnitOfWork, datos: ClienteCreate) -> Cliente:
    async with uow:
        cliente = await uow.clientes.add(
            Cliente(nombre=datos.nombre, email=datos.email)
        )
        return await _buscar(uow, cliente.id)


async def actualizar(
    uow: ClientesUnitOfWork, cliente_id: int, datos: ClienteUpdate
) -> Cliente:
    async with uow:
        cliente = await _buscar(uow, cliente_id)
        await uow.clientes.update(cliente, datos.model_dump(exclude_unset=True))
        return await _buscar(uow, cliente_id)


async def crear_perfil(
    uow: ClientesUnitOfWork, cliente_id: int, datos: PerfilCreate
) -> PerfilCliente:
    async with uow:
        await _buscar(uow, cliente_id)
        return await uow.perfiles.add(
            PerfilCliente(cliente_id=cliente_id, **datos.model_dump())
        )


async def _buscar(uow: ClientesUnitOfWork, cliente_id: int) -> Cliente:
    cliente = await uow.clientes.get_con_perfil(cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado"
        )
    return cliente
