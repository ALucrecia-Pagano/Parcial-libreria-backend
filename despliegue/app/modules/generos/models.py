"""Tabla genero (agregación opcional: un libro puede no tener género)."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Genero(SQLModel, table=True):
    __tablename__ = "genero"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)

    libros: list["Libro"] = Relationship(back_populates="genero")


import app.modules.libros.models  # noqa: F401
