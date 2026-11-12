"""Registro atómico de una venta y lecturas de lo propio.

Un solo `async with` crea la venta, copia el precio de cada libro, descuenta
el stock con aplicar_movimiento y deja un movimiento por renglón. Si algo
falla, el Unit of Work revierte venta, renglones, stock y movimientos.
"""
from decimal import Decimal

from app.core.dependencies import roles_vigentes
from app.core.errores import Conflicto, NoEncontrado, Prohibido
from app.core.paginacion import Pagina, construir_pagina, validar_pagina
from app.modules.libros.stock import aplicar_movimiento
from app.modules.usuarios.models import Usuario
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import VentaCreate, VentaRead
from app.modules.ventas.unit_of_work import VentasUnitOfWork

_LIBRO_INVALIDO = "No se puede registrar la venta: el libro no existe o está dado de baja"
_CLIENTE_INVALIDO = "No se puede registrar la venta: el cliente no existe"


async def registrar(uow: VentasUnitOfWork, datos: VentaCreate, usuario_id: int) -> Venta:
    async with uow:
        cliente = await uow.clientes.get_by_id(datos.cliente_id)
        if cliente is None:
            raise Conflicto(_CLIENTE_INVALIDO)

        lineas = []
        for renglon in datos.renglones:
            libro = await uow.libros.get_by_id_including_deleted(renglon.libro_id)
            if libro is None or libro.borrado_en is not None:
                raise Conflicto(_LIBRO_INVALIDO)
            lineas.append((renglon, libro))

        venta = await uow.ventas.add(
            Venta(cliente_id=cliente.id, total=Decimal("0.00"))
        )
        total = Decimal("0.00")
        for renglon, libro in lineas:
            precio = libro.precio
            await uow.renglones.add(
                RenglonVenta(
                    venta_id=venta.id,
                    libro_id=libro.id,
                    cantidad=renglon.cantidad,
                    precio_unitario=precio,
                )
            )
            total += precio * renglon.cantidad
            await aplicar_movimiento(
                uow, libro, -renglon.cantidad, "Venta", usuario_id, venta.id
            )
        await uow.ventas.update(venta, {"total": total})
        detalle = await uow.ventas.obtener_detalle(venta.id)
        if detalle is None:
            raise NoEncontrado("Venta no encontrada")
        return detalle


async def listar(
    uow: VentasUnitOfWork, page: int, size: int, cliente_id: int | None = None
) -> Pagina[VentaRead]:
    async with uow:
        if cliente_id is not None:
            cliente = await uow.clientes.get_by_id(cliente_id)
            if cliente is None:
                raise NoEncontrado("Cliente no encontrado")
        return await _pagina(uow, page, size, cliente_id=cliente_id)


async def listar_propias(
    uow: VentasUnitOfWork, usuario_id: int, page: int, size: int
) -> Pagina[VentaRead]:
    async with uow:
        return await _pagina(uow, page, size, usuario_id=usuario_id)


async def obtener(uow: VentasUnitOfWork, venta_id: int, usuario: Usuario) -> Venta:
    """404 si no existe. 403 si no es personal ni el cliente dueño. Recién después, los datos."""
    async with uow:
        venta = await uow.ventas.obtener_detalle(venta_id)
        if venta is None:
            raise NoEncontrado("Venta no encontrada")
        roles = await roles_vigentes(uow.session, usuario.id)
        es_personal = any(rol in roles for rol in ("VENDEDOR", "ADMIN"))
        es_dueno = venta.cliente is not None and venta.cliente.usuario_id == usuario.id
        if not es_personal and not es_dueno:
            raise Prohibido("No tenés permiso para ver esta venta")
        return venta


async def _pagina(
    uow: VentasUnitOfWork,
    page: int,
    size: int,
    cliente_id: int | None = None,
    usuario_id: int | None = None,
) -> Pagina[VentaRead]:
    total = await uow.ventas.contar(cliente_id=cliente_id, usuario_id=usuario_id)
    validar_pagina(total, page, size)
    items = await uow.ventas.listar(
        offset=(page - 1) * size,
        limit=size,
        cliente_id=cliente_id,
        usuario_id=usuario_id,
    )
    return construir_pagina(
        [VentaRead.model_validate(venta) for venta in items], total, page, size
    )
