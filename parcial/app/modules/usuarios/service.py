"""Lógica de negocio del módulo usuarios y autenticación (CH-07 y CH-09)."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import crear_token, verificar_password
from app.modules.usuarios.repository import registrar_intento
from app.modules.usuarios.schemas import LoginIn, LoginOut
from app.modules.usuarios.unit_of_work import UsuariosUnitOfWork


class UsuariosService:
    async def login(
        self,
        uow: UsuariosUnitOfWork,
        datos: LoginIn,
        hash_ficticio: str,
        ip: str,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> tuple[str, LoginOut]:
        """Autentica al usuario aplicando limitación de tasa (429) y auditoría en intento_acceso."""
        # 1. Límite de intentos: evaluar antes de tocar bcrypt (RN-07).
        # Cuenta los fallos en los últimos 60s desde el último éxito.
        bloqueado, retry_after = await uow.intentos.verificar_limite_intentos(
            datos.email, ip
        )
        if bloqueado:
            # El intento rechazado por 429 NO se registra (P-14) y responde sin consumir CPU.
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Intente más tarde.",
                headers={"Retry-After": str(retry_after)},
            )

        # 2. Búsqueda del usuario en su propio bloque UoW.
        # Libera la conexión al pool antes de ejecutar bcrypt.
        async with uow:
            usuario = await uow.usuarios.get_by_email(datos.email)

        # 3. Anti-enumeración: usuario inexistente
        if usuario is None:
            await registrar_intento(session_factory, datos.email, ip, exito=False)
            await verificar_password(datos.password, hash_ficticio)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # 4. Verificación de hash con bcrypt fuera de transacción
        password_valida = await verificar_password(
            datos.password, usuario.password_hash
        )

        # 5. Usuario inactivo o contraseña errónea devuelven el mismo 401 unificado
        if not password_valida or not usuario.activo:
            await registrar_intento(session_factory, datos.email, ip, exito=False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # 6. Autenticación exitosa: registrar éxito en sesión propia (reinicia la ventana)
        await registrar_intento(session_factory, datos.email, ip, exito=True)

        # 7. Obtener roles vigentes en un segundo bloque UoW
        async with uow:
            roles = await uow.asignaciones.roles_vigentes(usuario.id)

        # 8. Emitir JWT con roles vigentes
        token = crear_token(sub=str(usuario.id), roles=roles)

        respuesta = LoginOut(
            mensaje="Sesión iniciada",
            debe_cambiar_password=usuario.debe_cambiar_password,
            expira_en_segundos=settings.JWT_MINUTOS * 60,
        )
        return token, respuesta
