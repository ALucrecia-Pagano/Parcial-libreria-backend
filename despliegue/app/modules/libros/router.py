"""Router del módulo libros."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.libros.schemas import LibroCreate, LibroRead, LibroDetalleRead, LibroUpdate
from app.modules.libros import service

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/", response_model=list[LibroRead])
async def list_all(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                   titulo: str | None = None, genero_id: int | None = None,
                   session: AsyncSession = Depends(get_session)):
    return await service.list_libros(session, limit, offset, titulo, genero_id)


@router.get("/{libro_id}", response_model=LibroDetalleRead)
async def get_one(libro_id: int, session: AsyncSession = Depends(get_session)):
    libro = await service.get_libro(session, libro_id)
    return libro


@router.post("/", response_model=LibroDetalleRead, status_code=status.HTTP_201_CREATED)
async def create(data: LibroCreate, session: AsyncSession = Depends(get_session)):
    return await service.create_libro(session, data)


@router.patch("/{libro_id}", response_model=LibroDetalleRead)
async def update(
    libro_id: int,
    data: LibroUpdate,
    session: AsyncSession = Depends(get_session),
):
    libro = await service.get_libro(session, libro_id)
    return await service.update_libro(session, libro, data)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(libro_id: int, session: AsyncSession = Depends(get_session)):
    libro = await service.get_libro(session, libro_id)
    await service.delete_libro(session, libro)
