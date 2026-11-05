# Proposal — CH-04 `catalogo-auxiliar-repo-uow`

> **Governance: MEDIO** (refactor de capas en tres módulos: editoriales, géneros y autores). Dueño: Lucas Avila (Parte 2).

## Why

Después de CH-01 y CH-02, los módulos del catálogo auxiliar seguían con la estructura del TP: el servicio recibía la sesión, consultaba y hacía `commit()` por su cuenta, los listados devolvían una lista suelta con `limit`/`offset` y los contratos de entrada ignoraban los campos de más. La consigna (ejercicios 3 y 6) pide `Router → Service → UoW → Repository → Model`, el envoltorio `{items, total, page, size, pages}` y contratos con `extra="forbid"`.

## What Changes

- Por módulo (`editoriales`, `generos`, `autores`):
  - **Nuevo `repository.py`**: `EditorialRepository`, `GeneroRepository` y `AutorRepository` heredan de `BaseRepository[T]` y le pasan la clase del modelo (§6.4.3). Solo `flush()`, nunca `commit()`.
  - **Nuevo `unit_of_work.py`**: `EditorialesUnitOfWork`, `GenerosUnitOfWork`, `AutoresUnitOfWork` heredan de `UnitOfWork` y crean su repositorio con la misma sesión.
  - **`service.py`**: cada función recibe el UoW y lo abre con `async with uow:`; deja de recibir la sesión y deja de confirmar. Listados con `validar_pagina` antes del SELECT y `construir_pagina`.
  - **`router.py`**: dependencia `get_uow` (sesión de la petición), `router_abierto` (lecturas) y `router_admin` (escrituras, la guarda de rol llega con CH-10), y `raise traducir_integrity_error(exc) from None`.
  - **`schemas.py`**: `extra="forbid"` en todos los contratos de entrada; los PATCH rechazan `null` explícito (422) y se aplican con `exclude_unset`.
- **Endpoints**: `GET /editoriales`, `GET /generos` (y `GET /autores`) con envoltorio → 200, 422; `POST /editoriales`, `/generos`, `/autores` → 201, 409, 422; `PATCH /editoriales/{id}`, `/autores/{id}` → 200, 404, 409, 422.
- **BREAKING**: se eliminan `PATCH /generos/{id}` (no existe en la consigna) y los `DELETE` de editoriales, géneros y autores (decisión del integrante: el catálogo auxiliar no se borra físicamente). Esas rutas responden 405.
- **`main.py`**: solo los `include_router` de los seis routers nuevos.

**No entra**: `GET /{x}/{id}/libros` (CH-05; solo se adaptaron para seguir andando con el UoW), guardas de rol (CH-10), cambios en `models.py` (ya los dejó CH-01) y en `errores.py` (los mensajes `uq_editorial_nombre` y `uq_genero_nombre` ya estaban desde CH-02).

## Capabilities

### New Capabilities
- `catalogo-auxiliar`: alta, lectura paginada y modificación parcial de editoriales, géneros y autores con repositorios + Unit of Work, contratos estrictos y unicidad garantizada por la base.

## Impact

- **Crear (7)**: `parcial/app/modules/{editoriales,generos,autores}/repository.py`, `.../unit_of_work.py`, `parcial/test/CH-04_editoriales_generos_autores.http`.
- **Modificar (10)**: `service.py`, `router.py` y `schemas.py` de los tres módulos; `parcial/app/main.py`.
- **Reglas de negocio**: RN-01 (nombre de editorial y género), RN-11 (`extra="forbid"` como patrón), RN-15 (sin texto de la base, sin 500).
- **Casos**: apoya C-16 (paginación y PATCH parcial) en el catálogo auxiliar.
