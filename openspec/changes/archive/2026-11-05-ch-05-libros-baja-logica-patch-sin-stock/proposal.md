# Proposal — CH-05 `libros-baja-logica-patch-sin-stock`

> **Governance: MEDIO.** Dueño: Lucas Avila (Parte 2). Rama creada desde la de CH-04 (`01403e3`), porque reescribe rutas y un puente que dejó ese change.

## Why

El módulo libros seguía como en el TP: `DELETE /libros/{id}` borraba la fila (y la venta 1 lo impedía con 409), el `PATCH` aceptaba `stock` e `isbn` (cambiaba el stock sin dejar movimiento, contra RN-11), los listados devolvían una lista suelta y el servicio recibía la sesión y confirmaba solo. La consigna pide baja lógica con ISBN reutilizable (RN-13, RN-01), PATCH sin stock, envoltorio de paginación con filtros y capas con Unit of Work.

## What Changes

- **Nuevo `libros/repository.py`**: `LibroRepository(SoftDeleteRepository[Libro])` con `contar_catalogo` / `listar_catalogo` (mismos filtros: vigentes, `titulo` con `icontains` y parámetros ligados, `genero_id`), `obtener_detalle` (precarga editorial, género y autores) y `listar_vigentes_de_editorial|genero|autor`.
- **Nuevo `libros/unit_of_work.py`**: `LibrosUnitOfWork` con el repositorio de libros y `BaseRepository` genéricos de editorial, género y autor (para los 404), todos con la misma sesión.
- **`libros/service.py`**: `listar`, `obtener`, `actualizar`, `dar_de_baja`, `libros_de_editorial|genero|autor`, todos reciben el UoW y lo abren con `async with`.
- **`libros/schemas.py`**: `LibroUpdate` solo con `titulo` y `precio`, `extra="forbid"` (con `stock` o `isbn` → 422), sin `null`.
- **`libros/router.py`**: `router_abierto` (`GET /libros`, `GET /libros/{id}`), `router_por_entidad` (`GET /editoriales|generos|autores/{id}/libros`, mudadas desde sus módulos) y `router_admin` (`PATCH`, `DELETE` 204 con baja lógica).
- **Endpoints**: `GET /libros` (`page`, `size`, `titulo`, `genero_id`) → 200, 422; `GET /libros/{id}` → 200, 404 (dado de baja → 404), 422; `PATCH /libros/{id}` → 200, 404, 409, 422; `DELETE /libros/{id}` → 204, 404; `GET /{x}/{id}/libros` → 200, 404 (solo vigentes).
- Se quitan las rutas `/{id}/libros` de los routers de editoriales, géneros y autores y el puente `autores/service.get_autor` (archivos de CH-04, mismo dueño). `main.py`: solo `include_router`.

**No entra**: `POST /libros` con `stock_inicial`, reponer y movimientos (CH-06: el alta queda como legado del TP, marcado en el código); guardas de rol (CH-10). `errores.py` no cambia: `uq_libro_isbn_vigente` ya tenía su mensaje desde CH-02.

## Capabilities

### New Capabilities
- `catalogo-libros`: catálogo público de libros vigentes con búsqueda segura y paginación, detalle con precarga, PATCH limitado a título y precio, baja lógica y lecturas de libros por editorial, género o autor.

## Impact

- **Crear (3)**: `parcial/app/modules/libros/repository.py`, `parcial/app/modules/libros/unit_of_work.py`, `parcial/test/C-16_busqueda_paginacion_patch.http`.
- **Modificar (8)**: `libros/service.py`, `libros/router.py`, `libros/schemas.py`, `editoriales/router.py`, `generos/router.py`, `autores/router.py`, `autores/service.py`, `parcial/app/main.py`.
- **Reglas**: RN-01 (ISBN entre vigentes), RN-11 (PATCH sin stock → 422), RN-13 (baja lógica), RN-15.
- **Casos**: **C-16** completo. C-13 se completa en CH-06 (necesita el alta con `stock_inicial`).
