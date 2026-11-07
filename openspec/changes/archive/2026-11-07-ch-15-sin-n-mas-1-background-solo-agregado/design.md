# Design — CH-15 `sin-n-mas-1-background-solo-agregado`

## Context

Ver `proposal.md`. El detalle de la venta ya usa `joinedload` del cliente y `selectinload` de los renglones con el libro. El aviso ya loguea en `uvicorn.error`.

## Goals / Non-Goals

**Goals:** que el listado de libros no dispare cargas perezosas, y dejar el `.sql` y el `.http` de la evidencia.

**Non-Goals:** Redis, cambios en `despliegue/` y reescribir el aviso.

## Decisions

### D1. Los autores entran al `LibroRead` del listado

Si la respuesta trae autores, el repositorio los precarga en el mismo método del listado. El detalle ya los traía.

### D2. No se cambia el logger

`avisar_comprobante` usa `logging.getLogger("uvicorn.error")`. Con el arranque normal de uvicorn ese mensaje se ve después de la respuesta. No hace falta otro handler.

### D3. El `.sql` son dos sentencias sueltas

psql se detiene en el primer error. Cada sentencia se corre sola, como dice el comentario del archivo. Las dos tienen que fallar.

## Risks / Trade-offs

- [El listado de libros ahora trae `autores`] → es un campo de más. Los pedidos que miran stock, título o total siguen válidos.
