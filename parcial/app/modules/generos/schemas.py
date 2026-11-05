"""Contratos del módulo géneros: entrada (Create) y salida (Read).

No hay GeneroUpdate: el parcial no tiene PATCH /generos (CH-04).
El de entrada rechaza los campos que no declara (extra="forbid").
"""
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class GeneroCreate(SQLModel):
    """Entrada del alta: no lleva id, lo genera la base."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=80)


class GeneroRead(SQLModel):
    """Salida: lo que la API devuelve al cliente."""

    id: int
    nombre: str
