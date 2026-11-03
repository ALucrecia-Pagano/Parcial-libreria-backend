"""DTOs de entrada y salida del módulo clientes."""

from typing import Optional
from sqlmodel import SQLModel


class ClienteCreate(SQLModel):
    nombre: str
    email: str


class ClienteUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None


class PerfilCreate(SQLModel):
    telefono: str
    direccion: str


class PerfilRead(SQLModel):
    id: int
    telefono: str
    direccion: str


class ClienteRead(SQLModel):
    id: int
    nombre: str
    email: str
    perfil: Optional[PerfilRead] = None
