# Design — CH-02 `migracion-4-seed-y-clases-base`

> **Governance ALTO.** En `/opsx:apply`, antes de escribir la migración 4 (`parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py`), `parcial/seed.py` y las clases base de `parcial/app/core/`, el agente muestra el código propuesto y espera el OK de la integrante.

## Context

Motivación: ver `proposal.md` § Why. Requisitos: ver `specs/esquema-de-datos/spec.md`, `specs/datos-iniciales/spec.md` y `specs/acceso-a-datos-y-contratos-base/spec.md`.

Estado observado en `parcial/` tras el cierre de CH-01 (commit `dae0385`, 04/11/2026):
- La cabeza de Alembic en `parcial/migrations/versions/` es `be806bc23837_acceso_y_movimiento_stock.py` (`revision = 'be806bc23837'`). Ya existen en el esquema y en los modelos las tablas `usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad` y `movimiento_stock`, las columnas `cliente.usuario_id` y `libro.borrado_en`, y los 7 nombres de unicidad (`uq_usuario_email`, `uq_cliente_email`, `uq_cliente_usuario_id`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn_vigente`, `uq_asignacion_rol_abierta`).
- `parcial/app/core/database.py` expone `init_resources() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]`, `dispose_resources(engine: AsyncEngine) -> None`, `get_session(request: Request)` y `SessionDep`.
- `parcial/scripts/seed.py` (heredado del TP) llama a `dispose_resources()` sin argumento, rechaza una base con datos y no conoce los modelos de acceso ni de movimientos.
- En `parcial/test/` siguen los 8 archivos `C-01.http` .. `C-08.http` del TP junto a `CH-01_salud.http`.
- En `parcial/app/core/` todavía no existen `errores.py`, `repository.py`, `unit_of_work.py` ni `paginacion.py`.

## Goals / Non-Goals

**Goals:**
- Garantizar en la propia base que `movimiento_stock` sea de sólo agregado mediante un disparador PL/pgSQL instalado y revertido por la migración 4 escrita a mano (RN-12).
- Dejar `parcial/seed.py` idempotente en la raíz de `parcial/` usando `TRUNCATE ... RESTART IDENTITY CASCADE`, con `libro.stock == SUM(movimiento_stock.cantidad)` en los 5 libros, y limpiar los archivos obsoletos del TP (`parcial/scripts/` y `parcial/test/C-01..C-08.http`).
- Entregar las 4 piezas de infraestructura en `parcial/app/core/` (`errores.py`, `repository.py`, `unit_of_work.py`, `paginacion.py`) con contratos cerrados para que CH-04, CH-05 y CH-07 puedan implementarse en paralelo sin editar `app/core/`.

**Non-Goals:**
- No se implementan repositorios ni Unit of Work de ningún módulo (`modules/*/repository.py`, `modules/*/unit_of_work.py`).
- No se tocan `service.py`, `router.py` ni `schemas.py` de ningún módulo del TP.
- No se crea `parcial/test/solo_agregado.sql` (pertenece a CH-15 / caso C-14).
- No se crea `app/core/security.py` (CH-07) ni `app/core/dependencies.py` (CH-10).

## Decisions

Las decisiones **D1 a D10** fueron cerradas por la integrante durante `/opsx:explore CH-02` (04/11/2026, observación `#397` de Engram) y se complementan con el diseño técnico de la migración 4:

### M4 — Migración 4 escrita a mano (`movimiento_stock` de sólo agregado, RN-12)
- **Decisión**: Generar el archivo de revisión vacío con `alembic revision -m "movimiento_stock_solo_agregado"` (**sin** `--autogenerate`), verificando que `down_revision = 'be806bc23837'`.
- **Fundamento (Consigna pág. 10 § Ejercicio 2 y pág. 12 § Ejercicio 7; Cátedra `cap4` §4.10–4.11 y `cap6` §6.9)**: La comparación automática de Alembic compara metadatos de tablas/columnas/índices de SQLAlchemy contra el catálogo, pero no inspecciona funciones PL/pgSQL ni disparadores. El comentario en el encabezado de la migración debe dejar constancia expresa de que se escribió a mano y fue leída antes de aplicarse por esa razón.
- **SQL del `upgrade()`**:
  1. Función `rechazar_modificacion_movimiento_stock()` que ejecuta `RAISE EXCEPTION 'movimiento_stock es de sólo agregado: no se permite % sobre sus filas (RN-12)', TG_OP USING ERRCODE = 'integrity_constraint_violation';` (o excepción PL/pgSQL estándar `P0001`).
  2. Disparador `CREATE TRIGGER trg_movimiento_stock_solo_agregado BEFORE UPDATE OR DELETE ON movimiento_stock FOR EACH ROW EXECUTE FUNCTION rechazar_modificacion_movimiento_stock();`.
