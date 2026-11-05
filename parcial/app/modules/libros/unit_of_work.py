"""Unit of Work del módulo libros.

Compone, con la MISMA sesión, el repositorio de libros y repositorios genéricos de
editorial, género y autor (solo para comprobar que existen en las lecturas de
«libros de X»). Confirmar, revertir y no cerrar la sesión lo hereda de la base.
CH-06 le agrega el repositorio de movimientos de stock.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.core.unit_of_work import UnitOfWork
from app.modules.autores.models import Autor
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.repository import LibroRepository


class LibrosUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.libros = LibroRepository(session)
        self.editoriales = BaseRepository(session, Editorial)
        self.generos = BaseRepository(session, Genero)
        self.autores = BaseRepository(session, Autor)
