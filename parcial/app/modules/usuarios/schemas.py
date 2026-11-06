"""DTOs de entrada y salida del módulo usuarios (CH-07, CH-08, CH-10, CH-11 y CH-12)."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.security import PasswordBcrypt


class LoginIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: PasswordBcrypt


class LoginOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str
    debe_cambiar_password: bool
    expira_en_segundos: int


class RegistroIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    email: str
    password: PasswordBcrypt


# Alias semántico
RegistroClienteRequest = RegistroIn


class RegistroOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    nombre: str
    email: str
    cliente_id: int
    mensaje: str = "Registro completado exitosamente"


# Alias semántico
RegistroClienteResponse = RegistroOut


class LogoutOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str = "Sesión cerrada exitosamente"


class UsuarioYoOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    email: str
    nombre: str
    activo: bool
    debe_cambiar_password: bool
    roles_base: list[str]
    roles_token: list[str]


# Alias semántico
UsuarioYoResponse = UsuarioYoOut


class CambiarPasswordIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password_actual: PasswordBcrypt
    password_nueva: PasswordBcrypt


class CambiarPasswordOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str = "Contraseña actualizada correctamente"


class MensajeOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str


class UsuarioCreateAdminIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    nombre: str
    password: PasswordBcrypt
    rol: Literal["ADMIN", "VENDEDOR", "CLIENTE"]


class UsuarioAdminOut(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    email: str
    nombre: str
    activo: bool
    debe_cambiar_password: bool


class AsignacionRolCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: Literal["ADMIN", "VENDEDOR", "CLIENTE"]
    vence_en: datetime | None = None

    @field_validator("vence_en")
    @classmethod
    def validar_vence_en(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("vence_en debe incluir zona horaria")
        if v <= datetime.now(timezone.utc):
            raise ValueError("vence_en debe ser una fecha futura")
        return v


class AsignacionRolOut(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    usuario_id: int
    rol: str
    desde: datetime
    vence_en: datetime | None
    revocada_en: datetime | None
    otorgada_por: int | None


class EventoSeguridadOut(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    cuando: datetime
    actor: str
    accion: str

