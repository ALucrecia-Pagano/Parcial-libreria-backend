"""Unit of Work para el módulo de usuarios y seguridad."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.core.unit_of_work import UnitOfWork
from app.modules.clientes.models import Cliente
from app.modules.usuarios.repository import (
    AsignacionRolRepository,
    EventoSeguridadRepository,
    IntentoAccesoRepository,
    UsuarioRepository,
)


class UsuariosUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.asignaciones = AsignacionRolRepository(session)
        self.eventos = EventoSeguridadRepository(session)
        self.intentos = IntentoAccesoRepository(session)
        self.clientes = BaseRepository(session, Cliente)

