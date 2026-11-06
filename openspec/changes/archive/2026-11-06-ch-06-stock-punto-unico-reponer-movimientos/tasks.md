# Tasks: CH-06 — Punto único de stock, reponer y movimientos

> **Governance ALTO.** Dueño: Lucas Avila. Modo de trabajo: Claude escribe, Lucas aplica (`git apply`), corre los `.http` en su PC y hace el commit.
>
> **Alcance**:
> - **Crear (2)**: `parcial/app/modules/libros/stock.py`, `parcial/test/C-13_baja_reposicion_isbn.http`.
> - **Modificar (7)**: `libros/repository.py`, `unit_of_work.py`, `service.py`, `router.py`, `schemas.py` (ficha) y, por la guarda de ADMIN de CH-10, `parcial/test/CH-04_editoriales_generos_autores.http` y `parcial/test/C-16_busqueda_paginacion_patch.http` (archivos del mismo dueño).
> - `parcial/app/main.py`: sin cambios (CH-10 ya monta `router_admin` con `requiere_rol("ADMIN")`).
> - **Cierre**: esta carpeta, `openspec/specs/stock-libros/spec.md` y la marca en `CHANGES.md`.
>
> **Prohibido tocar**: `despliegue/`, migraciones, `models.py`, `app/core/`, `usuarios/`, `clientes/`, `ventas/`.

## 1. Rojo

- [x] 1.1 Escribir `parcial/test/C-13_baja_reposicion_isbn.http` (login de ADMIN + 16 pedidos), adelantado el 05/11 mientras se esperaba CH-10.
- [x] 1.2 Correrlo contra el código de CH-05: `/reponer` y `/movimientos` → 404; `POST /libros` con `"stock": 3` → 201 sin movimiento.

## 2. Implementación

- [x] 2.1 `stock.py` con `aplicar_movimiento` (único escritor de `libro.stock`).
- [x] 2.2 `MovimientoStockRepository` de solo agregado y atributo `movimientos` en el UoW.
- [x] 2.3 `LibroCreate` con `stock_inicial`, `ReponerIn`, `MovimientoRead`; `extra="forbid"` también en `AutoriaCreate`.
- [x] 2.4 Servicio: `crear`, `reponer` (404/409), `movimientos`; se elimina el alta legada.
- [x] 2.5 Router: `POST /libros`, `POST /libros/{id}/reponer`, `GET /libros/{id}/movimientos` con `UsuarioActualDep`.
- [x] 2.6 Login de ADMIN en los `.http` de CH-04 y C-16.
- [x] 2.7 ruff (F, E9, B) sin errores; búsqueda: ningún otro archivo asigna `libro.stock`.

## 3. Verde y cierre

- [x] 3.1 `git apply` en la PC del integrante; uvicorn recarga sin errores.
- [x] 3.2 `python seed.py` y C-13 completo con REST Client: todo coincide.
- [x] 3.3 Evidencia con `%USERPROFILE%\evidencia_CH-06.py` (Python, fuera del repo), incluido el invariante en todos los libros vigentes; pegada en `verify.md`.
- [x] 3.4 Archivar y marcar `[x]` en `CHANGES.md`.
