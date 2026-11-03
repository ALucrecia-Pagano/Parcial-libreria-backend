"""Rutas HTTP del módulo generos: reciben, delegan y declaran la respuesta."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead, GeneroUpdate

from app.modules.libros.schemas import LibroRead
from app.modules.libros.service import list_libros

router = APIRouter(prefix="/generos", tags=["generos"])


@router.post("/", response_model=GeneroRead, status_code=status.HTTP_201_CREATED)
async def create(data: GeneroCreate, session: AsyncSession = Depends(get_session)):
    return await service.create_genero(session, data)


@router.get("/", response_model=list[GeneroRead])
async def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await service.list_generos(session, limit, offset)


@router.get("/{genero_id}", response_model=GeneroRead)
async def get_one(genero_id: int, session: AsyncSession = Depends(get_session)):
    return await service.get_genero(session, genero_id)


@router.patch("/{genero_id}", response_model=GeneroRead)
async def update(
    genero_id: int,
    data: GeneroUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await service.update_genero(session, genero_id, data)


@router.delete("/{genero_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(genero_id: int, session: AsyncSession = Depends(get_session)):
    await service.delete_genero(session, genero_id)


@router.get("/{genero_id}/libros", response_model=list[LibroRead])
async def libros_del_genero(genero_id: int, limit: int = Query(20, ge=1, le=100),
                              offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)):
    await service.get_genero(session, genero_id)
    return await list_libros(session, limit, offset, genero_id=genero_id)
