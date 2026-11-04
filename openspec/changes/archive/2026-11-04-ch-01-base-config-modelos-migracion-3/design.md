# Design — CH-01 `base-config-modelos-migracion-3`

> **Governance ALTO.** En el apply, antes de escribir `config.py`, `env.example`, `alembic.ini`/`migrations/env.py` y la migración 3, el agente muestra lo que va a escribir y espera la revisión de la integrante. La migración 3 se muestra **después** de autogenerarla y **antes** de aplicarla.

## Context

Motivación: ver `proposal.md` § Why. Requisitos: ver `specs/`.

Estado observado en `parcial/` (lectura del 03/11/2026):

- `app/core/config.py`: clase plana con `os.getenv` + `python-dotenv`; expone `APP_NAME`, `DEBUG`, `DATABASE_URL` (falla si falta). Lo usan `database.py` (`DATABASE_URL`, `DEBUG`), `main.py` (`APP_NAME`) y `migrations/env.py` (`DATABASE_URL`).
- `app/core/database.py`: `init_resources()` / `dispose_resources()` con **globales de módulo**; `get_session` inicializa perezosamente si no hay fábrica. `scripts/seed.py` importa `init_resources` y `dispose_resources`.
- `app/main.py`: lifespan ya guarda `engine` y `session_factory` en `app.state`.
- `app/modules/health/router.py`: ya tiene `/live` y `/ready` (503 con `detail="base de datos no disponible"`), pero depende del `get_session` con globales.
- Unicidad en la base hoy (migraciones 1 y 2): `cliente.email` → índice único `ix_cliente_email`; `libro.isbn` → índice único `ix_libro_isbn`; `editorial.nombre` y `genero.nombre` → `UniqueConstraint` **sin nombre** (PostgreSQL los llama `editorial_nombre_key` / `genero_nombre_key`).
- `alembic.ini` tiene `sqlalchemy.url = postgresql+asyncpg://usuario:clave@...` como marcador.
- `migrations/env.py`: plantilla async, importa los 6 módulos de modelos, pisa la URL con `settings.DATABASE_URL`.
- Existe `parcial/.env.example` (del TP; no se pudo leer por permisos) y no existe `parcial/env.example`. `parcial/README.md` lo nombra en el paso 5 (`cp .env.example .env`, completar `DATABASE_URL`, `DEBUG=true` opcional, líneas 25–27) y en la lista de requisitos del TP (líneas 48 y 65).
- `editoriales/models.py` y `generos/models.py` declaran `nombre: str = Field(unique=True)`; `ventas/models.py` tiene `Venta.cliente` y `Venta.renglones` con `back_populates`.

## Goals / Non-Goals

**Goals:**
- Que todo lo que viene después (CH-02..CH-15) encuentre `settings`, `get_session`, los modelos y la migración 3 tal como los describen la KB y los specs.
- Que la migración 3 sea leída, corregida y reversible, y que `alembic check` quede limpio.

**Non-Goals:**
- No se crean schemas, repositorios, UoW, `errores.py`, `security.py`, `dependencies.py`, `seed.py` nuevo ni el disparador.
- No se reestructura `main.py` en dos grupos de rutas (CH-10); solo se toca el lifespan.
- No se borran los `C-0x.http` del TP (CH-02, DD-29).

## Decisions

### D1 — `Settings` con pydantic-settings
- `BaseSettings` con `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`. `POSTGRES_PASSWORD: SecretStr` y `JWT_SECRET: SecretStr` **sin default** → `ValidationError` al instanciar `settings = Settings()` en la importación, por eso falla tanto `uvicorn` como `alembic`.
- `model_config` incluye `hide_input_in_errors=True`. **Por qué**: el `ValidationError` de pydantic exponía parte del `JWT_SECRET` (`input_value` truncado) al faltar una variable; con la opción el error solo nombra la variable faltante. (Decidido en el apply, aprobado por la integrante el 03/11/2026.)
- Defaults no sensibles (los de la KB 08): `POSTGRES_USER=postgres`, `POSTGRES_DB=libreria`, `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5432`, `JWT_MINUTOS=30`, `BCRYPT_COSTO=12`, `COOKIE_SECURE=False`, `DB_POOL_SIZE=5`, `SQL_ECHO=False`.
- `DATABASE_URL` como `@computed_field` (+ `@property`) que arma la URL con `sqlalchemy.engine.URL.create("postgresql+asyncpg", ...)` y la devuelve con `render_as_string(hide_password=False)`. **Por qué** `URL.create` y no un f-string: una contraseña con `@`, `/` o `:` rompería la URL; `URL.create` escapa.
- `APP_NAME` queda como campo con default (no es variable de la KB, no es sensible; lo usa `main.py`). `DEBUG` se elimina: lo reemplaza `SQL_ECHO`.
- *Alternativa descartada*: mantener `DATABASE_URL` como variable (DD-04 dice que eso es solo de `despliegue/`).
- *Riesgo*: `computed_field` incluye la URL con contraseña en `settings.model_dump()`. Mitigación: nunca loguear `settings`; comentario en el archivo.

