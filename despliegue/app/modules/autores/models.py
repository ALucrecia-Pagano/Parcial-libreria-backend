"""Tabla autor (muchos a muchos con libro vía libro_autor)."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import LibroAutor


class Autor(SQLModel, table=True):
    __tablename__ = "autor"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: str

    autorias: list["LibroAutor"] = Relationship(back_populates="autor")


import app.modules.libros.models  # noqa: F401
