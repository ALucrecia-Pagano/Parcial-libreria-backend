# Design — CH-06 `stock-punto-unico-reponer-movimientos`

## Context

Motivación: `proposal.md` § Why. Requisitos: `specs/stock-libros/spec.md`. Base: rama de CH-05 mezclada con main (CH-07 a CH-12). `movimiento_stock` ya tiene su disparador de solo agregado (migración 4, CH-02) y `ck_libro_stock_no_negativo`; `get_usuario_actual` y `requiere_rol` vienen de CH-10.

## Decisions

### D1. Un solo escritor del stock
`aplicar_movimiento` es la caja registradora: cambia `libro.stock` y agrega el movimiento en la misma operación (un `flush`). No hay ningún otro código que asigne `libro.stock` (verificado con búsqueda en `app/`); el alta crea el libro con el valor por defecto 0 y el stock inicial entra por el punto único. Como corre dentro del `async with uow:` del servicio, si algo falla después (por ejemplo, en una venta de CH-14), el Unit of Work revierte stock y movimiento juntos.

### D2. Cantidad 0 no es un movimiento
El CHECK `cantidad <> 0` lo prohíbe en la base; `aplicar_movimiento` además lanza `ValueError` si se lo llama con 0, y el alta no lo llama cuando `stock_inicial = 0`. Resultado: un libro con stock 0 y sin movimientos (C-13 4.2/4.3).

### D3. Reponer un libro dado de baja es 409, no 404
`reponer` lee con `get_by_id_including_deleted`: si no existe → 404; si existe con `borrado_en` → 409 «No se puede reponer un libro dado de baja» (RN-13). Distinguir los dos casos le dice al cliente qué pasó.

### D4. El historial de movimientos incluye libros dados de baja
`GET /libros/{id}/movimientos` responde para cualquier libro que exista (vigente o no): es auditoría. Solo da 404 si el id no existe.

### D5. El usuario del movimiento sale de la sesión
Los handlers reciben `UsuarioActualDep`; FastAPI cachea `get_usuario_actual` por petición, así que la guarda `requiere_rol("ADMIN")` de `main.py` y el handler no consultan dos veces. El cliente nunca manda `usuario_id`.

### D6. Repositorio de movimientos sin update ni delete
`MovimientoStockRepository` sobrescribe `update` y `delete` para lanzar `NotImplementedError`: la regla de solo agregado (RN-12) queda en dos capas independientes, la aplicación y el disparador.

### D7. Contraseña del seed en los `.http`
Se escribe literal (`Secreto1234!`), igual que los `.http` de los compañeros (C-06 y otros): una sola convención en el repo. Se descartó leerla con `{{$dotenv ...}}` porque agregaba un paso de configuración por integrante.

## Risks / Trade-offs

- **Venta (CH-14)**: debe llamar a `aplicar_movimiento` con cantidad negativa y `venta_id`; si el stock no alcanza, el CHECK `ck_libro_stock_no_negativo` dispara un `IntegrityError` que `errores.py` ya traduce a mensaje propio.
- **Concurrencia**: `libro.stock += cantidad` se calcula en Python sobre el valor leído; dos reposiciones simultáneas del mismo libro podrían pisarse. Con la carga del parcial no es un caso de prueba; la mejora sería `SELECT ... FOR UPDATE` o un `UPDATE ... SET stock = stock + :n`.
