# Proposal — CH-14 `venta-rn10-mis-ventas-dueno`

> **Governance: ALTO** (dinero y stock). Dueño: Juan García (Parte 5). Depende de CH-06 y CH-10, ya en `main`.

## Why

Registrar una venta en el TP descontaba el stock a mano, dentro de un `commit()` del servicio, y no distinguía la venta propia de la ajena. La consigna pide una sola transacción (RN-10), el punto único de stock (RN-11) y que un cliente vea solo lo suyo (RN-14).

## What Changes

- `POST /ventas` en un solo Unit of Work: copia el precio, calcula el total, descuenta el stock con `aplicar_movimiento` (cantidad negativa, motivo «Venta», `venta_id`) y deja un movimiento por renglón.
- Si no hay stock, el CHECK revierte venta, renglones, descuentos y movimientos (409). Cliente o libro inexistente, o libro dado de baja: 409, sin escrituras.
- El cuerpo no acepta precio, total ni fecha (`extra="forbid"`). Sin renglones o con un libro repetido: 422. No hay PATCH ni DELETE de ventas.
- `GET /ventas` y `GET /clientes/{id}/ventas` para VENDEDOR o ADMIN, con envoltorio de página.
- `GET /ventas/{id}` sin `requiere_rol`: 200 si es personal o el dueño, 403 si no, 404 si no existe.
- `GET /mis-ventas` para cualquier sesión, solo las ventas de su ficha.
- El aviso del comprobante se agenda recién después de confirmar.

## Capabilities

### New Capabilities

- `ventas`: alta atómica de una venta y lecturas de lo propio.

### Modified Capabilities

- *(Ninguna. El punto único de stock sigue siendo el de `stock-libros`; esta capacidad lo usa.)*

## Impact

- Crear: `parcial/app/modules/ventas/repository.py`, `unit_of_work.py`, `parcial/test/C-10_venta_valida.http`, `C-11_venta_sin_stock.http`, `C-12_venta_referencias_invalidas.http`.
- Modificar: `service.py`, `router.py`, `schemas.py`, `parcial/test/C-06_401_vs_403.http`.
- `aplicar_movimiento` acepta cualquier Unit of Work que tenga `movimientos`, para que la venta lo llame sin abrir otra transacción.
