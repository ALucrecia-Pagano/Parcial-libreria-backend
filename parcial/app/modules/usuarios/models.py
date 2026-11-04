"""Tablas de acceso: usuario, asignacion_rol, intento_acceso y evento_seguridad.

Un usuario no tiene columna ``rol``: los roles viven en ``asignacion_rol``
(historial con apertura y cierre). ``intento_acceso`` y ``evento_seguridad``
no se relacionan con ninguna otra tabla (aisladas por diseño).
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Index, UniqueConstraint, text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import MovimientoStock


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    __table_args__ = (UniqueConstraint("email", name="uq_usuario_email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    nombre: str
    password_hash: str
    activo: bool = Field(default=True)
    debe_cambiar_password: bool = Field(default=False)

    cliente: Optional["Cliente"] = Relationship(
        back_populates="usuario", sa_relationship_kwargs={"uselist": False}
    )
    asignaciones: list["AsignacionRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "[AsignacionRol.usuario_id]"},
    )
    asignaciones_otorgadas: list["AsignacionRol"] = Relationship(
        back_populates="otorgante",
        sa_relationship_kwargs={"foreign_keys": "[AsignacionRol.otorgada_por]"},
    )
    movimientos: list["MovimientoStock"] = Relationship(back_populates="usuario")


class AsignacionRol(SQLModel, table=True):
    __tablename__ = "asignacion_rol"
    __table_args__ = (
        CheckConstraint(
            "rol IN ('ADMIN','VENDEDOR','CLIENTE')",
            name="ck_asignacion_rol_rol_valido",
        ),
        # A lo sumo una asignación abierta (no revocada) por usuario y rol (RN-03).
        Index(
            "uq_asignacion_rol_abierta",
            "usuario_id",
            "rol",
            unique=True,
            postgresql_where=text("revocada_en IS NULL"),
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    rol: str
    desde: datetime = Field(
        default_factory=_ahora,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    vence_en: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    revocada_en: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    otorgada_por: Optional[int] = Field(
        default=None, foreign_key="usuario.id", index=True
    )

    usuario: Optional["Usuario"] = Relationship(
        back_populates="asignaciones",
        sa_relationship_kwargs={"foreign_keys": "[AsignacionRol.usuario_id]"},
    )
    otorgante: Optional["Usuario"] = Relationship(
        back_populates="asignaciones_otorgadas",
        sa_relationship_kwargs={"foreign_keys": "[AsignacionRol.otorgada_por]"},
    )


class IntentoAcceso(SQLModel, table=True):
    __tablename__ = "intento_acceso"
    __table_args__ = (
        Index("ix_intento_acceso_email_ip_cuando", "email", "ip", "cuando"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    cuando: datetime = Field(
        default_factory=_ahora,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    email: str
    ip: str
    exito: bool


class EventoSeguridad(SQLModel, table=True):
    __tablename__ = "evento_seguridad"

    id: Optional[int] = Field(default=None, primary_key=True)
    cuando: datetime = Field(
        default_factory=_ahora,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    actor: str
    accion: str


import app.modules.clientes.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
