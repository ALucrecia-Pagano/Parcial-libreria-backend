"""Repositorio de géneros: acceso a la tabla genero, sin confirmar nada.

Hereda de BaseRepository (genero no tiene baja lógica) y le pasa la clase del
modelo, porque el genérico T se borra en ejecución (consigna §6.4.3).
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.generos.models import Genero


class GeneroRepository(BaseRepository[Genero]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Genero)
