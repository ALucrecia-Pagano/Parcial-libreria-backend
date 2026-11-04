"""Tablas libro y libro_autor.

libro_autor es la entidad intermedia del muchos a muchos entre libro y
autor: guarda los datos propios de la relación (rol y orden). Para ir de
un libro a sus autores se navega ``libro.autorias[i].autor``.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Numeric, text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.autores.models import Autor
    from app.modules.clientes.models import Cliente  # noqa: F401 (registro del metadata)
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.usuarios.models import Usuario
    from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401 (registro del metadata)


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_libro_precio_positivo"),
        CheckConstraint("stock >= 0", name="ck_libro_stock_no_negativo"),
        # ISBN único solo entre libros vigentes (no dados de baja).
        Index(
            "uq_libro_isbn_vigente",
            "isbn",
            unique=True,
            postgresql_where=text("borrado_en IS NULL"),
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str
    titulo: str = Field(index=True)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0)
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: Optional[int] = Field(
        default=None, foreign_key="genero.id", index=True
    )
    borrado_en: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    editorial: Optional["Editorial"] = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    autorias: list["LibroAutor"] = Relationship(back_populates="libro")
    renglones: list["RenglonVenta"] = Relationship(back_populates="libro")
    movimientos: list["MovimientoStock"] = Relationship(back_populates="libro")


class LibroAutor(SQLModel, table=True):
    """Objeto de asociación libro <-> autor (clave primaria compuesta)."""

    __tablename__ = "libro_autor"
    __table_args__ = (
        CheckConstraint("orden >= 1", name="ck_libro_autor_orden_minimo"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="ck_libro_autor_rol_valido",
        ),
    )

    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True, index=True)
    rol: str
    orden: int

    libro: Optional["Libro"] = Relationship(back_populates="autorias")
    autor: Optional["Autor"] = Relationship(back_populates="autorias")


class MovimientoStock(SQLModel, table=True):
    """Registro de solo agregado de cada cambio de stock (cantidad con signo)."""

    __tablename__ = "movimiento_stock"
    __table_args__ = (
        CheckConstraint("cantidad <> 0", name="ck_movimiento_stock_cantidad_no_cero"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    venta_id: Optional[int] = Field(default=None, foreign_key="venta.id", index=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    cantidad: int
    motivo: str
    cuando: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    libro: Optional["Libro"] = Relationship(back_populates="movimientos")
    venta: Optional["Venta"] = Relationship(back_populates="movimientos")
    usuario: Optional["Usuario"] = Relationship(back_populates="movimientos")


import app.modules.autores.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.usuarios.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401
