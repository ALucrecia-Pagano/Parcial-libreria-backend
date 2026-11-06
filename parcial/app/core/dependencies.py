"""Dependencias de autenticación y autorización (CH-10).

- `get_usuario_actual`: lee exclusivamente la cookie HttpOnly `access_token`
  (Regla 18 de AGENTS.md, cátedra §5.3). Nunca lee la cabecera Authorization.
- `requiere_rol`: consulta roles vigentes en la base en cada petición (RN-04).
- `exigir_password_al_dia`: bloquea con 403 si debe cambiar contraseña (RN-06).
- Comparte la misma sesión `Depends(get_session)` con el Unit of Work (cátedra §6.7, Ejercicio 6).
"""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Request, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionDep, get_session
from app.core.security import decodificar_token
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repository import AsignacionRolRepository, UsuarioRepository


class UsuarioActual:
    """Contenedor de identidad: entidad Usuario de base de datos + roles declarados en el token."""

    def __init__(self, usuario: Usuario, roles_token: list[str]) -> None:
        self.usuario = usuario
        self.roles_token = roles_token

    @property
    def id(self) -> int:
        return self.usuario.id  # type: ignore[return-value]

    @property
    def email(self) -> str:
        return self.usuario.email

    @property
    def nombre(self) -> str:
        return self.usuario.nombre

    @property
    def activo(self) -> bool:
        return self.usuario.activo

    @property
    def debe_cambiar_password(self) -> bool:
        return self.usuario.debe_cambiar_password


async def get_usuario_actual(
    request: Request,
    session: SessionDep,
) -> UsuarioActual:
    """Extrae el usuario autenticado exclusivamente desde la cookie access_token.

    Responde 401 si no hay cookie, si el token es inválido o venció, o si el usuario no existe o está inactivo.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    try:
        payload = decodificar_token(token)
        usuario_id = int(payload.get("sub", 0))
        roles_token = list(payload.get("roles", []))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    repo = UsuarioRepository(session)
    usuario = await repo.get_by_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    return UsuarioActual(usuario=usuario, roles_token=roles_token)


UsuarioActualDep = Annotated[UsuarioActual, Depends(get_usuario_actual)]


async def roles_vigentes(session: AsyncSession, usuario_id: int) -> list[str]:
    """Consulta la tabla asignacion_rol para obtener los roles activos no vencidos."""
    repo = AsignacionRolRepository(session)
    return await repo.roles_vigentes(usuario_id)


def requiere_rol(*roles: str) -> Callable:
    """Fábrica de dependencias: 403 Forbidden si el usuario no posee ninguno de los roles vigentes en la BD."""

    async def _verificar_rol(
        usuario_actual: UsuarioActualDep,
        session: SessionDep,
    ) -> UsuarioActual:
        roles_en_base = await roles_vigentes(session, usuario_actual.id)
        if not any(r in roles_en_base for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Requiere uno de los siguientes roles: {list(roles)}",
            )
        return usuario_actual

    return _verificar_rol


async def exigir_password_al_dia(
    usuario_actual: UsuarioActualDep,
) -> UsuarioActual:
    """Control RN-06: 403 Forbidden si el usuario tiene pendiente el cambio de contraseña."""
    if usuario_actual.debe_cambiar_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe cambiar su contraseña antes de operar en el sistema",
        )
    return usuario_actual


PasswordAlDiaDep = Annotated[UsuarioActual, Depends(exigir_password_al_dia)]
