"""Contratos de autores, separados de la tabla.

Los de entrada rechazan los campos que no declaran (extra="forbid").
"""
from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel


class AutorCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1)
    nacionalidad: str = Field(min_length=1)


class AutorRead(SQLModel):
    id: int
    nombre: str
    nacionalidad: str


class AutorUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1)
    nacionalidad: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def rechazar_nulos(self):
        # Ausente = no se toca; null explícito = 422 (las columnas son NOT NULL).
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos del autor no pueden ser nulos")
        return self