### D2 — `database.py` sin globales
- `crear_motor(settings) -> AsyncEngine` (`pool_size=DB_POOL_SIZE`, `echo=SQL_ECHO`) y `crear_fabrica(engine) -> async_sessionmaker` (`expire_on_commit=False`). Se conservan `init_resources()` (devuelve `(engine, fabrica)`) y `dispose_resources(engine)` como envoltorios, para "adaptar" lo del TP como pide la ficha.
- `get_session(request: Request)` toma `request.app.state.session_factory` y hace `async with fabrica() as session: yield session` (cierra siempre). Se ofrece el alias `SessionDep = Annotated[AsyncSession, Depends(get_session)]` (regla `fastapi` del registry).
- *Por qué sin globales*: la cátedra (§1.9, §3.10, §4.5) pide crearlos en el ciclo de vida, "ni por petición ni a nivel de módulo"; la inicialización perezosa actual escondería un lifespan roto.
- *Efecto colateral aceptado (C4)*: `scripts/seed.py` llama `dispose_resources()` sin argumento y usa los modelos viejos → queda roto hasta CH-02 (que reescribe el seed en la raíz). No se toca.

### D3 — Health
- Se mantiene la forma actual (`{"estado": "vivo"}`, `{"estado": "lista"}`, 503 con mensaje propio). `/ready` usa `SessionDep` y atrapa `SQLAlchemyError` y `OSError` (asyncpg/socket) en vez de `Exception` genérico. Como `create_async_engine` no conecta al crearse, la app arranca con la base apagada y `/ready` puede dar 503 y luego recuperarse.
- `pool_pre_ping` no se activa: no hace falta para el caso y agrega una ida y vuelta por checkout.

### D4 — Modelos
- **Estilo**: igual que el TP (`Optional[int]` PK, `Relationship(back_populates=...)` en los dos extremos, fechas `sa_column=Column(DateTime(timezone=True), nullable=False)` con `default_factory=lambda: datetime.now(timezone.utc)`, imports al pie para registrar el metadata). Se mantiene `int`/`SERIAL` como el TP en lugar del `BIGINT IDENTITY` que sugiere `postgresql-table-design`, para no mezclar tipos de PK/FK con las tablas existentes.
- **`usuarios/models.py`**: `Usuario` (`email` con `UniqueConstraint("email", name="uq_usuario_email")`, `activo` default `True`, `debe_cambiar_password` default `False`, todos NOT NULL); `AsignacionRol` (`CheckConstraint("rol IN ('ADMIN','VENDEDOR','CLIENTE')", name="ck_asignacion_rol_rol_valido")`, `Index("uq_asignacion_rol_abierta", "usuario_id", "rol", unique=True, postgresql_where=text("revocada_en IS NULL"))`, `usuario_id` e `otorgada_por` FK a `usuario.id` con índice). `IntentoAcceso` con `Index("ix_intento_acceso_email_ip_cuando", "email", "ip", "cuando")`; `EventoSeguridad` sin extras ni relaciones (aisladas por diseño, KB 04).
- **`libros/models.py`**: `Libro.borrado_en: Optional[datetime]` timestamptz nulo; `isbn` pierde `unique=True`/`index=True` y se declara `Index("uq_libro_isbn_vigente", "isbn", unique=True, postgresql_where=text("borrado_en IS NULL"))`. `MovimientoStock` con `CheckConstraint("cantidad <> 0", name="ck_movimiento_stock_cantidad_no_cero")`, `libro_id`/`usuario_id` NOT NULL con índice, `venta_id` nulo con índice, `motivo: str` sin CHECK (DD-14).
- **`clientes/models.py`**: `email` pasa de `Field(unique=True, index=True)` a `UniqueConstraint("email", name="uq_cliente_email")`; `usuario_id: Optional[int]` FK con `UniqueConstraint("usuario_id", name="uq_cliente_usuario_id")` (el UNIQUE ya indexa; no se agrega índice aparte).
- **`editoriales/models.py` y `generos/models.py`** (C1): `nombre` pasa de `Field(unique=True)` a `__table_args__ = (UniqueConstraint("nombre", name="uq_editorial_nombre"),)` / `uq_genero_nombre`. Mismo nombre en modelo y base → `alembic check` limpio.
- **`ventas/models.py`** (C3): solo se agrega `Venta.movimientos` y el `TYPE_CHECKING` de `MovimientoStock`; nada más cambia.
- **Relaciones en los dos extremos** (C3, todas con `back_populates`):

  | Lado A | Lado B | Notas |
  |---|---|---|
  | `Usuario.cliente: Optional[Cliente]` | `Cliente.usuario: Optional[Usuario]` | `uselist=False` en **los dos** lados (1 a 0..1) |
  | `Usuario.asignaciones: list[AsignacionRol]` | `AsignacionRol.usuario` | `foreign_keys="[AsignacionRol.usuario_id]"` en ambos |
  | `Usuario.asignaciones_otorgadas: list[AsignacionRol]` | `AsignacionRol.otorgante: Optional[Usuario]` | `foreign_keys="[AsignacionRol.otorgada_por]"` en ambos (hay dos FK a `usuario`; sin esto SQLAlchemy da `AmbiguousForeignKeysError`) |
  | `Libro.movimientos: list[MovimientoStock]` | `MovimientoStock.libro` | |
  | `Venta.movimientos: list[MovimientoStock]` | `MovimientoStock.venta: Optional[Venta]` | `venta_id` nulo |
  | `Usuario.movimientos: list[MovimientoStock]` | `MovimientoStock.usuario` | |

  Ninguna relación se carga perezosamente desde el código (regla 17): la precarga la declaran los repositorios de los changes siguientes.
