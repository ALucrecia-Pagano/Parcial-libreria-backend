"""Lógica de negocio del módulo usuarios y autenticación (CH-07, CH-08, CH-09, CH-10, CH-11 y CH-12)."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.dependencies import UsuarioActual
from app.core.errores import Conflicto, DemasiadosIntentos, NoAutenticado, NoEncontrado
from app.core.paginacion import Pagina, ParamsPaginacion, validar_pagina
from app.core.security import crear_token, hashear_password, verificar_password
from app.modules.clientes.models import Cliente
from app.modules.usuarios.models import AsignacionRol, EventoSeguridad, Usuario
from app.modules.usuarios.repository import registrar_intento
from app.modules.usuarios.schemas import (
    AsignacionRolCreateIn,
    AsignacionRolOut,
    CambiarPasswordIn,
    CambiarPasswordOut,
    EventoSeguridadOut,
    LoginIn,
    LoginOut,
    MensajeOut,
    RegistroIn,
    RegistroOut,
    UsuarioAdminOut,
    UsuarioCreateAdminIn,
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
                raise NoAutenticado("Usuario no encontrado o inactivo")
            roles_base = await uow.asignaciones.roles_vigentes(usuario.id)

        return UsuarioYoOut(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            activo=usuario.activo,
            debe_cambiar_password=usuario.debe_cambiar_password,
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
            raise DemasiadosIntentos(
                "Demasiados intentos fallidos. Intente más tarde.",
                retry_after=retry_after,
            )

        # 2. Búsqueda del usuario en su propio bloque UoW.
        # Libera la conexión al pool antes de ejecutar bcrypt.
        async with uow:
            usuario = await uow.usuarios.get_by_email(datos.email)

        # 3. Anti-enumeración: usuario inexistente
        if usuario is None:
            await registrar_intento(session_factory, datos.email, ip, exito=False)
            await verificar_password(datos.password, hash_ficticio)
            raise NoAutenticado("Credenciales inválidas")

        # 4. Verificación de hash con bcrypt fuera de transacción
        password_valida = await verificar_password(
            datos.password, usuario.password_hash
        )

        # 5. Usuario inactivo o contraseña errónea devuelven el mismo 401 unificado
        if not password_valida or not usuario.activo:
            await registrar_intento(session_factory, datos.email, ip, exito=False)
            raise NoAutenticado("Credenciales inválidas")

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

    async def cambiar_password(
        self,
        uow: UsuariosUnitOfWork,
        usuario_actual: UsuarioActual,
        datos: CambiarPasswordIn,
    ) -> CambiarPasswordOut:
        """Cambia la contraseña del usuario autenticado, registrando auditoría en evento_seguridad (RN-16, DD-30)."""
        # 1. Verificación previa fuera de la transacción (cátedra §5.6, §6.7)
        password_valida = await verificar_password(
            datos.password_actual, usuario_actual.usuario.password_hash
        )
        if not password_valida:
            raise NoAutenticado("Contraseña actual incorrecta")

        # 2. Hash previo fuera de la transacción
        nuevo_hash = await hashear_password(datos.password_nueva)

        # 3. Un solo bloque async with uow: (RN-16)
        async with uow:
            usuario = await uow.usuarios.get_by_id(usuario_actual.id)
            if usuario is None or not usuario.activo:
                raise NoAutenticado("Usuario no encontrado o inactivo")
            usuario.password_hash = nuevo_hash
            usuario.debe_cambiar_password = False
            await uow.usuarios.add(usuario)

            evento = EventoSeguridad(
                actor=usuario.email,
                accion="Cambio de contraseña",
            )
            await uow.eventos.add(evento)

        return CambiarPasswordOut(mensaje="Contraseña actualizada correctamente")

    async def alta_personal(
        self,
        uow: UsuariosUnitOfWork,
        admin: UsuarioActual,
        datos: UsuarioCreateAdminIn,
    ) -> UsuarioAdminOut:
        """Da de alta un usuario de personal con contraseña provisoria y rol inicial (RN-06, RN-16)."""
        # 1. Hashear contraseña provisoria fuera de la transacción (cátedra §5.6)
        password_hash = await hashear_password(datos.password)

        # 2. Un solo bloque async with uow: (RN-16)
        async with uow:
            usuario = Usuario(
                email=datos.email,
                nombre=datos.nombre,
                password_hash=password_hash,
                activo=True,
                debe_cambiar_password=True,
            )
            await uow.usuarios.add(usuario)
            await uow.session.flush()

            asignacion = AsignacionRol(
                usuario_id=usuario.id,
                rol=datos.rol,
                otorgada_por=admin.id,
            )
            await uow.asignaciones.add(asignacion)

            evento = EventoSeguridad(
                actor=admin.email,
                accion="Alta de personal",
            )
            await uow.eventos.add(evento)

        return UsuarioAdminOut.model_validate(usuario)

    async def listar_roles(
        self,
        uow: UsuariosUnitOfWork,
        usuario_id: int,
    ) -> list[AsignacionRolOut]:
        """Devuelve el historial completo de asignaciones de un usuario (activas, vencidas y revocadas)."""
        async with uow:
            usuario = await uow.usuarios.get_by_id(usuario_id)
            if usuario is None:
                raise NoEncontrado("Usuario no encontrado")
            asignaciones = await uow.asignaciones.obtener_asignaciones(usuario_id)
            return [AsignacionRolOut.model_validate(a) for a in asignaciones]

    async def asignar_rol(
        self,
        uow: UsuariosUnitOfWork,
        admin: UsuarioActual,
        usuario_id: int,
        datos: AsignacionRolCreateIn,
    ) -> AsignacionRolOut:
        """Asigna un rol con vigencia opcional a un usuario, cerrando asignaciones vencidas previas (RN-03, RN-16)."""
        ahora = datetime.now(timezone.utc)
        async with uow:
            usuario = await uow.usuarios.get_by_id(usuario_id)
            if usuario is None:
                raise NoEncontrado("Usuario no encontrado")

            # Verificar si existe una asignación abierta (revocada_en IS NULL)
            abierta = await uow.asignaciones.obtener_abierta(usuario_id, datos.rol)
            if abierta is not None:
                # Si sigue vigente (no venció), conflicto RN-03
                if abierta.vence_en is None or abierta.vence_en > ahora:
                    raise Conflicto("El usuario ya tiene ese rol activo asignado")
                # Si ya venció, se cierra en el mismo UoW
                abierta.revocada_en = ahora
                await uow.session.flush()

            nueva = AsignacionRol(
                usuario_id=usuario_id,
                rol=datos.rol,
                vence_en=datos.vence_en,
                otorgada_por=admin.id,
            )
            await uow.asignaciones.add(nueva)
            await uow.session.flush()

            evento = EventoSeguridad(
                actor=admin.email,
                accion=f"Asignación de rol {datos.rol}",
            )
            await uow.eventos.add(evento)

        return AsignacionRolOut.model_validate(nueva)

    async def revocar_rol(
        self,
        uow: UsuariosUnitOfWork,
        admin: UsuarioActual,
        usuario_id: int,
        rol: str,
    ) -> MensajeOut:
        """Revoca un rol activo a un usuario aplicando reglas de autoprotección (RN-05, RN-16)."""
        ahora = datetime.now(timezone.utc)
        async with uow:
            usuario = await uow.usuarios.get_by_id(usuario_id)
            if usuario is None:
                raise NoEncontrado("Usuario no encontrado")

            # Buscar la asignación abierta y vigente
            asignacion = await uow.asignaciones.obtener_abierta(usuario_id, rol)
            if asignacion is None or (
                asignacion.vence_en is not None and asignacion.vence_en <= ahora
            ):
                raise NoEncontrado(
                    f"El usuario no tiene una asignación activa del rol {rol}"
                )

            # RN-05: Autoprotección
            if rol == "ADMIN":
                admins_vigentes = await uow.asignaciones.contar_admins_vigentes()
                if admins_vigentes <= 1:
                    raise Conflicto(
                        "No se puede revocar el rol: no pueden quedar cero administradores vigentes en el sistema"
                    )
                if usuario_id == admin.id:
                    raise Conflicto(
                        "Un administrador no puede revocarse su propio rol ADMIN"
                    )

            # Marcar revocación sin borrar la fila física
            asignacion.revocada_en = ahora
            await uow.asignaciones.add(asignacion)

            evento = EventoSeguridad(
                actor=admin.email,
                accion=f"Revocación de rol {rol}",
            )
            await uow.eventos.add(evento)

        return MensajeOut(mensaje="Rol revocado correctamente")

    async def listar_eventos(
        self,
        uow: UsuariosUnitOfWork,
        params: ParamsPaginacion,
    ) -> Pagina[EventoSeguridadOut]:
        """Consulta paginada del historial de auditoría de seguridad ordenada de más recientes a más antiguos."""
        async with uow:
            total = await uow.eventos.contar()
            pages = validar_pagina(total, params.page, params.size)
            items = await uow.eventos.listar_recientes(params.offset, params.size)
            return Pagina(
                items=[EventoSeguridadOut.model_validate(e) for e in items],
                total=total,
                page=params.page,
                size=params.size,
                pages=pages,
            )

