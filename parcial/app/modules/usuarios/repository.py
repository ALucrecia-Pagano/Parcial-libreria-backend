"""Repositorios para el módulo de usuarios y seguridad."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.usuarios.models import AsignacionRol, EventoSeguridad, Usuario


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