- **FK `ON DELETE` y tipo de PK (C5, decidido)**: se sigue el estilo del TP: PK `Optional[int]` (SERIAL) y FK sin `ON DELETE` (queda `NO ACTION`). En el parcial no se borran usuarios ni libros físicamente (baja lógica / `activo`) y `movimiento_stock` es de sólo agregado; mezclar `BIGINT` con las FK `INTEGER` existentes no aporta. Se aparta a propósito de la regla de `postgresql-table-design`.
- *Alternativa descartada*: `UniqueConstraint` común para el ISBN + columna generada — no expresa "único entre vigentes".
- Índices de FK: cada FK nueva lleva índice propio, como exige la consigna (sección 4.10). asignacion_rol.usuario_id también, porque el índice único parcial uq_asignacion_rol_abierta solo cubre las filas con revocada_en IS NULL y no sirve para consultar el historial de roles revocados. La única FK sin índice propio es cliente.usuario_id, porque su UNIQUE ya crea uno.

### D5 — Migración 3
1. `alembic revision --autogenerate -m "acceso y movimiento stock"` (la URL sale de `Settings`).
2. **Leer el archivo entero** y corregir a mano (SU-04). Correcciones esperadas:
   - Orden: crear `usuario` antes que `asignacion_rol`, `movimiento_stock` y la FK de `cliente.usuario_id`.
   - `libro.isbn`: el autogenerate tiende a emitir `drop_index('ix_libro_isbn')` + `create_index('uq_libro_isbn_vigente', ...)` **sin** `postgresql_where`, o a omitirlo. Se deja explícito `op.drop_index("ix_libro_isbn", table_name="libro")` y `op.create_index("uq_libro_isbn_vigente", "libro", ["isbn"], unique=True, postgresql_where=sa.text("borrado_en IS NULL"))`; en `downgrade`, al revés (y `op.create_index("ix_libro_isbn", "libro", ["isbn"], unique=True)`).
   - `cliente.email`: `drop_index("ix_cliente_email")` + `create_unique_constraint("uq_cliente_email", "cliente", ["email"])`; inverso en downgrade.
   - `editorial`/`genero` (C1): con el nombre ya declarado en el modelo, el autogenerate emite (o no detecta) un `drop_constraint`/`create_unique_constraint`; se reemplaza por `op.execute("ALTER TABLE editorial RENAME CONSTRAINT editorial_nombre_key TO uq_editorial_nombre")` (ídem `genero`) y el inverso en downgrade: renombrar no reconstruye el índice ni deja una ventana sin unicidad.
   - `asignacion_rol`: verificar que el índice parcial salga con `postgresql_where`.
   - `downgrade`: borrar en orden inverso (FK de cliente, `movimiento_stock`, `asignacion_rol`, `evento_seguridad`, `intento_acceso`, `usuario`), columnas `cliente.usuario_id` y `libro.borrado_en`.
3. **Comentarios obligatorios** (los pide la consigna): (a) en el docstring/encabezado, "Migración autogenerada y LEÍDA antes de aplicarla; corregida a mano en los puntos marcados `# CORRECCIÓN MANUAL`"; (b) junto a **cada** operación corregida, un comentario `# CORRECCIÓN MANUAL: el autogenerate generó <X>; se cambió por <Y> porque <motivo>` (uno por corrección, en `upgrade` y en `downgrade`). Si el autogenerate ya salió bien en un punto esperado, se anota igual "revisado, sin cambios".
4. Probar: `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head` → `alembic check`.

