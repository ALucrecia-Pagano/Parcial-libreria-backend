# Proposal — CH-06 `stock-punto-unico-reponer-movimientos`

> **Governance: ALTO** (integridad del stock: un camino alternativo de escritura rompe el invariante). Dueño: Lucas Avila (Parte 2). Rama `CH-06-stock-punto-unico`, creada desde la de CH-05 (que ya incluye main con CH-10).

## Why

Después de CH-05, el alta de libros seguía siendo el legado del TP: aceptaba `stock` y lo escribía directo, sin movimiento (el rojo lo mostró: `POST /libros` con `"stock": 3` → 201 sin ningún `movimiento_stock`). No existían la reposición ni la consulta de movimientos. La consigna pide un único punto de escritura del stock, con su movimiento en la misma transacción, y el invariante `libro.stock = SUM(movimientos)` (RN-11).

## What Changes

- **Nuevo `libros/stock.py`**: `aplicar_movimiento(uow, libro, cantidad, motivo, usuario_id, venta_id=None)` suma la cantidad a `libro.stock` y agrega la fila de `movimiento_stock` en el mismo flush. Es el **único** código que escribe `libro.stock` (aparte de `seed.py`). CH-14 lo va a llamar para la venta.
- **`libros/repository.py`**: `MovimientoStockRepository` (solo agrega y lee; `update` y `delete` lanzan error, RN-12) con `listar_de_libro`.
- **`libros/unit_of_work.py`**: atributo `movimientos`.
- **`libros/schemas.py`**: `LibroCreate` con `stock_inicial` (≥ 0), `extra="forbid"` y al menos un autor; `ReponerIn` (`cantidad > 0`); `MovimientoRead`.
- **`libros/service.py`**: `crear` (libro con stock 0 + autorías + movimiento «Stock inicial» si `stock_inicial > 0`, todo en un `async with uow:`), `reponer` (404 si no existe, 409 si está dado de baja), `movimientos`. Se elimina el alta legada.
- **`libros/router.py`** (`router_admin`, montado con `requiere_rol("ADMIN")` por CH-10): `POST /libros` → 201, 409, 422; `POST /libros/{id}/reponer` → 200, 404, 409, 422; `GET /libros/{id}/movimientos` → 200, 404. El `usuario_id` sale de `get_usuario_actual` (`UsuarioActualDep`).
- **`.http` de CH-04 y C-16**: suman el login de ADMIN, porque desde CH-10 las escrituras piden sesión (sin cambiar lo que prueban).
- `main.py` no cambia: el de CH-10 ya monta `router_admin` con la guarda de ADMIN.

**No entra**: la venta (CH-14 llama a `aplicar_movimiento`), detalle sin N+1 (CH-15).

## Capabilities

### New Capabilities
- `stock-libros`: alta con stock inicial, reposición y consulta de movimientos, con un único punto de escritura del stock y el invariante stock = suma de movimientos.

## Impact

- **Crear (2)**: `parcial/app/modules/libros/stock.py`, `parcial/test/C-13_baja_reposicion_isbn.http`.
- **Modificar (7)**: `libros/repository.py`, `unit_of_work.py`, `service.py`, `router.py`, `schemas.py`; `parcial/test/CH-04_editoriales_generos_autores.http`, `parcial/test/C-16_busqueda_paginacion_patch.http`.
- **Reglas**: RN-11, RN-12, RN-13, RN-01.
- **Casos**: **C-13** completo.
