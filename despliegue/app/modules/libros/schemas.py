"""Contratos del catálogo y del objeto de asociación LibroAutor."""
from decimal import Decimal
from typing import Literal
from pydantic import model_validator
from sqlmodel import Field, SQLModel
from app.modules.autores.schemas import AutorRead
from app.modules.editoriales.schemas import EditorialRead
from app.modules.generos.schemas import GeneroRead


class AutoriaCreate(SQLModel):
    autor_id: int
    rol: Literal["autor", "coautor", "traductor", "ilustrador"]
    orden: int = Field(ge=1)


class LibroCreate(SQLModel):
    isbn: str = Field(min_length=1)
    titulo: str = Field(min_length=1)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    editorial_id: int
    genero_id: int | None = None
    autores: list[AutoriaCreate]


class LibroUpdate(SQLModel):
    isbn: str | None = Field(default=None, min_length=1)
    titulo: str | None = Field(default=None, min_length=1)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    editorial_id: int | None = None
    genero_id: int | None = None
    autores: list[AutoriaCreate] | None = None

    @model_validator(mode="after")
    def rechazar_nulos(self):
        for campo in self.model_fields_set - {"genero_id"}:
            if getattr(self, campo) is None:
                raise ValueError(f"{campo} no puede ser nulo")
        return self


class LibroRead(SQLModel):
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: int
    genero_id: int | None
    editorial: EditorialRead
    genero: GeneroRead | None


class AutoriaRead(AutoriaCreate):
    autor: AutorRead


class LibroDetalleRead(LibroRead):
    autores: list[AutoriaRead] = Field(validation_alias="autorias")


class LibroDeAutorRead(SQLModel):
    rol: str
    orden: int
    libro: LibroRead
