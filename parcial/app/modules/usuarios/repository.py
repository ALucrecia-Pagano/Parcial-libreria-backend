"""Repositorios para el módulo de usuarios y seguridad."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.repository import BaseRepository
from app.modules.usuarios.models import (
    AsignacionRol,
    EventoSeguridad,
    IntentoAcceso,
    Usuario,
)


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Usuario)

    async def get_by_email(self, email: str) -> Usuario | None:
        """Busca un usuario por su email único."""
        consulta = select(Usuario).where(Usuario.email == email)
        return (await self.session.scalars(consulta)).first()


class AsignacionRolRepository(BaseRepository[AsignacionRol]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AsignacionRol)

    async def roles_vigentes(self, usuario_id: int) -> list[str]:
        """Devuelve los roles activos y no vencidos de un usuario."""
        ahora = datetime.now(timezone.utc)
        consulta = (
            select(AsignacionRol.rol)
            .where(
                AsignacionRol.usuario_id == usuario_id,
                AsignacionRol.revocada_en.is_(None),
                (AsignacionRol.vence_en.is_(None) | (AsignacionRol.vence_en > ahora)),
            )
        )
        return list((await self.session.scalars(consulta)).all())


class EventoSeguridadRepository(BaseRepository[EventoSeguridad]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, EventoSeguridad)


class IntentoAccesoRepository(BaseRepository[IntentoAcceso]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, IntentoAcceso)

    async def obtener_fallos_recientes(
        self, email: str, ip: str, ventana_segundos: int = 60
    ) -> list[IntentoAcceso]:
        """Consulta los intentos fallidos en los últimos 60 segundos posteriores al último éxito."""
        ahora = datetime.now(timezone.utc)
        desde_ventana = ahora - timedelta(seconds=ventana_segundos)

        # 1. Buscar la fecha del último login exitoso para este (email, ip)
        consulta_ultimo_exito = (
            select(func.max(IntentoAcceso.cuando))
            .where(
                IntentoAcceso.email == email,
                IntentoAcceso.ip == ip,
                IntentoAcceso.exito.is_(True),
            )
        )
        ultimo_exito = await self.session.scalar(consulta_ultimo_exito)

        # 2. Filtrar fallos en la ventana de tiempo y posteriores al último éxito
        condiciones = [
            IntentoAcceso.email == email,
            IntentoAcceso.ip == ip,
            IntentoAcceso.exito.is_(False),
            IntentoAcceso.cuando >= desde_ventana,
        ]
        if ultimo_exito is not None:
            condiciones.append(IntentoAcceso.cuando > ultimo_exito)

        consulta_fallos = (
            select(IntentoAcceso)
            .where(*condiciones)
            .order_by(IntentoAcceso.cuando.asc())
        )
        return list((await self.session.scalars(consulta_fallos)).all())

    async def verificar_limite_intentos(
        self, email: str, ip: str, limite: int = 5, ventana_segundos: int = 60
    ) -> tuple[bool, int]:
        """Devuelve (bloqueado, segundos_restantes).
        Si bloqueado es True, segundos_restantes indica el valor de Retry-After."""
        fallos = await self.obtener_fallos_recientes(email, ip, ventana_segundos)
        if len(fallos) >= limite:
            ahora = datetime.now(timezone.utc)
            segundos_pasados = (ahora - fallos[0].cuando).total_seconds()
            retry_after = max(1, int(ventana_segundos - segundos_pasados))
            return True, retry_after
        return False, 0


async def registrar_intento(
    session_factory: async_sessionmaker[AsyncSession],
    email: str,
    ip: str,
    exito: bool,
) -> None:
    """Registra un intento de acceso en una sesión y transacción independiente.

    (1) Qué hace distinto: Abre su propia AsyncSession y confirma inmediatamente
        mediante commit, sin utilizar el Unit of Work ni la sesión de la petición.
    (2) Por qué no puede compartir la transacción: Si compartiera la transacción
        de la petición, cuando un intento de login falla y se lanza un error HTTP 401,
        la transacción principal se revierte (rollback) y la fila del intento fallido
        se perdería, impidiendo contar los fallos acumulados para el límite de tasa.
    (3) Su costo: Genera una conexión transaccional adicional al pool de conexiones y
        persiste filas en la tabla intento_acceso incluso si la petición termina en error.
    """
    async with session_factory() as session:
        intento = IntentoAcceso(email=email, ip=ip, exito=exito)
        session.add(intento)
        await session.commit()
