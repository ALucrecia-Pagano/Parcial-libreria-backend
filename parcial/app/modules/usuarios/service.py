"""Lógica de negocio del módulo usuarios y autenticación (CH-07, CH-08 y CH-09)."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import crear_token, hashear_password, verificar_password
from app.modules.clientes.models import Cliente
from app.modules.usuarios.models import AsignacionRol, Usuario
from app.modules.usuarios.repository import registrar_intento
from app.modules.usuarios.schemas import (
    LoginIn,
    LoginOut,
    RegistroIn,
    RegistroOut,
    UsuarioYoOut,
)
from app.modules.usuarios.unit_of_work import UsuariosUnitOfWork


class UsuariosService:
    async def registrar_cliente(
        self,
        uow: UsuariosUnitOfWork,
        datos: RegistroIn,
    ) -> RegistroOut:
        """Registra un nuevo cliente de forma atómica: usuario + rol CLIENTE + ficha de cliente (RN-02).

        Calcula el hash de la contraseña ANTES de abrir la transacción para no retener
        conexiones del pool mientras corre bcrypt.
        """
        password_hash = await hashear_password(datos.password)

        async with uow:
            nuevo_usuario = Usuario(
                email=datos.email,
                nombre=datos.nombre,
                password_hash=password_hash,
                activo=True,
                debe_cambiar_password=False,
            )
            await uow.usuarios.add(nuevo_usuario)

            nueva_asignacion = AsignacionRol(
                usuario_id=nuevo_usuario.id,
                rol="CLIENTE",
                otorgada_por=None,
            )
            await uow.asignaciones.add(nueva_asignacion)

            nuevo_cliente = Cliente(
                nombre=datos.nombre,
                email=datos.email,
                usuario_id=nuevo_usuario.id,
            )
            await uow.clientes.add(nuevo_cliente)

        return RegistroOut(
            id=nuevo_usuario.id,
            nombre=nuevo_usuario.nombre,
            email=nuevo_usuario.email,
            cliente_id=nuevo_cliente.id,
            mensaje="Registro completado exitosamente",
        )

    async def obtener_yo(
        self,
        uow: UsuariosUnitOfWork,
        usuario_id: int,
        roles_token: list[str],
    ) -> UsuarioYoOut:
        """Obtiene la información del usuario autenticado, roles vigentes en BD y roles en el token."""
        async with uow:
            usuario = await uow.usuarios.get_by_id(usuario_id)
            if usuario is None or not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado o inactivo",
                )
            roles_base = await uow.asignaciones.roles_vigentes(usuario.id)

        return UsuarioYoOut(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            activo=usuario.activo,
            roles_base=roles_base,
            roles_token=roles_token,
        )

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
