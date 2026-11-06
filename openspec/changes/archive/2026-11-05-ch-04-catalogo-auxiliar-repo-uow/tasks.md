# Tasks: CH-04 — Editoriales, géneros y autores a repositorio + Unit of Work

> **Governance MEDIO.** Dueño: Lucas Avila. Modo de trabajo acordado: Claude escribe el código, Lucas lo aplica (`git apply`), corre los `.http` en su PC y hace el commit.
>
> **Alcance (Regla Propia 2 de `AGENTS.md`)**: este change SOLO toca:
> - **Crear (7)**: `parcial/app/modules/{editoriales,generos,autores}/repository.py`, `parcial/app/modules/{editoriales,generos,autores}/unit_of_work.py`, `parcial/test/CH-04_editoriales_generos_autores.http`.
> - **Modificar (10)**: `service.py`, `router.py`, `schemas.py` de los tres módulos y `parcial/app/main.py` (solo `include_router`).
> - **Cierre**: esta carpeta de `openspec/`, `openspec/specs/catalogo-auxiliar/spec.md` y la marca de Estado en `CHANGES.md`.
>
> **Prohibido tocar**: `despliegue/`, migraciones, `models.py`, `app/core/`, `libros/`, `clientes/`, `ventas/`.
>
> **Decisiones del integrante (05/11/2026 06:17)**: se quitan los `DELETE` de los tres módulos además de `PATCH /generos`; se mantienen los `GET /{id}`.

## 1. Rojo

- [x] 1.1 Escribir `parcial/test/CH-04_editoriales_generos_autores.http` con 20 pedidos y su respuesta esperada (listados, altas, PATCH, rutas que no existen).
- [x] 1.2 Correrlo contra el código del TP y ver fallar 1.1, 1.2, 1.3, 1.4 (lista suelta, sin `page`/`size`), 3.2 (campo extra aceptado) y 4.1 (`PATCH /generos` existe).

## 2. Implementación

- [x] 2.1 `repository.py` en los tres módulos, heredando de `BaseRepository` y pasando la clase del modelo.
- [x] 2.2 `unit_of_work.py` en los tres módulos, heredando de `UnitOfWork` con la misma sesión.
- [x] 2.3 `schemas.py`: `extra="forbid"` en Create/Update; `rechazar_nulos` en los PATCH; se elimina `GeneroUpdate`.
- [x] 2.4 `service.py`: recibe el UoW y lo abre con `async with`; paginación con `validar_pagina` + `construir_pagina`; 404 propio; sin `commit()` ni `session`.
- [x] 2.5 `router.py`: `get_uow`, `router_abierto` / `router_admin`, `traducir_integrity_error`; sin `DELETE` ni `PATCH /generos`; rutas `/{id}/libros` adaptadas sin cambiar su lógica (CH-05).
- [x] 2.6 `main.py`: `include_router` de los seis routers.
- [x] 2.7 Análisis estático (ruff F, E9, B) sin errores.

## 3. Verde y cierre

- [x] 3.1 `git apply` en la PC del integrante; uvicorn recarga sin errores.
- [x] 3.2 `python seed.py` y los 20 pedidos del `.http` con REST Client: todos coinciden.
- [x] 3.3 Evidencia guardada con un script `curl` fuera del repo (`~/evidencia_CH-04.sh`), pegada en `verify.md`.
- [x] 3.4 Archivar el change y marcar `[x]` en `CHANGES.md`.
