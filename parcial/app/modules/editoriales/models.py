"""Tabla editorial (agregación: muchos libros comparten una editorial)."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    pais: str

    libros: list["Libro"] = Relationship(back_populates="editorial")


import app.modules.libros.models  # noqa: F401
