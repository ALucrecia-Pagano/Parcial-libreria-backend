"""Repositorio de autores: acceso a la tabla autor, sin confirmar nada.

Hereda de BaseRepository y le pasa la clase del modelo (consigna §6.4.3).
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.autores.models import Autor


class AutorRepository(BaseRepository[Autor]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Autor)
