"""Unit of Work del módulo editoriales.

Compone los repositorios que necesitan las operaciones del módulo, todos con la
MISMA sesión: así todo lo que escriban queda en la misma transacción. Confirmar al
salir del bloque, revertir con excepción y no cerrar la sesión lo hereda de la base.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.modules.editoriales.repository import EditorialRepository


class EditorialesUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.editoriales = EditorialRepository(session)
