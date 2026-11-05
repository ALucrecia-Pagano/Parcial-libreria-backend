"""Contratos del módulo editoriales: entrada (Create, Update) y salida (Read).

Los de entrada rechazan los campos que no declaran (extra="forbid"): un campo de
más es un 422, no algo que se ignora en silencio (RN-11 como patrón).
"""
from typing import Optional

from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel


class EditorialCreate(SQLModel):
    """Entrada del alta: no lleva id, lo genera la base."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    pais: str = Field(min_length=1, max_length=80)


class EditorialUpdate(SQLModel):
    """Entrada del PATCH: todo opcional; el servicio aplica solo lo enviado (exclude_unset)."""

    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120)
    pais: Optional[str] = Field(default=None, min_length=1, max_length=80)

    @model_validator(mode="after")
    def rechazar_nulos(self):
        # Ausente = no se toca; null explícito = 422 (las columnas son NOT NULL).
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos de la editorial no pueden ser nulos")
        return self


class EditorialRead(SQLModel):
    """Salida: lo que la API devuelve al cliente."""

    id: int
    nombre: str
    pais: str
