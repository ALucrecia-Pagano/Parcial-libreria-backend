"""Contratos del módulo clientes: entrada estricta y salida con usuario_id.

Los de entrada rechazan lo que no declaran (extra="forbid"). usuario_id sale en
la lectura y no se puede mandar en el alta ni en el PATCH: el vínculo lo crea
el auto-registro, no el personal.
"""
from typing import Optional

from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel


class ClienteCreate(SQLModel):
    """Alta de mostrador: no lleva id ni usuario_id."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=180)


class ClienteUpdate(SQLModel):
    """PATCH parcial. Ausente = no se toca; null explícito o cuerpo vacío = 422."""

    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120)
    email: Optional[str] = Field(default=None, min_length=3, max_length=180)

    @model_validator(mode="after")
    def rechazar_vacio_o_nulos(self):
        if not self.model_fields_set:
            raise ValueError("El cuerpo del PATCH no puede estar vacío")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos del cliente no pueden ser nulos")
        return self


class PerfilCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    telefono: str = Field(min_length=1, max_length=40)
    direccion: str = Field(min_length=1, max_length=200)


class PerfilRead(SQLModel):
    id: int
    telefono: str
    direccion: str


class ClienteRead(SQLModel):
    id: int
    nombre: str
    email: str
    usuario_id: Optional[int] = None
    perfil: Optional[PerfilRead] = None
