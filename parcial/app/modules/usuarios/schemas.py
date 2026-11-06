"""DTOs de entrada y salida del módulo usuarios (CH-07, CH-08, CH-10 y CH-11)."""

from pydantic import BaseModel, ConfigDict, EmailStr

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
