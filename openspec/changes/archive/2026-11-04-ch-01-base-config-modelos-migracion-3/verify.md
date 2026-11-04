# Verify — CH-01 `base-config-modelos-migracion-3`

Evidencia real corrida contra PostgreSQL 16 (contenedor `pg-parcial`, puerto 5433, base `libreria_parcial`) el 03-04/11/2026. Sin secretos en este archivo. Migración 3: `be806bc23837` (OK de la integrante 04/11/2026).

## Tabla tarea → .http / comando → esperado → obtenido

| Tarea | .http / comando | Esperado | Obtenido |
|---|---|---|---|
| 0.2 | `\d editorial/genero/libro/cliente` (base en revisión 2) | `editorial_nombre_key`, `genero_nombre_key`, `ix_libro_isbn`, `ix_cliente_email` | los 4 nombres presentes |
| 1.2 (rojo) | `uvicorn app.main:app` con `.env` sin `DATABASE_URL` + `CH-01_salud.http` | la app no arranca | `RuntimeError: Falta configurar DATABASE_URL...`; `curl` live/ready: sin conexión (000) |
| 2.1 | `pip install -r requirements.txt` + `pip check` | sin error | `No broken requirements found.` |
| 2.2 | `settings.DATABASE_URL.split('@')[1]` | `host:puerto/base` | `localhost:5433/libreria_parcial` |
| 2.3 | `uvicorn` sin `POSTGRES_PASSWORD`; sin `JWT_SECRET` | `ValidationError` que nombra la variable, sin secretos | ver abajo |
| 2.4 | `grep -iE "password=.+\|secret=.+" env.example` | vacío | vacío |
| 3.1 | `grep -n "global\|^engine" database.py` | vacío | vacío |
| 3.2 | arranque + apagado del lifespan | sin errores | apagado limpio, 0 trazas |
| 3.4 / 6.1 (verde) | `CH-01_salud.http` | 200 / 200 / 503 / recuperación sin reiniciar | `GET /health/live` 200 `{"estado":"vivo"}`; `GET /health/ready` 200 `{"estado":"lista"}`; con PostgreSQL detenido `ready` 503 `{"detail":"base de datos no disponible"}`; tras reiniciarlo `ready` 200 `{"estado":"lista"}` |
| 3.5 | `SQL_ECHO=true` + `/health/ready` | `SELECT 1` en consola | `SELECT 1` presente |
| 4.1–4.5 | `import` de cada módulo; `git diff` ventas/editoriales/generos | sin error; solo lo previsto | ok |
| 4.6 | `python -c` de relaciones | 6 pares recíprocos | ver abajo |
| 5.1 / 5.2 | `alembic current` con y sin `POSTGRES_PASSWORD` | conecta / `ValidationError` | `0f5ab569096b (head)` / `ValidationError ... POSTGRES_PASSWORD Field required` |
| 5.3 | `alembic revision --autogenerate` | `down_revision='0f5ab569096b'` | `be806bc23837`, `down_revision = '0f5ab569096b'`; sin `drop_table` de tablas existentes en `upgrade` |
| 5.4 | lectura + corrección a mano (8 marcas `CORRECCIÓN MANUAL`) | OK de la integrante | OK 04/11/2026 |
| 5.5 | `upgrade head` → `downgrade base` → `upgrade head` | sin error | ver abajo |
| 5.6 | `alembic check` | sin diferencias | `No new upgrade operations detected.` |
| 5.7 | `\d` de las tablas | 7 nombres `uq_*`, un índice por FK nueva, `timestamptz` | ver abajo |
| 5.8 | psql en `BEGIN … ROLLBACK` (11 casos) | cada error nombra su constraint | los 11 casos coinciden; tras el ROLLBACK 0 filas |
| 5.9 | `downgrade -1` + `\d libro/editorial/genero/cliente` + `upgrade head` | esquema del TP restaurado | `ix_libro_isbn` único sin predicado, sin `borrado_en`, `editorial_nombre_key`/`genero_nombre_key` restaurados, `ix_cliente_email`, tablas nuevas ausentes; luego head y `alembic check` limpios |

## 2.3 Salida (sin valores secretos)

```
== sin POSTGRES_PASSWORD
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
POSTGRES_PASSWORD
  Field required [type=missing]
== sin JWT_SECRET
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
JWT_SECRET
  Field required [type=missing]
```

## 4.6 Salida completa

