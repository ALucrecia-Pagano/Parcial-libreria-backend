"""Contratos del catálogo y del objeto de asociación LibroAutor."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel
from app.modules.autores.schemas import AutorRead
from app.modules.editoriales.schemas import EditorialRead
from app.modules.generos.schemas import GeneroRead


class AutoriaCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    autor_id: int
    rol: Literal["autor", "coautor", "traductor", "ilustrador"]
    orden: int = Field(ge=1)


class LibroCreate(SQLModel):
    """Alta de libro (CH-06): el stock entra como stock_inicial y deja su movimiento.

    Con extra="forbid", mandar "stock" (en lugar de "stock_inicial") da 422.
    """

    model_config = ConfigDict(extra="forbid")

    isbn: str = Field(min_length=1)
    titulo: str = Field(min_length=1)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_inicial: int = Field(default=0, ge=0)
    editorial_id: int
    genero_id: int | None = None
    autores: list[AutoriaCreate] = Field(min_length=1)


class LibroUpdate(SQLModel):
    """PATCH del libro: solo título y precio (CH-05).

    El stock NO se edita por PATCH (RN-11): cambia con movimientos (CH-06). Con
    extra="forbid", mandar stock, isbn u otro campo da 422.
    """

    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, min_length=1)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def rechazar_nulos(self):
        # Ausente = no se toca; null explícito = 422 (las columnas son NOT NULL).
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError(f"{campo} no puede ser nulo")
        return self


class AutoriaRead(AutoriaCreate):
    autor: AutorRead


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
    autores: list[AutoriaRead] = Field(default_factory=list, validation_alias="autorias")


class LibroDetalleRead(LibroRead):
    pass


class ReponerIn(SQLModel):
    """Cuerpo de POST /libros/{id}/reponer."""

    model_config = ConfigDict(extra="forbid")

    cantidad: int = Field(gt=0)


class MovimientoRead(SQLModel):
    id: int
    libro_id: int
    venta_id: int | None
    usuario_id: int
    cantidad: int
    motivo: str
    cuando: datetime
