"""Repositorios del módulo libros.

LibroRepository hereda de SoftDeleteRepository: las lecturas normales ocultan los
libros dados de baja (RN-13) y la baja es lógica (soft_delete pone borrado_en).
Cada método se nombra por lo que trae y declara adentro su precarga, para que
ninguna lectura dependa de la carga perezosa (consigna §6.5).

La búsqueda por título usa parámetros ligados (icontains → ILIKE con el valor
como parámetro y los comodines escapados): ' OR '1'='1 se busca como texto.
"""
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.repository import SoftDeleteRepository
from app.modules.libros.models import Libro, LibroAutor


class LibroRepository(SoftDeleteRepository[Libro]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Libro)

    @staticmethod
    def _filtros_catalogo(titulo: str | None, genero_id: int | None) -> list:
        filtros = [Libro.borrado_en.is_(None)]
        if titulo is not None:
            filtros.append(Libro.titulo.icontains(titulo, autoescape=True))
        if genero_id is not None:
            filtros.append(Libro.genero_id == genero_id)
        return filtros

    async def contar_catalogo(self, titulo: str | None = None, genero_id: int | None = None) -> int:
        """Total con los MISMOS filtros que listar_catalogo."""
        consulta = (
            select(func.count())
            .select_from(Libro)
            .where(*self._filtros_catalogo(titulo, genero_id))
        )
        return await self.session.scalar(consulta)

    async def listar_catalogo(
        self, offset: int, limit: int, titulo: str | None = None, genero_id: int | None = None
    ) -> Sequence[Libro]:
        """Libros vigentes de una página, con editorial y género precargados."""
        consulta = (
            select(Libro)
            .where(*self._filtros_catalogo(titulo, genero_id))
            .options(joinedload(Libro.editorial), joinedload(Libro.genero))
            .order_by(Libro.id)
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.scalars(consulta)).all()

    async def obtener_detalle(self, libro_id: int) -> Libro | None:
        """Libro vigente con editorial, género y autores (en orden) precargados."""
        consulta = (
            select(Libro)
            .where(Libro.id == libro_id, Libro.borrado_en.is_(None))
            .options(
                joinedload(Libro.editorial),
                joinedload(Libro.genero),
                selectinload(Libro.autorias).joinedload(LibroAutor.autor),
            )
            # Relee aunque el libro ya esté en la sesión (por ejemplo, después de un PATCH).
            .execution_options(populate_existing=True)
        )
        libro = await self.session.scalar(consulta)
        if libro is not None:
            libro.autorias.sort(key=lambda autoria: (autoria.orden, autoria.autor_id))
        return libro

    async def listar_vigentes_de_editorial(self, editorial_id: int) -> Sequence[Libro]:
        return await self._listar_vigentes(Libro.editorial_id == editorial_id)

    async def listar_vigentes_de_genero(self, genero_id: int) -> Sequence[Libro]:
        return await self._listar_vigentes(Libro.genero_id == genero_id)

    async def listar_vigentes_de_autor(self, autor_id: int) -> Sequence[Libro]:
        consulta = (
            select(Libro)
            .join(LibroAutor, LibroAutor.libro_id == Libro.id)
            .where(LibroAutor.autor_id == autor_id, Libro.borrado_en.is_(None))
            .options(joinedload(Libro.editorial), joinedload(Libro.genero))
            .order_by(Libro.id)
        )
        return (await self.session.scalars(consulta)).all()

    async def _listar_vigentes(self, condicion) -> Sequence[Libro]:
        consulta = (
            select(Libro)
            .where(condicion, Libro.borrado_en.is_(None))
            .options(joinedload(Libro.editorial), joinedload(Libro.genero))
            .order_by(Libro.id)
        )
        return (await self.session.scalars(consulta)).all()
