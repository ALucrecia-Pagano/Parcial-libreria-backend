"""Paginación de colecciones: envoltorio {items, total, page, size, pages} (RN-14).

Orden de uso en un servicio, para no consultar los ítems de una página que no
existe (D10):
    total = await repo.count()
    validar_pagina(total, params.page, params.size)
    items = await repo.get_all(offset=params.offset, limit=params.size)
    return construir_pagina(items, total, params.page, params.size)

El total tiene que respetar los mismos filtros que la consulta de los ítems.
"""
from collections.abc import Sequence
from math import ceil
from typing import Annotated, Generic, TypeVar

from fastapi import Depends, HTTPException, Query
from sqlmodel import SQLModel

T = TypeVar("T")


class Pagina(SQLModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class ParamsPaginacion:
    """Parámetros de consulta: fuera de rango, FastAPI responde 422 solo."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Número de página (arranca en 1)"),
        size: int = Query(default=20, ge=1, le=100, description="Tamaño de página (1..100)"),
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


PaginacionDep = Annotated[ParamsPaginacion, Depends()]


def calcular_paginas(total: int, size: int) -> int:
    """Una colección vacía tiene una página, vacía."""
    return max(1, ceil(total / size))


def validar_pagina(total: int, page: int, size: int) -> int:
    """Devuelve la cantidad de páginas, o 422 si la pedida no existe."""
    pages = calcular_paginas(total, size)
    if page > pages:
        raise HTTPException(
            status_code=422,
            detail=f"La página {page} no existe: hay {pages}",
        )
    return pages


def construir_pagina(items: Sequence[T], total: int, page: int, size: int) -> Pagina[T]:
    pages = validar_pagina(total=total, page=page, size=size)
    return Pagina(items=list(items), total=total, page=page, size=size, pages=pages)
