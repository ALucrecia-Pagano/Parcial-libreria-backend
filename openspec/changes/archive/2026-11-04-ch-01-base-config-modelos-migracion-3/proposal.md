# Proposal — CH-01 `base-config-modelos-migracion-3`

> **Governance: ALTO** (configuración y secretos; migración que cambia el esquema con datos). La implementación de `config.py`, `env.example`, `alembic.ini`/`env.py` y la migración 3 **se propone y se revisa antes de escribirse**: en `/opsx:apply` el agente muestra el plan de cada uno de esos archivos y espera el OK de la integrante antes de tocarlos.

## Why

El parcial (caps. 5 y 6) arranca sobre el TP de los caps. 1–4, que se configura con una sola `DATABASE_URL` leída a mano con `os.getenv`, no tiene usuarios, roles ni movimientos de stock, y declara el ISBN con un UNIQUE común. Todos los demás changes (CH-02 en adelante) necesitan una base común: `Settings` sin secretos por defecto, el motor y la sesión creados en el lifespan, la salud que distingue "vivo" de "listo", los modelos nuevos con sus constraints **nombrados** (los usa `errores.py` de CH-02) y la migración 3 aplicada. Es el primer eslabón del camino crítico: nadie avanza hasta que esto esté en `main`.

## What Changes

- **BREAKING (config)**: `app/core/config.py` pasa de `os.getenv("DATABASE_URL")` a `Settings` de pydantic-settings con `POSTGRES_USER/PASSWORD/DB/HOST/PORT`, `JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO`, `COOKIE_SECURE`, `DB_POOL_SIZE`, `SQL_ECHO`. La URL `postgresql+asyncpg://...` se arma con `@computed_field`. **Sin default** para `POSTGRES_PASSWORD` ni `JWT_SECRET`: si faltan, la app (y Alembic) no arrancan. `DATABASE_URL` y `DEBUG` dejan de existir en `parcial/` (DD-04: `despliegue/` sigue con `DATABASE_URL`).
- `app/core/database.py`: funciones que crean el motor (`pool_size=DB_POOL_SIZE`, `echo=SQL_ECHO`) y la fábrica (`expire_on_commit=False`); el lifespan de `app/main.py` las llama, las guarda en `app.state` y hace `dispose()` al apagar. `get_session` toma la fábrica de `app.state` (ya no hay globales de módulo ni inicialización perezosa).
- `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`; **503** si la base no contesta). Módulo `health` solo con `router.py`.
- Módulo nuevo `usuarios` con `Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad`; `MovimientoStock` en `libros`.
- **Toda relación nueva se declara en los dos extremos** (`back_populates`), como exige la consigna: `Usuario.cliente` ↔ `Cliente.usuario` (objeto único en los dos lados), `Usuario.asignaciones` ↔ `AsignacionRol.usuario`, `Usuario.asignaciones_otorgadas` ↔ `AsignacionRol.otorgante`, `Libro.movimientos` ↔ `MovimientoStock.libro`, `Venta.movimientos` ↔ `MovimientoStock.venta`, `Usuario.movimientos` ↔ `MovimientoStock.usuario`.
- `Cliente.usuario_id` (nulo, UNIQUE); `Libro.borrado_en` y el UNIQUE de `isbn` **reemplazado** por el índice único parcial `uq_libro_isbn_vigente`.
- Constraints nombrados **en el modelo y en la migración**: `uq_usuario_email`, `uq_cliente_email`, `uq_cliente_usuario_id`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn_vigente`, `uq_asignacion_rol_abierta`.
- Migración 3 (`<rev>_acceso_y_movimiento_stock.py`) autogenerada, **leída antes de aplicarla** (comentario que lo dice) y **corregida a mano**, con un comentario explicativo junto a **cada** corrección; ida y vuelta `upgrade head → downgrade base → upgrade head`.
- Alembic toma la URL de `Settings`; `alembic.ini` queda sin URL.
- `requirements.txt` + `pydantic-settings>=2.0`, `bcrypt>=4.0`, `PyJWT>=2.8`; `parcial/env.example` con todas las variables y ningún secreto; **se borra** `parcial/.env.example` (documentaba `DATABASE_URL`, que desaparece) y se actualizan los pasos de `parcial/README.md` y el comentario de `parcial/.gitignore` que lo nombran.
- `parcial/test/CH-01_salud.http` (verificación auxiliar, no es un caso C).

**No entra**: `security.py` y hash ficticio (CH-07), `dependencies.py` (CH-10), repositorios/UoW/`errores.py` (CH-02), `seed.py`, disparador de sólo agregado (migración 4, CH-02).

## Capabilities

### New Capabilities
- `configuracion-y-ciclo-de-vida`: configuración tipada sin secretos por defecto, recursos (motor, fábrica de sesiones) creados y liberados en el lifespan, una sesión por petición, Alembic leyendo la misma configuración.
- `salud`: endpoints `/health/live` y `/health/ready` y cómo responden según el estado de la base.
- `esquema-de-datos`: tablas nuevas de acceso y de movimientos de stock, cambios en `cliente` y `libro`, constraints nombrados, índices únicos parciales (RN-01, RN-03, base de RN-12) y la migración 3 reversible.

### Modified Capabilities
- (ninguna: `openspec/specs/` está vacío)

## Impact

- **Código** (`parcial/` únicamente): `app/core/config.py`, `app/core/database.py`, `app/main.py`, `app/modules/health/router.py`, `app/modules/libros/models.py`, `app/modules/clientes/models.py`, `app/modules/editoriales/models.py`, `app/modules/generos/models.py`, `app/modules/ventas/models.py`, nuevo `app/modules/usuarios/`, `migrations/env.py`, `alembic.ini`, `requirements.txt`, `README.md`, `.gitignore` (solo un comentario), nuevo `env.example`, **borrado** `.env.example`, nueva migración 3, nuevo `test/CH-01_salud.http`. (Los tres `models.py` de editoriales, géneros y ventas, `README.md`, `.gitignore` y el borrado de `.env.example` se suman por decisión de la integrante; las fichas CH-01, CH-04 y CH-14 de `CHANGES.md` ya los reflejan.)
- **Entorno**: cada integrante debe reescribir su `.env` local con `POSTGRES_*` y `JWT_SECRET` (el `DATABASE_URL` del TP deja de servir en `parcial/`).
- **Base**: la migración 3 cambia el índice de `libro.isbn` y de `cliente.email` y renombra los UNIQUE de `editorial.nombre` y `genero.nombre`; reversible.
- **Dependencias**: `pydantic-settings`, `bcrypt`, `PyJWT` (las dos últimas solo se instalan; se usan desde CH-02/CH-07).
- **Conflictos resueltos** (detalle en `design.md` § Conflictos resueltos): C1–C5 decididos por la integrante. Queda aceptado que `scripts/seed.py` del TP no funciona entre CH-01 y CH-02.
