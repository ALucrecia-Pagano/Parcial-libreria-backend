"""Repositorios de cliente y perfil. Ninguno confirma la transacción.

La precarga del perfil vive dentro de los métodos que lo devuelven (consigna
§6.5): una lectura no depende de la carga perezosa.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.repository import BaseRepository
from app.modules.clientes.models import Cliente, PerfilCliente


class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Cliente)

    async def get_con_perfil(self, cliente_id: int) -> Cliente | None:
        consulta = (
            select(Cliente)
            .where(Cliente.id == cliente_id)
            .options(joinedload(Cliente.perfil))
            .execution_options(populate_existing=True)
        )
        return (await self.session.scalars(consulta)).unique().one_or_none()

    async def get_by_email(self, email: str) -> Cliente | None:
        consulta = (
            select(Cliente)
            .where(Cliente.email == email)
            .options(joinedload(Cliente.perfil))
        )
        return (await self.session.scalars(consulta)).unique().one_or_none()

    async def get_by_usuario_id(self, usuario_id: int) -> Cliente | None:
        consulta = (
            select(Cliente)
            .where(Cliente.usuario_id == usuario_id)
            .options(joinedload(Cliente.perfil))
        )
        return (await self.session.scalars(consulta)).unique().one_or_none()


class PerfilClienteRepository(BaseRepository[PerfilCliente]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PerfilCliente)
