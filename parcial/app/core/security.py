"""Funciones criptográficas y manejo de tokens de seguridad (CH-07).

- Bcrypt corre en hilos de trabajo vía `asyncio.to_thread` con semáforo para no
  bloquear el event loop de FastAPI (EA-01, cátedra §5.6).
- `PasswordBcrypt` valida que la contraseña no exceda 72 bytes en UTF-8,
  respondiendo 422 ante desbordes (cátedra §5.4, §2.3.1).
- Tokens JWT firmados con HMAC-SHA256 y vigencia acotada a `settings.JWT_MINUTOS`.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import bcrypt
import jwt
from pydantic import AfterValidator

from app.core.config import settings

# Semáforo para controlar la concurrencia de hashing y no saturar hilos ni CPU.
_BCRYPT_SEMAPHORE = asyncio.Semaphore(4)


def _validar_longitud_bcrypt(v: str) -> str:
    if len(v.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar los 72 bytes")
    return v


PasswordBcrypt = Annotated[str, AfterValidator(_validar_longitud_bcrypt)]


def _hash_sync(password: str) -> str:
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_COSTO)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def hashear_password(password: str) -> str:
    """Calcula el hash bcrypt en un worker thread respetando el semáforo."""
    async with _BCRYPT_SEMAPHORE:
        return await asyncio.to_thread(_hash_sync, password)


def _verify_sync(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Formato de salt o hash inválido esperado de bcrypt
        return False


async def verificar_password(password: str, password_hash: str) -> bool:
    """Verifica la contraseña contra el hash bcrypt en un worker thread."""
    async with _BCRYPT_SEMAPHORE:
        return await asyncio.to_thread(_verify_sync, password, password_hash)


def crear_token(sub: str, roles: list[str]) -> str:
    """Emite un JWT con claims 'sub', 'roles', 'iat' y 'exp' firmado con JWT_SECRET."""
    ahora = datetime.now(timezone.utc)
    expira = ahora + timedelta(minutes=settings.JWT_MINUTOS)
    payload: dict[str, Any] = {
        "sub": sub,
        "roles": roles,
        "iat": int(ahora.timestamp()),
        "exp": int(expira.timestamp()),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET.get_secret_value(), algorithm="HS256"
    )


def decodificar_token(token: str) -> dict[str, Any]:
    """Decodifica y valida firma y expiración de un JWT. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(
        token, settings.JWT_SECRET.get_secret_value(), algorithms=["HS256"]
    )
