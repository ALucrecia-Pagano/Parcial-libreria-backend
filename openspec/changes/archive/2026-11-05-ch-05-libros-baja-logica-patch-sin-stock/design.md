# Design — CH-05 `libros-baja-logica-patch-sin-stock`

## Context

Motivación: `proposal.md` § Why. Requisitos: `specs/catalogo-libros/spec.md`. Parte de la rama de CH-04 (`01403e3`). `libro.borrado_en` y el índice único parcial `uq_libro_isbn_vigente` (`WHERE borrado_en IS NULL`) ya existen desde CH-01; `SoftDeleteRepository` desde CH-02.

## Decisions

### D1. Baja lógica con SoftDeleteRepository
`DELETE` usa `soft_delete` (pone `borrado_en` con zona horaria y hace `flush()`). `get_by_id` del repositorio no ve las bajas, así que dar de baja dos veces, editar o pedir el detalle de un libro dado de baja da 404. La fila queda: la venta 1 lo sigue mostrando, porque `ventas` precarga `renglon.libro` sin filtrar bajas.

### D2. Filtros compartidos entre la página y el total
`_filtros_catalogo(titulo, genero_id)` arma la lista de condiciones una sola vez y la usan `contar_catalogo` y `listar_catalogo`: el `total` cuenta con los mismos filtros que la página (consigna, ejercicio 3).

### D3. Búsqueda con parámetros ligados
`Libro.titulo.icontains(titulo, autoescape=True)` genera `ILIKE` con el valor como parámetro y los comodines `%` y `_` escapados. `' OR '1'='1` se busca como texto: lista vacía, `total` 0.

### D4. Precarga declarada en cada método
Catálogo y «libros de X»: `joinedload` de editorial y género. Detalle: además `selectinload(autorias).joinedload(autor)`, con `populate_existing` para releer después de un PATCH en la misma sesión. Ninguna lectura depende de la carga perezosa.

### D5. «Libros de X» en el módulo libros, sin paginar
Las tres rutas pasan a `libros/router.py` (`router_por_entidad`, sin prefijo): las resuelve el repositorio de libros. Devuelven una lista simple de libros vigentes porque la consigna les asigna solo 200 y 404 (sin `page`/`size`, sin 422). La existencia de la editorial, el género o el autor se comprueba con `BaseRepository` genéricos dentro del UoW de libros (como pide la ficha), sin depender de los servicios de CH-04.

### D6. PATCH: lista blanca de campos
`LibroUpdate` declara solo `titulo` y `precio` con `extra="forbid"`: cualquier otro campo (incluidos `stock` e `isbn`) es 422 sin llegar al servicio. `exclude_unset` aplica solo lo enviado; `null` explícito es 422.

### D7. Alta legada hasta CH-06
`POST /libros` conserva la lógica del TP (con `stock` directo) para no romper el alta mientras CH-06 no esté: está marcada como LEGADO en `schemas.py`, `service.py` y `router.py`.

## Risks / Trade-offs

- **El alta legada todavía escribe `stock` sin movimiento.** Lo resuelve CH-06 (punto único de escritura). Hasta entonces, no usar `POST /libros` para demostrar el invariante.
- **Listas «libros de X» sin paginar**: con el catálogo del parcial son pocas filas; si creciera, se pagina con el mismo envoltorio.
