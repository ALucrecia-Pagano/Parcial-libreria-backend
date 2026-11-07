# Proposal — CH-15 `sin-n-mas-1-background-solo-agregado`

> **Governance: BAJO.** Dueño: Juan García (Parte 5). Depende de CH-14, CH-06 y CH-02.

## Why

El detalle de una venta y los listados que muestran relaciones tienen que resolverse con una cantidad fija de consultas, el aviso del comprobante tiene que verse con el arranque normal de uvicorn, y el disparador de solo agregado tiene que demostrarse con el único `.sql` que la consigna permite.

## What Changes

- La precarga de editorial, género y autores queda en los listados de libros. El detalle de la venta ya precarga cliente, renglones y libro, también si el libro fue dado de baja.
- El aviso usa el logger `uvicorn.error`, que se ve con `uvicorn` sin configuración extra.
- `parcial/test/solo_agregado.sql` intenta `UPDATE` y `DELETE` sobre `movimiento_stock`. Los dos los rechaza el disparador (C-14).
- `C-15_sin_n_mas_1.http` pide el detalle de una venta de 2 renglones y de otra de 4, para comparar la cantidad de SELECT con `SQL_ECHO=true`.
- El README nombra a los integrantes y distingue el seed del parcial del seed del TP.

## Capabilities

### New Capabilities

- *(Ninguna.)*

### Modified Capabilities

- `ventas`: el detalle de una venta se lee con una cantidad de consultas que no depende de los renglones.
- `catalogo-libros`: el listado trae autores, editorial y género ya cargados.
- `stock-libros`: se demuestra, con SQL, que `movimiento_stock` no se actualiza ni se borra.

## Impact

- Modificar: repositorios de libros y de ventas, `parcial/README.md`.
- Crear: `parcial/test/solo_agregado.sql`, `parcial/test/C-15_sin_n_mas_1.http`, `parcial/evidencia/` con la consola de C-15 y la captura de C-14.
