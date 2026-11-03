"""Rutas HTTP del módulo ventas."""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.ventas import service
from app.modules.ventas.tasks import avisar_comprobante
from app.modules.ventas.schemas import VentaCreate, VentaRead, VentaDetalleRead

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post("/", response_model=VentaDetalleRead, status_code=status.HTTP_201_CREATED)
async def registrar_venta(venta_in: VentaCreate, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    venta = await service.crear_venta(session, venta_in)
    background_tasks.add_task(avisar_comprobante, venta.id, venta.cliente.email)
    return venta


@router.get("/", response_model=list[VentaRead])
async def leer_ventas(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await service.obtener_ventas(session, limit, offset)


@router.get("/{venta_id}", response_model=VentaDetalleRead)
async def leer_venta_detalle(venta_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_venta_por_id(session, venta_id)
