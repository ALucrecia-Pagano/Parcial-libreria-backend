"""Unit of Work base: marca el límite de la transacción con `async with`.

Salir del bloque sin errores confirma; salir con una excepción revierte y la
deja seguir su camino. No hay tercera opción.

Reparto de responsabilidades (D9, consigna pág. 9):
- get_session crea y cierra la sesión.
- El router construye el UnitOfWork y traduce los errores a HTTP.
- El servicio recibe el UnitOfWork y lo abre.
- El UnitOfWork confirma o revierte, y nada más: no cierra la sesión porque no
  la creó, y no sabe nada de HTTP.

Cada módulo hereda de esta clase y crea sus repositorios con la misma sesión,
para que todo lo que escriban quede en la misma transacción.
"""
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
