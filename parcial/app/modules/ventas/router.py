"""Rutas de ventas.

router_staff pide VENDEDOR o ADMIN (lo monta main.py).
router_protegido solo pide sesión: el detalle decide si quien mira es personal o el dueño.
El aviso del comprobante se agenda después de que el servicio confirmó la venta.
"""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.dependencies import UsuarioActualDep
from app.core.errores import traducir_integrity_error
from app.core.paginacion import Pagina, PaginacionDep
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, VentaDetalleRead, VentaRead
from app.modules.ventas.tasks import avisar_comprobante
from app.modules.ventas.unit_of_work import VentasUnitOfWork


def get_uow(session: SessionDep) -> VentasUnitOfWork:
    return VentasUnitOfWork(session)


UowDep = Annotated[VentasUnitOfWork, Depends(get_uow)]

router_staff = APIRouter(tags=["ventas"])
router_protegido = APIRouter(tags=["ventas"])


@router_staff.post("/ventas", response_model=VentaDetalleRead, status_code=status.HTTP_201_CREATED)
async def registrar(
    datos: VentaCreate,
    background_tasks: BackgroundTasks,
    usuario: UsuarioActualDep,
    uow: UowDep,
):
    try:
        venta = await service.registrar(uow, datos, usuario.id)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None
    background_tasks.add_task(avisar_comprobante, venta.id, venta.cliente.email)
    return venta


@router_staff.get("/ventas", response_model=Pagina[VentaRead])
async def listar(uow: UowDep, paginacion: PaginacionDep):
    return await service.listar(uow, paginacion.page, paginacion.size)


@router_staff.get("/clientes/{cliente_id}/ventas", response_model=Pagina[VentaRead])
async def listar_de_cliente(cliente_id: int, uow: UowDep, paginacion: PaginacionDep):
    return await service.listar(uow, paginacion.page, paginacion.size, cliente_id)


@router_protegido.get("/mis-ventas", response_model=Pagina[VentaRead])
async def listar_propias(usuario: UsuarioActualDep, uow: UowDep, paginacion: PaginacionDep):
    return await service.listar_propias(uow, usuario.id, paginacion.page, paginacion.size)


@router_protegido.get("/ventas/{venta_id}", response_model=VentaDetalleRead)
async def obtener(venta_id: int, usuario: UsuarioActualDep, uow: UowDep):
    return await service.obtener(uow, venta_id, usuario.usuario)