- **SQL del `downgrade()`**:
  1. `DROP TRIGGER IF EXISTS trg_movimiento_stock_solo_agregado ON movimiento_stock;`
  2. `DROP FUNCTION IF EXISTS rechazar_modificacion_movimiento_stock();`
  *(En ese orden: PostgreSQL no permite borrar una función mientras un disparador dependa de ella).*
- **Código de error: `P0001` (confirmado por la integrante en `/opsx:apply`, 04/11/2026)**: el `RAISE EXCEPTION` queda sin `ERRCODE` propio. Alcanza porque ningún endpoint hace `UPDATE` ni `DELETE` sobre `movimiento_stock`: el disparador protege contra el acceso directo por `psql`, que es lo que demuestra C-14. Por eso no hace falta que el error llegue como `IntegrityError` ni que se traduzca a 409.
- **Por qué convive con `seed.py`**: En PostgreSQL, un disparador `BEFORE UPDATE OR DELETE ... FOR EACH ROW` se dispara en sentencias `UPDATE` y `DELETE`, pero **no** en `TRUNCATE`. Así la tabla rechaza cualquier edición o borrado de filas individuales y a la vez permite que `seed.py` vacíe el esquema con `TRUNCATE ... RESTART IDENTITY CASCADE` (DD-31).
- *Alternativa descartada*: Segundo mecanismo de `cap6` §6.9 (rol de base de datos sin permisos de `UPDATE`/`DELETE`). La consigna (pág. 12 § Ejercicio 7 y DD-07) explicita que no se pide porque el parcial usa un solo rol de base.

### D1 (1B) — Una sola contraseña ficticia en `PASSWORD_SEED` (`parcial/seed.py` y `parcial/README.md`)
- **Decisión**: Usar una única contraseña ficticia para los 5 usuarios del seed (`admin@example.com`, `admin2@example.com`, `vendedor@example.com`, `ana@example.com`, `nuevo@example.com`), declarada en una constante `PASSWORD_SEED = "Secreto1234!"` al comienzo de `parcial/seed.py`. **Corregido por la integrante en `/opsx:apply` (04/11/2026)**: el valor vive solo en `parcial/seed.py`; `parcial/README.md` y el aviso al grupo dicen "ver `PASSWORD_SEED` en `seed.py`", sin repetirlo (consigna pág. 19: las contraseñas "viven sólo en ese archivo").
- **Fundamento (Consigna pág. 19 § Datos iniciales)**: *"Las contraseñas son de mentira y viven sólo en ese archivo. Es parte de la puesta en marcha del proyecto y no un extra para probar."* Usar una sola constante evita que los 5 integrantes confundan qué contraseña corresponde a cada usuario al escribir los archivos `.http` de C-01 a C-16. El hash se calcula en `seed.py` con `bcrypt.hashpw(PASSWORD_SEED.encode("utf-8"), bcrypt.gensalt(rounds=settings.BCRYPT_COSTO)).decode("utf-8")` sin depender de `security.py` (CH-07).
- *Alternativa descartada (1A)*: Una contraseña distinta por rol/usuario.

### D2 (2A) — Correos y datos de los clientes en `parcial/seed.py`
- **Decisión**:
  - Cliente 1: `Lucía Fernández`, `email="lucia@example.com"`, `usuario_id=None`, con `PerfilCliente(telefono="261-4000001", direccion="Av. San Martín 123, Mendoza")`.
  - Cliente 2: `Tomás Ríos`, `email="tomas@example.com"`, `usuario_id=None`, sin perfil.
  - Cliente 3: `Ana Paz`, `email="ana@example.com"`, `usuario_id=4` (el `id` del usuario `ana@example.com`), sin perfil.
- **Fundamento (Consigna pág. 20 § Datos iniciales y pág. 21 § C-02; KB `04_modelo_de_datos.md`)**: La consigna fija los nombres y quién tiene perfil o usuario; fijar `tomas@example.com` y `lucia@example.com` da un correo predecible para que CH-08 (`C-02_registro.http`) pruebe el choque `409` al registrarse con el correo de un cliente existente sin usuario (RN-02).
- *Alternativa descartada (2B)*: Correos con apellido (`lucia.fernandez@example.com`).