```
Usuario cliente <-> usuario uselist= False
Usuario asignaciones <-> usuario uselist= True
Usuario asignaciones_otorgadas <-> otorgante uselist= True
Usuario movimientos <-> usuario uselist= True
AsignacionRol usuario <-> asignaciones uselist= False
AsignacionRol otorgante <-> asignaciones_otorgadas uselist= False
MovimientoStock libro <-> movimientos uselist= False
MovimientoStock venta <-> movimientos uselist= False
MovimientoStock usuario <-> movimientos uselist= False
Libro editorial <-> libros uselist= False
Libro genero <-> libros uselist= False
Libro autorias <-> libro uselist= True
Libro renglones <-> libro uselist= True
Libro movimientos <-> libro uselist= True
Cliente perfil <-> cliente uselist= False
Cliente usuario <-> cliente uselist= False
Cliente ventas <-> cliente uselist= True
Venta cliente <-> ventas uselist= False
Venta renglones <-> venta uselist= True
Venta movimientos <-> venta uselist= True
```

## 5.5 / 5.6 Ida y vuelta de la migración

```
### alembic upgrade head
Running upgrade 0f5ab569096b -> be806bc23837, acceso y movimiento stock
### alembic downgrade base
Running downgrade be806bc23837 -> 0f5ab569096b, acceso y movimiento stock
Running downgrade 0f5ab569096b -> 95dd46a75b66, Agrega tabla genero y relacion con libro
Running downgrade 95dd46a75b66 -> , esquema inicial sin genero
### alembic upgrade head
Running upgrade  -> 95dd46a75b66, esquema inicial sin genero
Running upgrade 95dd46a75b66 -> 0f5ab569096b, Agrega tabla genero y relacion con libro
Running upgrade 0f5ab569096b -> be806bc23837, acceso y movimiento stock
### alembic current
be806bc23837 (head)
### alembic check
No new upgrade operations detected.
```

## 5.7 Esquema (extracto de `\d`)

- `usuario`: `uq_usuario_email` UNIQUE.
- `asignacion_rol`: `desde`, `vence_en`, `revocada_en` en `timestamp with time zone`; índices `ix_asignacion_rol_otorgada_por`, `ix_asignacion_rol_usuario_id`, `uq_asignacion_rol_abierta` UNIQUE `(usuario_id, rol) WHERE revocada_en IS NULL`; CHECK `ck_asignacion_rol_rol_valido`.
- `intento_acceso`: `cuando` timestamptz; índice `ix_intento_acceso_email_ip_cuando (email, ip, cuando)`.
- `evento_seguridad`: `cuando` timestamptz; sin FK ni índices extra.
- `movimiento_stock`: `cuando` timestamptz; `usuario_id` NOT NULL; índices `ix_movimiento_stock_libro_id`, `_usuario_id`, `_venta_id`; CHECK `ck_movimiento_stock_cantidad_no_cero`.
- `cliente`: `uq_cliente_email`, `uq_cliente_usuario_id` (UNIQUE; es el único índice de `usuario_id`, ver design § Índices de FK), FK `cliente_usuario_id_fkey`.
- `libro`: `borrado_en` timestamptz; `uq_libro_isbn_vigente` UNIQUE `(isbn) WHERE borrado_en IS NULL`; ya no existe `ix_libro_isbn`.
- `editorial`: `uq_editorial_nombre`; `genero`: `uq_genero_nombre`.

## 5.8 Salida de los casos de unicidad / CHECK (dentro de `BEGIN … ROLLBACK`)

```
T1 usuario email duplicado      -> 23505 violates unique constraint "uq_usuario_email"
T2 ISBN vigente repetido        -> 23505 violates unique constraint "uq_libro_isbn_vigente"
T3 mismo ISBN, anterior de baja -> OK  (A vigente=f, C vigente=t)
T4 segunda asignación abierta   -> 23505 violates unique constraint "uq_asignacion_rol_abierta"
T5 revocada + nueva             -> OK  (ADMIN abierta=f, ADMIN abierta=t)
T6 rol inválido ('JEFE')        -> 23514 violates check constraint "ck_asignacion_rol_rol_valido"
T7 cantidad = 0                 -> 23514 violates check constraint "ck_movimiento_stock_cantidad_no_cero"
T8 movimiento sin usuario_id    -> 23502 null value in column "usuario_id" violates not-null constraint
T9 cliente.usuario_id repetido  -> 23505 violates unique constraint "uq_cliente_usuario_id"
T10 editorial duplicada         -> 23505 violates unique constraint "uq_editorial_nombre"
T11 género duplicado            -> 23505 violates unique constraint "uq_genero_nombre"
tras ROLLBACK: usuarios=0, libros=0, editoriales=0
```

## Notas

- `scripts/seed.py` (TP) queda roto hasta CH-02 (supuesto aceptado C4).
- La base de prueba quedó en la revisión `be806bc23837` (head).
