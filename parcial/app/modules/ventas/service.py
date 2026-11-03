"""Lógica del módulo ventas y traducción de errores de la base."""

from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import VentaCreate


async def crear_venta(session: AsyncSession, venta_in: VentaCreate) -> Venta:
    libros_ids = [renglon.libro_id for renglon in venta_in.renglones]
    consulta = select(Libro).where(Libro.id.in_(libros_ids))
    resultado = await session.execute(consulta)
    libros_db = {libro.id: libro for libro in resultado.scalars().all()}
    if len(libros_db) != len(libros_ids):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uno o más libros solicitados no existen en el catálogo",
        )

    renglones_nuevos = []
    total_venta = Decimal("0")
    for renglon_in in venta_in.renglones:
        precio_real = libros_db[renglon_in.libro_id].precio
        renglones_nuevos.append(RenglonVenta(
            libro_id=renglon_in.libro_id,
            cantidad=renglon_in.cantidad,
            precio_unitario=precio_real,
        ))
        total_venta += precio_real * renglon_in.cantidad

    nueva_venta = Venta(
        cliente_id=venta_in.cliente_id,
        total=total_venta,
        renglones=renglones_nuevos,
    )
    session.add(nueva_venta)
    await _guardar(session, "No se pudo registrar la venta: el cliente no existe o los datos son inválidos")
    # Volvemos a consultar para devolver las relaciones cargadas después del commit.
    return await obtener_venta_por_id(session, nueva_venta.id)


async def obtener_ventas(session: AsyncSession, limit: int = 20, offset: int = 0) -> Sequence[Venta]:
    consulta = select(Venta).order_by(Venta.id).limit(limit).offset(offset)
    resultado = await session.execute(consulta)
    return resultado.scalars().all()


async def obtener_venta_por_id(session: AsyncSession, venta_id: int) -> Venta:
    consulta = (
        select(Venta).where(Venta.id == venta_id)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
        )
    )
    resultado = await session.execute(consulta)
    venta = resultado.scalars().first()
    if venta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return venta


async def _guardar(session: AsyncSession, mensaje_conflicto: str) -> None:
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=mensaje_conflicto
        ) from None
