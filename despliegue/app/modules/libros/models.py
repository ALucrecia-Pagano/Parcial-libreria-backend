"""Tablas libro y libro_autor.

libro_autor es la entidad intermedia del muchos a muchos entre libro y
autor: guarda los datos propios de la relación (rol y orden). Para ir de
un libro a sus autores se navega ``libro.autorias[i].autor``.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.autores.models import Autor
    from app.modules.clientes.models import Cliente  # noqa: F401 (registro del metadata)
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401 (registro del metadata)


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_libro_precio_positivo"),
        CheckConstraint("stock >= 0", name="ck_libro_stock_no_negativo"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)
    titulo: str = Field(index=True)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0)
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: Optional[int] = Field(
        default=None, foreign_key="genero.id", index=True
    )

    editorial: Optional["Editorial"] = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    autorias: list["LibroAutor"] = Relationship(back_populates="libro")
    renglones: list["RenglonVenta"] = Relationship(back_populates="libro")


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


import app.modules.autores.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401
