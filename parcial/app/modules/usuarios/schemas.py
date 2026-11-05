"""DTOs de entrada y salida del módulo usuarios (CH-07)."""

from pydantic import BaseModel, ConfigDict

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
