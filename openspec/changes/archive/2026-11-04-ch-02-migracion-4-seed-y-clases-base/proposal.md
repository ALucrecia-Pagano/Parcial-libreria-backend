# Proposal — CH-02 `migracion-4-seed-y-clases-base`

> **Governance: ALTO** (migración 4 escrita a mano con disparador de base de datos, `seed.py` destructivo con `TRUNCATE ... RESTART IDENTITY CASCADE` y clases base de `app/core/` que sostienen a todos los módulos). En `/opsx:apply`, antes de escribir la migración 4, `parcial/seed.py` y las clases base de `app/core/`, el agente muestra el contenido propuesto y espera el OK de la integrante.

## Why

CH-01 dejó creados los modelos nuevos y la migración 3 (`be806bc23837`), pero todavía faltan las tres piezas que destraban en paralelo el trabajo de los otros cuatro integrantes (Gate 2: CH-04, CH-05 y CH-07): (1) la tabla `movimiento_stock` aún permite `UPDATE` y `DELETE` porque la comparación automática de Alembic (`--autogenerate`) no ve funciones ni disparadores (RN-12); (2) no existe `parcial/seed.py` en la raíz con el dataset inicial del parcial (y el `scripts/seed.py` del TP quedó obsoleto tras CH-01); y (3) ningún módulo puede pasar a capas (`Router → Service → UoW → Repository → Model`) sin las clases base de `app/core/` (`BaseRepository[T]`, `SoftDeleteRepository[T]`, `UnitOfWork`, `paginacion.py` y `errores.py`).

## What Changes

- **Migración 4 escrita a mano** (`parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py`, con `down_revision = 'be806bc23837'`): crea en PL/pgSQL la función `rechazar_modificacion_movimiento_stock()` y el disparador `trg_movimiento_stock_solo_agregado` (`BEFORE UPDATE OR DELETE ON movimiento_stock FOR EACH ROW`) que rechaza cualquier modificación o borrado de filas en `movimiento_stock` (RN-12). Su `downgrade()` elimina el disparador y la función en ese orden. Incluye comentario de que fue escrita a mano y leída antes de aplicarla.
- **BREAKING (seed y archivos heredados del TP en `parcial/`)**:
  - Se crea `parcial/seed.py` en la raíz de `parcial/`: vacía todas las tablas con `TRUNCATE ... RESTART IDENTITY CASCADE` (un `DELETE` lo frenaría el disparador y `RESTART IDENTITY` reinicia las secuencias a `1`) y carga el dataset oficial del parcial: 5 usuarios con una única contraseña ficticia en la constante `PASSWORD_SEED` hasheada con `bcrypt` directo y sus roles en `asignacion_rol` (`otorgada_por = NULL`), 3 editoriales ficticias, 3 géneros, 6 autores, 5 libros con ISBN ficticios y `stock == SUM(movimiento_stock.cantidad)`, 3 clientes (`Lucía Fernández` con perfil, `Tomás Ríos` sin usuario, `Ana Paz` vinculada a `ana@example.com`), la venta 1 de Lucía por `vendedor@example.com` (`1 Rayuela + 2 Ficciones = 69000.00`), los 7 movimientos de stock (`5 "Stock inicial"` por `admin@example.com` y `2 "Venta"` por `vendedor@example.com`) y 1 fila en `evento_seguridad` con actor `"SISTEMA"` (`"Carga de los datos iniciales"`, RN-16).
  - Se eliminan `parcial/scripts/seed.py` y `parcial/scripts/__init__.py` (el seed viejo del TP) y se actualiza la sección de datos iniciales de `parcial/README.md` para documentar `python seed.py` y la contraseña ficticia `PASSWORD_SEED` (D1, D3).
  - Se eliminan `parcial/test/C-01.http` a `parcial/test/C-08.http` (casos del TP que colisionaban en nombre con los casos C-01..C-16 del parcial; siguen intactos en `despliegue/test/`, DD-29).
