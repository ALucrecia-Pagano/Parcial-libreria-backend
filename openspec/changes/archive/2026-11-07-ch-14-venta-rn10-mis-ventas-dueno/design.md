# Design — CH-14 `venta-rn10-mis-ventas-dueno`

## Context

Ver `proposal.md` y `specs/ventas/spec.md`. `aplicar_movimiento` ya es el único escritor de `libro.stock`. El CHECK `ck_libro_stock_no_negativo` ya tiene mensaje en `errores.py`.

## Goals / Non-Goals

**Goals:** una transacción por venta, y el 403 del detalle decidido en el servicio.

**Non-Goals:** contar las consultas del detalle (CH-15) y bloquear ventas concurrentes (queda para el cap. 7).

## Decisions

### D1. El Unit of Work de ventas trae libros y movimientos

Así `aplicar_movimiento` corre en la misma sesión. El parámetro del punto único pasa a ser cualquier objeto con `movimientos`, sin cambiar lo que hace.

### D2. Primero las referencias, después las escrituras

Cliente inexistente y libro inexistente o dado de baja se responden 409 antes de insertar. El stock no se precalcula: si el flush choca con el CHECK, el Unit of Work revierte todo, incluida la Rayuela que sí alcanzaba.

### D3. El detalle no lleva `requiere_rol`

`router_protegido` solo exige sesión. El servicio lee los roles vigentes y el `usuario_id` del cliente de la venta. 404 si no hay venta; 403 si no es personal ni dueño.

### D4. El aviso va después del `async with`

`BackgroundTasks` se agenda en el router, cuando `registrar` ya volvió. Si la venta lanzó, no se agenda.

## Risks / Trade-offs

- [Un 409 de stock consume ids de venta y de movimiento] → la secuencia no retrocede; los `.http` que esperan el id 2 asumen un seed recién corrido.
- [Dos ventas a la vez pueden pisarse] → el CHECK igual impide stock negativo. El bloqueo de fila queda fuera de este parcial.
