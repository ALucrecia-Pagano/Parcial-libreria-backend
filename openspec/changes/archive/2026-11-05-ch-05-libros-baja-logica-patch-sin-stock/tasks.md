# Tasks: CH-05 — Libros: baja lógica, reuso del ISBN, PATCH sin stock

> **Governance MEDIO.** Dueño: Lucas Avila. Modo de trabajo: Claude escribe, Lucas aplica (`git apply`), corre los `.http` en su PC y hace el commit. Rama creada desde la de CH-04.
>
> **Alcance**:
> - **Crear (3)**: `parcial/app/modules/libros/repository.py`, `parcial/app/modules/libros/unit_of_work.py`, `parcial/test/C-16_busqueda_paginacion_patch.http`.
> - **Modificar (8)**: `libros/service.py`, `libros/router.py`, `libros/schemas.py`, `parcial/app/main.py` (ficha) y, por la mudanza de las rutas «libros de X» y el borrado del puente, `editoriales/router.py`, `generos/router.py`, `autores/router.py`, `autores/service.py` (archivos de CH-04, mismo dueño).
> - **Cierre**: esta carpeta, `openspec/specs/catalogo-libros/spec.md` y la marca en `CHANGES.md`.
>
> **Prohibido tocar**: `despliegue/`, migraciones, `models.py`, `app/core/`, `clientes/`, `ventas/`.

## 1. Rojo

- [x] 1.1 Escribir `parcial/test/C-16_busqueda_paginacion_patch.http` (23 pedidos: inyección, paginación con filtro, detalle, PATCH, baja lógica, libros por entidad).
- [x] 1.2 Correrlo contra el código anterior: listados sin envoltorio (1.3 y 1.4 dan 200), `PATCH {"stock":99}` cambia el stock sin movimiento, `PATCH {"isbn":...}` cambia el ISBN, `DELETE /libros/3` → 409 y Ficciones sigue en todas las lecturas.

## 2. Implementación

- [x] 2.1 `LibroRepository(SoftDeleteRepository[Libro])` con filtros compartidos, búsqueda con parámetros ligados y precarga en cada método.
- [x] 2.2 `LibrosUnitOfWork` con `libros` y `BaseRepository` genéricos de editorial, género y autor.
- [x] 2.3 `LibroUpdate` solo con `titulo` y `precio`, `extra="forbid"`, sin `null`.
- [x] 2.4 Servicio con UoW: `listar`, `obtener`, `actualizar`, `dar_de_baja`, `libros_de_editorial|genero|autor`; alta marcada como legado hasta CH-06.
- [x] 2.5 Router: `router_abierto`, `router_por_entidad`, `router_admin`; DELETE 204.
- [x] 2.6 Quitar las rutas `/{id}/libros` de editoriales, géneros y autores y el puente `get_autor`; `main.py` con los tres routers de libros.
- [x] 2.7 ruff (F, E9, B) sin errores y sin referencias al código viejo.

## 3. Verde y cierre

- [x] 3.1 `git apply` en la PC del integrante; uvicorn recarga sin errores.
- [x] 3.2 `python seed.py` y los 23 pedidos con REST Client: todos coinciden.
- [x] 3.3 Evidencia con `~/evidencia_CH-05.sh` (fuera del repo), pegada en `verify.md`.
- [x] 3.4 Archivar y marcar `[x]` en `CHANGES.md`.