### D6 — Alembic y `alembic.ini`
- `migrations/env.py` importa además `app.modules.usuarios.models` y usa `settings.DATABASE_URL` (el `computed_field`). `alembic.ini` pierde la línea `sqlalchemy.url` (queda un comentario de que la URL viene de `Settings`). Como `config.set_main_option` se sigue llamando en `env.py`, `async_engine_from_config` encuentra la URL. Nota: `set_main_option` interpreta `%`; si la contraseña tiene `%`, se escapa como `%%` (comentario en `env.py`).

### D7 — Verificación (TDD con `.http`)
- `parcial/test/CH-01_salud.http`: tres pedidos con el esperado en comentario (`live` 200, `ready` 200, `ready` con la base apagada 503). Rojo: se escribe primero y se corre contra la app actual tras romper la configuración (la app no arranca → falla todo) / o con el `ready` que hoy usa globales; verde tras implementar. El 503 se provoca deteniendo el servicio de PostgreSQL.
- Esquema: psql (`\d usuario`, `\d asignacion_rol`, `\d libro`, `\d cliente`, `\di uq_*`) e inserciones de prueba **dentro de `BEGIN … ROLLBACK`** para los escenarios de unicidad/CHECK (sin dejar datos). No se escribe ningún `.py` de prueba (regla 4).

## Conflictos resueltos (decisión de la integrante, 03/11/2026)

| # | Conflicto | Decisión |
|---|---|---|
| C1 | La ficha pide `uq_editorial_nombre`/`uq_genero_nombre` pero sus `models.py` no estaban en "Archivos" (y la KB 04 dice que esas tablas "no cambian"). | Se nombra **en los dos lados**: modelo (`editoriales/models.py`, `generos/models.py` entran al alcance) y migración 3 (`RENAME CONSTRAINT`). Renombrar solo en la migración dejaría el modelo distinto de la base. Las tablas no cambian de columnas, solo el nombre del constraint. |
| C2 | Existía `parcial/.env.example` (TP, con `DATABASE_URL`) y se pide `parcial/env.example`. | Se **borra** `.env.example`, queda solo `env.example`, y se actualizan `parcial/README.md` (paso 5 y lista de requisitos) y el comentario de `parcial/.gitignore` ("copia .env.example" → `env.example`; las reglas de ignorado no cambian). |
| C3 | "La navegación se declara en los dos extremos" (consigna, se corrige) vs. `ventas/models.py` fuera de "Archivos". | `ventas/models.py` entra al alcance (`Venta.movimientos`). **Todas** las relaciones nuevas con `back_populates` en los dos extremos (tabla de D4), `Usuario.cliente` también con `uselist=False`, `AsignacionRol.otorgante` declarada con `foreign_keys` explícito. |
| C4 | `scripts/seed.py` (TP) usa `dispose_resources()` sin argumento y modelos viejos. | **Supuesto aceptado**: el seed viejo queda roto entre CH-01 y CH-02; CH-02 lo reemplaza por `seed.py` en la raíz. |
| C5 | Registry `postgresql-table-design`: `BIGINT IDENTITY` y `ON DELETE` explícito; el TP usa SERIAL y FK sin `ON DELETE`. | **Decisión**: estilo del TP (D4). |

Las ampliaciones de alcance (C1, C2, C3) ya están reflejadas en las fichas CH-01, CH-04 y CH-14 de `CHANGES.md` (las editó el orquestador); al cerrar el change, igual avisar al grupo.

Verificación de relaciones: el `python -c` de una línea (task 4.6) no deja ningún `.py` en el repo (regla 4) y su salida se pega en el verify como evidencia.

## Risks / Trade-offs

- [El autogenerate emite operaciones destructivas o en orden incorrecto] → se lee entero antes de aplicar y se prueba la ida y vuelta sobre base vacía.
- [Bases locales con datos del TP] → todas las columnas nuevas son nulas; cambiar `ix_libro_isbn` a parcial no falla con datos únicos ya existentes.
- [El `.env` viejo de cada integrante deja de servir] → `env.example` + aviso en el resumen del change.
- [`settings` importado al nivel de módulo impide importar la app sin entorno] → es lo que se busca (la app no arranca sin secretos); se documenta en `env.example`.
- [Renombrar constraints depende del nombre por defecto de PostgreSQL] → antes de escribir la migración se verifica con `\d editorial` que se llama `editorial_nombre_key`.

## Migration Plan

Local, por integrante: actualizar `.env` según `env.example` → `pip install -r requirements.txt` → `alembic upgrade head`. Rollback: `alembic downgrade -1` (deja el esquema del TP) y volver al `.env` anterior.
