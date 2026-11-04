"""Tablas cliente y perfil_cliente (uno a uno: un cliente, un perfil)."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuarios.models import Usuario
    from app.modules.ventas.models import Venta


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"
    __table_args__ = (
        UniqueConstraint("email", name="uq_cliente_email"),
        UniqueConstraint("usuario_id", name="uq_cliente_usuario_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")

    perfil: Optional["PerfilCliente"] = Relationship(
        back_populates="cliente", sa_relationship_kwargs={"uselist": False}
    )
    usuario: Optional["Usuario"] = Relationship(
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


import app.modules.usuarios.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401
