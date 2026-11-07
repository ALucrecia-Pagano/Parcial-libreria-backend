"""Repositorios de venta y renglón.

La precarga del detalle (cliente, renglones y libro de cada renglón, aunque el
libro esté dado de baja) se declara acá. El número de consultas no crece con
los renglones: un joinedload del cliente y un selectinload de los renglones.
"""
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.repository import BaseRepository
from app.modules.clientes.models import Cliente
from app.modules.ventas.models import RenglonVenta, Venta


class VentaRepository(BaseRepository[Venta]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Venta)

    async def obtener_detalle(self, venta_id: int) -> Venta | None:
        consulta = (
            select(Venta)
            .where(Venta.id == venta_id)
            .options(
                joinedload(Venta.cliente),
                selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
            )
            .execution_options(populate_existing=True)
        )
        return (await self.session.scalars(consulta)).unique().one_or_none()

    async def contar(
        self, cliente_id: int | None = None, usuario_id: int | None = None
    ) -> int:
        consulta = select(func.count()).select_from(Venta)
        consulta = self._filtrar(consulta, cliente_id, usuario_id)
        return await self.session.scalar(consulta)

    async def listar(
        self,
        offset: int,
        limit: int,
        cliente_id: int | None = None,
        usuario_id: int | None = None,
    ) -> Sequence[Venta]:
        consulta = select(Venta).order_by(Venta.id).offset(offset).limit(limit)
        consulta = self._filtrar(consulta, cliente_id, usuario_id)
        return (await self.session.scalars(consulta)).all()

    @staticmethod
    def _filtrar(consulta, cliente_id: int | None, usuario_id: int | None):
        if cliente_id is not None:
            consulta = consulta.where(Venta.cliente_id == cliente_id)
        if usuario_id is not None:
            consulta = consulta.join(Cliente, Venta.cliente_id == Cliente.id).where(
                Cliente.usuario_id == usuario_id
            )
        return consulta


class RenglonVentaRepository(BaseRepository[RenglonVenta]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RenglonVenta)