### D3 (3B) — Eliminación de `parcial/scripts/seed.py` y `parcial/scripts/__init__.py`
- **Decisión**: Borrar `parcial/scripts/seed.py` y `parcial/scripts/__init__.py` (además de borrar `parcial/test/C-01.http`..`C-08.http` según DD-29) y actualizar `parcial/README.md` (paso 10 y notas) para que indique `python seed.py` en lugar de `python -m scripts.seed`. `despliegue/` no se toca.
- **Fundamento (Consigna pág. 8 § Estructura obligatoria y pág. 21 § Casos de prueba mínimos; IN-04)**: En `parcial/`, el único seed válido es `python seed.py` en la raíz (que carga la venta 1 por `69000.00`). Dejar `parcial/scripts/seed.py` (roto tras CH-01 y con total `71000.00`) induce a error.
- *Alternativa descartada (3A)*: Dejar `parcial/scripts/seed.py` roto sin borrarlo.

### D4 (4A) — `MENSAJES_CONSTRAINT` pre-cargado en `parcial/app/core/errores.py`
- **Decisión**: Pre-cargar desde CH-02 en `MENSAJES_CONSTRAINT` los **7 constraints de unicidad** creados en CH-01 (`uq_usuario_email`, `uq_cliente_email`, `uq_cliente_usuario_id`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn_vigente`, `uq_asignacion_rol_abierta`), más `ix_perfil_cliente_cliente_id` (nombre real en la base, corregido en `/opsx:apply`) y los CHECK/FK conocidos (`ck_libro_precio_positivo`, `ck_libro_stock_no_negativo`, `ck_movimiento_stock_cantidad_no_cero`, `ck_asignacion_rol_rol_valido`, `ck_libro_autor_orden_minimo`, `ck_libro_autor_rol_valido`, `ck_venta_total_no_negativo`, `ck_renglon_cantidad_positiva`, `ck_renglon_precio_unitario_positivo`).
- **Fundamento (Consigna pág. 8 § RN-15, Cátedra `cap4` §4.13)**: Evita que ningún error devuelva texto interno de la base y reduce al mínimo la necesidad de que CH-04, CH-05, CH-08, CH-12, CH-13 y CH-14 editen `app/core/errores.py` al mismo tiempo (menos conflictos de Git entre los 5 integrantes).
- *Alternativa descartada (4B)*: Dejar `MENSAJES_CONSTRAINT` vacío en CH-02.

### D5 (5A) — Firma de `traducir_integrity_error` en `parcial/app/core/errores.py`
- **Decisión**: `traducir_integrity_error(exc: IntegrityError, default: str = "Los datos enviados entran en conflicto con el estado actual") -> HTTPException` **devuelve** la instancia de `HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)` para que quien la invoque escriba `raise traducir_integrity_error(exc) from None`.
- **Extracción del nombre del constraint**: Primero intenta leer `exc.orig.__cause__.constraint_name` (corregido en `/opsx:apply`: SQLAlchemy envuelve el error de `asyncpg`, y el nombre exacto queda en `__cause__`, no en `exc.orig`); si no está o no coincide, busca si alguna clave de `MENSAJES_CONSTRAINT` aparece en `str(exc.orig)`; si ninguna coincide, usa `default`. En ningún caso concatena ni devuelve `str(exc)` ni `str(exc.orig)` (RN-15).
- *Alternativa descartada (5B)*: Hacer el `raise` adentro de la función.

### D6 (6A) — Firma y comportamiento de `add`, `update` y `delete` en `BaseRepository[T]`
- **Decisión**:
  - `async def add(self, entity: T) -> T`: hace `self.session.add(entity)`, `await self.session.flush()`, `await self.session.refresh(entity)` y devuelve `entity`.
  - `async def update(self, entity: T, cambios: dict[str, Any] | None = None) -> T`: si `cambios` no es `None`, aplica `for campo, valor in cambios.items(): setattr(entity, campo, valor)`; luego hace `self.session.add(entity)`, `await self.session.flush()`, `await self.session.refresh(entity)` y devuelve `entity`.
  - `async def delete(self, entity: T) -> None`: hace `await self.session.delete(entity)` y `await self.session.flush()`.
- **Fundamento (Consigna pág. 12 § Ejercicio 6; Cátedra `cap6` §6.4.4)**: *"add y update hacen flush(), nunca commit(): ningún repositorio confirma."* Que `update` acepte `cambios` opcional permite tanto pasarle `data.model_dump(exclude_unset=True)` directamente como mutar la entidad antes y llamar `await repo.update(entity)`.
- *Alternativa descartada (6B)*: `update(self, entity: T)` sin parámetro `cambios`.

### D7 (7B) — `BaseRepository[T]` y `SoftDeleteRepository[T]` mínimos (sin `where` ni `options` genéricos)
- **Decisión**: Mantener `BaseRepository[T]` y `SoftDeleteRepository[T]` estrictamente con los métodos de la consigna:
  - En `BaseRepository[T]`: `__init__(self, session: AsyncSession, model: type[T])`, `get_by_id(self, entity_id: int) -> T | None`, `get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]` (ordenado por `self.model.id`), `count(self) -> int`, `add`, `update`, `delete`.
  - En `SoftDeleteRepository[T](BaseRepository[T])`: redefine `get_by_id`, `get_all` y `count` filtrando `self.model.borrado_en.is_(None)`, y agrega `get_by_id_including_deleted(self, entity_id: int) -> T | None` y `soft_delete(self, entity: T) -> T` (que asigna `entity.borrado_en = datetime.now(timezone.utc)` y hace `flush()`).
  - **Sin** parámetros `where` ni `options` en la clase base.
- **Fundamento (Consigna pág. 12 § Ejercicio 6; Cátedra `cap6` §6.4.2, §6.4.3, §6.5)**: La consigna dice expresamente: *"Cada entidad tiene su repositorio, con métodos que se nombran por lo que traen, y la precarga se declara adentro del método que la necesita (sección 6.5)."* Si la clase base recibiera `options` o `where` desde afuera, la decisión de qué precargar o cómo filtrar se escaparía al Service en lugar de vivir adentro de un método con nombre propio del repositorio hijo.
- **Diferencia con el apunte (anotada por la integrante en `/opsx:apply`, 04/11/2026)**: el catálogo de `cap6-uow-transacciones.md` §6.4.4 trae `get_by_id(id, cargar)`, con un parámetro de carga en el método genérico. Acá no se adopta porque manda la consigna pág. 12: los métodos se nombran por lo que traen y la precarga se declara adentro del método que la necesita. Así, quien llama no decide qué se precarga: esa decisión queda en el repositorio hijo.
- *Alternativa descartada (7A)*: Parámetros genéricos `where` y `options` en `get_all`/`count`.

### D8 (8A) y D10 (10A) — Diseño de `parcial/app/core/paginacion.py` y validación temprana de `page > pages`
- **Decisión**: `parcial/app/core/paginacion.py` expone:
  1. `Pagina(SQLModel, Generic[T])`: schema genérico con `items: list[T]`, `total: int`, `page: int`, `size: int`, `pages: int`.
  2. `ParamsPaginacion`: clase inyectable por `Depends` con `page: Annotated[int, Query(ge=1)] = 1`, `size: Annotated[int, Query(ge=1, le=100)] = 20` y propiedad `@property def offset(self) -> int: return (self.page - 1) * self.size` (más alias `PaginacionDep = Annotated[ParamsPaginacion, Depends()]`).
  3. `calcular_paginas(total: int, size: int) -> int`: devuelve `1 if total == 0 else math.ceil(total / size)`.
  4. `validar_pagina(total: int, page: int, size: int) -> int`: calcula `pages = calcular_paginas(total, size)`; si `page > pages`, lanza `HTTPException(status_code=422, detail=f"La página {page} no existe: hay {pages}")` (literal: la constante está obsoleta en la versión instalada); si es válida, devuelve `pages`. Permite validar el rango **antes** de emitir el `SELECT` de los `items` (D10).
  5. `construir_pagina(items: Sequence[T], total: int, page: int, size: int) -> Pagina[T]`: llama a `pages = validar_pagina(total, page, size)` y devuelve `Pagina(items=list(items), total=total, page=page, size=size, pages=pages)`.
- **Fundamento (Consigna pág. 10 § Ejercicio 3 y pág. 19; Cátedra `cap2` §2.9; DD-24 / P-15)**: Cumple el contrato `{items, total, page, size, pages}`, `page >= 1`, `size` 1..100 (default 20), `total == 0 -> pages = 1` con lista vacía, y el mensaje exacto `"La página 4 no existe: hay 3"` con código 422 sin ejecutar la consulta de ítems cuando la página pedida excede el total de páginas.
- *Alternativa descartada (8B / 10B)*: Declarar `Query` a mano en cada router y validar recién después de consultar `items`.

### D9 (9) — Quién abre el `UnitOfWork` y quién traduce el `IntegrityError` (Consigna pág. 9 vs. Cátedra)
- **Decisión**:
  1. `UnitOfWork` (`parcial/app/core/unit_of_work.py`) recibe `session: AsyncSession`; `__aenter__` devuelve `self`; `__aexit__(self, exc_type, exc, tb)` hace `await self.session.rollback()` si `exc_type is not None` y `await self.session.commit()` si `exc_type is None`. **No cierra la sesión** y **no sabe nada de HTTP** (no importa `fastapi` ni atrapa `IntegrityError`).
  2. El **Service** recibe el UoW, lo abre con `async with uow:` y deja propagar cualquier `IntegrityError` (al salir del `async with`, `UnitOfWork.__aexit__` ejecuta `await self.session.rollback()`).
  3. El **Router** construye el UoW con una dependencia, llama al servicio dentro de `try: ... except IntegrityError as exc: raise traducir_integrity_error(exc) from None`, traduciendo el error de integridad a `409 Conflict`.
- **Fundamento (Consigna pág. 8–9 § Estructura obligatoria del proyecto vs. Cátedra `cap1` §1.10.1 y `cap2` §2.10)**: En el apunte de cátedra (`cap1` §1.10.1 y `cap2` §2.10) se comenta que en el TPI con manejador global *"el Router no traduce excepciones"*; sin embargo, la **consigna del parcial** (pág. 9, tabla *Estructura obligatoria del proyecto*) establece taxativamente para este examen:
  - `app/modules/<módulo>/service.py`: *"Las reglas de negocio. Recibe el Unit of Work y lo abre"*
  - `app/modules/<módulo>/router.py`: *"Rutas HTTP: construyen el Unit of Work, llaman al servicio y traducen errores"*
  Prevalece la consigna del parcial (confirmado por la integrante en D9). Documentar esta convención en el docstring de `unit_of_work.py` y `errores.py` asegura que CH-04 a CH-14 la apliquen de forma uniforme.
- *Alternativas descartadas (9A / 9B)*: Traducir `IntegrityError` dentro del `Service` o dentro de `UnitOfWork.__aexit__`.

## Risks / Trade-offs

- **[El `flush()` dentro de `add`/`update` lanza `IntegrityError` antes del `__aexit__`]** → Como la llamada a `repo.add()` o `repo.update()` ocurre dentro del bloque `async with uow:`, al dispararse `IntegrityError` en `flush()` Python invoca inmediatamente `uow.__aexit__(IntegrityError, exc, tb)`, que ejecuta `await self.session.rollback()` y deja propagar la excepción hacia el router, donde `except IntegrityError as exc: raise traducir_integrity_error(exc) from None` devuelve el 409 con la transacción ya revertida.
- **[En Windows el entorno del agente puede bloquear el borrado de archivos (`rm` / `Remove-Item`)]** → Ya ocurrió en CH-01 con `parcial/.env.example`. Si la herramienta del agente bloquea el borrado de `parcial/test/C-01..C-08.http` o `parcial/scripts/`, el agente le pasa el comando exacto a la integrante para que lo ejecute en su terminal y luego verifica con `git status`.
- **[Diferencia entre el seed del TP (`71000.00`) y el del parcial (`69000.00`)]** → Se elimina `parcial/scripts/` y se actualiza `parcial/README.md` en este mismo change (D1, D3) para que nadie ejecute el seed viejo en `parcial/`.

## Migration Plan

1. Con la base en la revisión 3 (`be806bc23837`), crear y aplicar la migración 4 (`alembic upgrade head`).
2. Probar la reversibilidad completa: `alembic downgrade base` → `alembic upgrade head` → `alembic check`.
3. Ejecutar `python seed.py` dos veces seguidas desde `parcial/`.
4. Rollback: `alembic downgrade -1` quita el disparador `trg_movimiento_stock_solo_agregado` y la función `rechazar_modificacion_movimiento_stock()`, dejando la base intacta en la revisión 3.

