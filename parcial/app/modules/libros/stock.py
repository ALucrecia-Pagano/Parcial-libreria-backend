"""Punto único de escritura del stock (CH-06, RN-11).

`aplicar_movimiento` es el ÚNICO código del proyecto que escribe `libro.stock`
(la única excepción es seed.py, que igual deja stock = suma de movimientos).
Cambia el stock y agrega la fila de movimiento_stock en la MISMA operación, así
que el invariante `libro.stock = SUM(movimiento_stock.cantidad)` no se puede romper
desde la aplicación: no hay otro camino para tocar el stock.

- Lo llaman el alta de libros («Stock inicial»), la reposición («Reposición») y,
  en CH-14, la venta («Venta», con cantidad negativa y venta_id).
- No confirma nada: corre dentro del `async with uow:` del servicio que lo llama.
- Si el stock quedara negativo, el flush choca con el CHECK ck_libro_stock_no_negativo
  y el IntegrityError revierte TODO (el Unit of Work no confirma a medias).
- Los movimientos nunca se editan ni se borran (RN-12): además de no haber código
  que lo haga, lo impide el disparador de la migración 4.
"""
from typing import Protocol

from app.modules.libros.models import Libro, MovimientoStock
from app.modules.libros.repository import MovimientoStockRepository


class UowDeMovimientos(Protocol):
    """Cualquier Unit of Work que escriba stock por el mismo repositorio de movimientos."""

    movimientos: MovimientoStockRepository


async def aplicar_movimiento(
    uow: UowDeMovimientos,
    libro: Libro,
    cantidad: int,
    motivo: str,
    usuario_id: int,
    venta_id: int | None = None,
) -> MovimientoStock:
    if cantidad == 0:
        # Un movimiento de 0 no existe (CHECK cantidad <> 0): quien llama decide no llamar.
        raise ValueError("Un movimiento de stock no puede ser de cantidad 0")
    libro.stock += cantidad
    movimiento = MovimientoStock(
        libro_id=libro.id,
        venta_id=venta_id,
        usuario_id=usuario_id,
        cantidad=cantidad,
        motivo=motivo,
    )
    # add() hace flush(): manda a la base el UPDATE del stock y el INSERT del movimiento juntos.
    return await uow.movimientos.add(movimiento)