- **`parcial/app/core/errores.py`**: diccionario `MENSAJES_CONSTRAINT` pre-cargado con los 7 constraints de unicidad de CH-01 (`uq_usuario_email`, `uq_cliente_email`, `uq_cliente_usuario_id`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn_vigente`, `uq_asignacion_rol_abierta`) más los CHECK y FK conocidos (D4), y función `traducir_integrity_error(exc: IntegrityError, default: str = ...) -> HTTPException` que devuelve `HTTPException(status_code=409, detail=...)` con mensaje propio y sin filtrar texto interno de PostgreSQL (RN-15, D5). La traducción la invoca el Router al atrapar `IntegrityError` (D9).
- **`parcial/app/core/repository.py`**: `BaseRepository[T]` (recibe `session: AsyncSession` y `model: type[T]`; ofrece `get_by_id`, `get_all(offset, limit)` ordenado por `id`, `count`, `add`, `update(entity, cambios=None)` y `delete`, haciendo `flush()` y nunca `commit()`, sin parámetros genéricos `where` ni `options`, D6, D7) y `SoftDeleteRepository[T]` (hereda de `BaseRepository[T]`, filtra `borrado_en IS NULL` en `get_by_id`, `get_all` y `count`, y agrega `get_by_id_including_deleted` y `soft_delete`).
- **`parcial/app/core/unit_of_work.py`**: `UnitOfWork` base como gestor de contexto asincrónico (`__aenter__` / `__aexit__`): confirma (`commit()`) al salir sin excepción, revierte (`rollback()`) si sale con excepción, no atrapa ni traduce errores a HTTP (D9) y **no cierra la sesión** porque no la creó.
- **`parcial/app/core/paginacion.py`**: envoltorio genérico `Pagina[T]` (`{items, total, page, size, pages}`), dependencia `ParamsPaginacion` (`page >= 1`, `size` 1..100 con default 20 y propiedad `offset`), `validar_pagina(total, page, size) -> int` (que valida temprano `page > pages` antes de consultar `items` y lanza `422 "La página X no existe: hay Y"`, D8, D10) y `construir_pagina(items, total, page, size) -> Pagina[T]`.

**No entra**: repositorios ni UoW específicos de cada módulo (los crean CH-04, CH-05, CH-06, CH-07, CH-13 y CH-14), `app/core/security.py` (CH-07), `app/core/dependencies.py` (CH-10), ni `parcial/test/solo_agregado.sql` (C-14, lo crea CH-15).

## Capabilities

### New Capabilities
- `datos-iniciales`: puesta en marcha reproducible de la base con `parcial/seed.py` (`TRUNCATE ... RESTART IDENTITY CASCADE`), usuarios con roles iniciales, catálogo ficticio, clientes, venta inicial, movimientos de stock consistentes con `libro.stock` y evento de seguridad inicial del actor `SISTEMA`.
- `acceso-a-datos-y-contratos-base`: clases base de infraestructura en `app/core/` para repositorios genéricos y con baja lógica (`repository.py`), gestión transaccional por petición (`unit_of_work.py`), envoltorio y validación de paginación (`paginacion.py`) y traducción de `IntegrityError` a HTTP 409 sin exponer detalles del motor (`errores.py`).

### Modified Capabilities
- `esquema-de-datos`: se agrega el requisito del disparador de sólo agregado sobre `movimiento_stock` (RN-12) instalado y revertido por la migración 4 escrita a mano.

## Impact

- **Crear (6 archivos en `parcial/`)**:
  - `parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py`
  - `parcial/seed.py`
  - `parcial/app/core/errores.py`
  - `parcial/app/core/repository.py`
  - `parcial/app/core/unit_of_work.py`
  - `parcial/app/core/paginacion.py`
- **Modificar (1 archivo en `parcial/`)**:
  - `parcial/README.md` (paso 10 y notas de carga inicial: reemplaza `python -m scripts.seed` y `71000.00` por `python seed.py`, `69000.00` y documenta `PASSWORD_SEED`, según D1 y D3).
- **Eliminar (10 archivos en `parcial/`)**:
  - `parcial/test/C-01.http` .. `parcial/test/C-08.http` (8 archivos del TP, DD-29).
  - `parcial/scripts/seed.py` y `parcial/scripts/__init__.py` (2 archivos del seed viejo del TP, D3).
- **Sistemas / Dependencias**: desbloquea Gate 2 (`CH-04`, `CH-05`, `CH-07`). No agrega paquetes a `requirements.txt` (`bcrypt` ya fue instalado en CH-01).

