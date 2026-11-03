"""Tablas cliente y perfil_cliente (uno a uno: un cliente, un perfil)."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.ventas.models import Venta


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)

    perfil: Optional["PerfilCliente"] = Relationship(
        back_populates="cliente", sa_relationship_kwargs={"uselist": False}
    )
    ventas: list["Venta"] = Relationship(back_populates="cliente")


class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", unique=True, index=True)
    telefono: str
    direccion: str

    cliente: Optional["Cliente"] = Relationship(back_populates="perfil")


import app.modules.ventas.models  # noqa: F401
