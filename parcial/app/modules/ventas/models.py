"""Tablas venta y renglon_venta.

La venta se crea con sus renglones (composición: el renglón nace con la
venta); cada renglón nombra un libro que ya existe (asociación).
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import Libro


class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_venta_total_no_negativo"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    fecha: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    total: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False),
    )

    cliente: Optional["Cliente"] = Relationship(back_populates="ventas")
    renglones: list["RenglonVenta"] = Relationship(back_populates="venta")


class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_renglon_cantidad_positiva"),
        CheckConstraint(
            "precio_unitario > 0", name="ck_renglon_precio_unitario_positivo"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False)
    )

    venta: Optional["Venta"] = Relationship(back_populates="renglones")
    libro: Optional["Libro"] = Relationship(back_populates="renglones")


import app.modules.clientes.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
