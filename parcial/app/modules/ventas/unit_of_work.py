"""Unit of Work de ventas: venta, renglones, libros, movimientos y clientes.

Todo usa la misma sesión. El stock se escribe solo con aplicar_movimiento,
que espera el repositorio `movimientos`.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.core.unit_of_work import UnitOfWork
from app.modules.clientes.models import Cliente
from app.modules.libros.repository import LibroRepository, MovimientoStockRepository
from app.modules.ventas.repository import RenglonVentaRepository, VentaRepository


class VentasUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.ventas = VentaRepository(session)
        self.renglones = RenglonVentaRepository(session)
        self.libros = LibroRepository(session)
        self.movimientos = MovimientoStockRepository(session)
        self.clientes = BaseRepository(session, Cliente)
