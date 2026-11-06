"""Rutas HTTP del módulo libros.

El router construye el Unit of Work con una dependencia (misma sesión de la
petición), se lo pasa al servicio sin abrirlo y traduce el IntegrityError a 409.

- router_abierto: catálogo público (listado y detalle).
- router_por_entidad: libros vigentes de una editorial, un género o un autor
  (públicos; viven acá porque los resuelve el repositorio de libros).
- router_admin: alta, PATCH, baja lógica, reposición y movimientos; main.py lo monta
  con requiere_rol("ADMIN") (CH-10). El usuario del movimiento sale de get_usuario_actual.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.dependencies import UsuarioActualDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.libros import service
from app.modules.libros.schemas import (
    LibroCreate,
    LibroDetalleRead,
    LibroRead,
    LibroUpdate,
    MovimientoRead,
    ReponerIn,
)
from app.modules.libros.unit_of_work import LibrosUnitOfWork


def get_uow(session: SessionDep) -> LibrosUnitOfWork:
    return LibrosUnitOfWork(session)


UowDep = Annotated[LibrosUnitOfWork, Depends(get_uow)]

router_abierto = APIRouter(prefix="/libros", tags=["libros"])
router_por_entidad = APIRouter(tags=["libros"])
router_admin = APIRouter(prefix="/libros", tags=["libros"])


@router_abierto.get("", response_model=Pagina[LibroRead])
async def listar(
    uow: UowDep,
    paginacion: PaginacionDep,
    titulo: str | None = Query(default=None, description="Parte del título, sin distinguir mayúsculas"),
    genero_id: int | None = Query(default=None),
):
    return await service.listar(uow, paginacion.page, paginacion.size, titulo, genero_id)


@router_abierto.get("/{libro_id}", response_model=LibroDetalleRead)
async def obtener(libro_id: int, uow: UowDep):
    return await service.obtener(uow, libro_id)


@router_por_entidad.get("/editoriales/{editorial_id}/libros", response_model=list[LibroRead])
async def libros_de_editorial(editorial_id: int, uow: UowDep):
    return await service.libros_de_editorial(uow, editorial_id)


@router_por_entidad.get("/generos/{genero_id}/libros", response_model=list[LibroRead])
async def libros_de_genero(genero_id: int, uow: UowDep):
    return await service.libros_de_genero(uow, genero_id)


@router_por_entidad.get("/autores/{autor_id}/libros", response_model=list[LibroRead])
async def libros_de_autor(autor_id: int, uow: UowDep):
    return await service.libros_de_autor(uow, autor_id)


@router_admin.patch("/{libro_id}", response_model=LibroDetalleRead)
async def actualizar(libro_id: int, datos: LibroUpdate, uow: UowDep):
    try:
        return await service.actualizar(uow, libro_id, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_admin.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dar_de_baja(libro_id: int, uow: UowDep):
    await service.dar_de_baja(uow, libro_id)


@router_admin.post("", response_model=LibroDetalleRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: LibroCreate, uow: UowDep, usuario: UsuarioActualDep):
    try:
        return await service.crear(uow, datos, usuario.id)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_admin.post("/{libro_id}/reponer", response_model=MovimientoRead)
async def reponer(libro_id: int, datos: ReponerIn, uow: UowDep, usuario: UsuarioActualDep):
    try:
        return await service.reponer(uow, libro_id, datos.cantidad, usuario.id)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_admin.get("/{libro_id}/movimientos", response_model=list[MovimientoRead])
async def movimientos(libro_id: int, uow: UowDep):
    return await service.movimientos(uow, libro_id)
