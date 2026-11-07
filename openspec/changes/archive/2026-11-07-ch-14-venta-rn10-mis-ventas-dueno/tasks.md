# Tasks — CH-14 venta atómica y lo propio

## 1. Contratos y prueba

- [x] 1.1 Reescribir los contratos de `POST /ventas` con `extra="forbid"`, renglones no vacíos y sin libros repetidos, y verificar que un cuerpo con `total` no valida.
- [x] 1.2 Escribir `C-10_venta_valida.http`, `C-11_venta_sin_stock.http` y `C-12_venta_referencias_invalidas.http`, y agregar a `C-06_401_vs_403.http` la venta propia de Ana.

## 2. Capas

- [x] 2.1 Crear `repository.py` y `unit_of_work.py` de ventas, con el detalle que precarga cliente, renglones y libro.
- [x] 2.2 Implementar `registrar` en un solo `async with`, llamando a `aplicar_movimiento` con cantidad negativa y motivo «Venta».
- [x] 2.3 Exponer `router_staff` (`POST /ventas`, `GET /ventas`, `GET /clientes/{id}/ventas`) y `router_protegido` (`GET /ventas/{id}`, `GET /mis-ventas`), y agendar el aviso solo si la venta se confirmó.

## 3. Verificación

- [x] 3.1 Correr `python seed.py` y los `.http` C-10, C-11, C-12 y el tramo nuevo de C-06 contra PostgreSQL, y guardar el resultado en `verify.md`.

## Workflow follow-up

- Archivar el change y marcar CH-14 en `CHANGES.md` después de la verificación.
