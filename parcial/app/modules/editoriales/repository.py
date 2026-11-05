"""Repositorio de editoriales: acceso a la tabla editorial, sin confirmar nada.

Hereda de BaseRepository (editorial no tiene baja lógica). Le pasa la clase del
modelo al constructor porque el genérico T se borra en ejecución (consigna §6.4.3).
add y update solo hacen flush(): confirmar es tarea del Unit of Work.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.editoriales.models import Editorial


class EditorialRepository(BaseRepository[Editorial]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Editorial)
