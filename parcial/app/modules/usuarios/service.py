"""Lógica de negocio del módulo usuarios y autenticación (CH-07)."""

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import crear_token, verificar_password
from app.modules.usuarios.schemas import LoginIn, LoginOut
from app.modules.usuarios.unit_of_work import UsuariosUnitOfWork


class UsuariosService:
    async def login(
        self,
        uow: UsuariosUnitOfWork,
        datos: LoginIn,
        hash_ficticio: str,
    ) -> tuple[str, LoginOut]:
        """Autentica al usuario, mitiga enumeración con hash ficticio y emite token JWT."""
        # Punto de inserción para CH-09: límite de intentos fallidos antes de bcrypt.

        # 1. Búsqueda del usuario en su propio bloque UoW.
        # Al salir del bloque async with, la transacción de lectura finaliza y la conexión
        # se libera al pool antes de ejecutar bcrypt.
        async with uow:
            usuario = await uow.usuarios.get_by_email(datos.email)

        # 2. Anti-enumeración: si no existe, verificar contra hash ficticio (mismo tiempo).
        # Esta verificación corre sin ninguna conexión retenida en el pool.
        if usuario is None:
            await verificar_password(datos.password, hash_ficticio)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # 3. Verificación de hash con bcrypt fuera de la transacción para no retener el pool
        password_valida = await verificar_password(
            datos.password, usuario.password_hash
        )

        # 4. Usuario inactivo o contraseña errónea devuelven el mismo 401 unificado
        if not password_valida or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # 5. Obtener roles vigentes en un segundo bloque UoW
        async with uow:
            roles = await uow.asignaciones.roles_vigentes(usuario.id)

        # 6. Emitir JWT con roles vigentes al momento del login
        token = crear_token(sub=str(usuario.id), roles=roles)

        respuesta = LoginOut(
            mensaje="Sesión iniciada",
            debe_cambiar_password=usuario.debe_cambiar_password,
            expira_en_segundos=settings.JWT_MINUTOS * 60,
        )
        return token, respuesta
