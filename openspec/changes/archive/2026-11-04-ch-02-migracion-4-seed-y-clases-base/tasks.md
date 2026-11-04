# Tasks: CH-02 — Migración 4 (disparador de sólo agregado), `seed.py` nuevo y clases base

> **Governance nivel ALTO** (`CHANGES.md`): las tareas marcadas con **[revisión]** modifican una migración DDL escrita a mano, el script que trunca y recarga toda la base (`parcial/seed.py`), la limpieza de archivos heredados o las clases base compartidas de `parcial/app/core/`. Durante `/opsx:apply`, presentar el plan al integrante antes de escribir y parar a revisar en los puntos marcados.
>
> **Regla de alcance (Regla Propia 2 de `AGENTS.md`)**: este change **SOLO** puede tocar los siguientes archivos del repositorio:
> - **Crear (6)**:
>   1. `parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py` (con `down_revision = 'be806bc23837'`)
>   2. `parcial/seed.py`
>   3. `parcial/app/core/errores.py`
>   4. `parcial/app/core/repository.py`
>   5. `parcial/app/core/unit_of_work.py`
>   6. `parcial/app/core/paginacion.py`
> - **Modificar (1)**:
>   1. `parcial/README.md` (paso 10 de puesta en marcha, sección de datos iniciales con `PASSWORD_SEED` y nota de `seed.py` en la raíz)
> - **Eliminar (10)**:
>   1. `parcial/test/C-01.http` a `parcial/test/C-08.http` (8 archivos heredados del TP)
>   2. `parcial/scripts/seed.py` y `parcial/scripts/__init__.py` (2 archivos del seed viejo del TP)
> - **Evidencia de cierre (1)**:
>   1. `openspec/changes/ch-02-migracion-4-seed-y-clases-base/verify.md`
>
> **Correcciones aprobadas por la integrante durante `/opsx:apply` (04/11/2026)**: (1) las editoriales del seed llevan `pais="Argentina"`, porque `editorial.pais` es obligatoria; (2) las pruebas 4.3 y 5.5 crean las editoriales con `pais`; (3) los modelos están en `parcial/app/modules/*/models.py` (`parcial/app/models/` no existe); (4) los 6 autores del seed llevan `nacionalidad="Argentina"`, y en `libro_autor` los libros de un solo autor usan `rol="autor"`, `orden=1`, y la Antología `rol="coautor"`, `orden` 1, 2 y 3; (5) el valor de `PASSWORD_SEED` vive solo en `parcial/seed.py`: el README y el aviso al grupo dicen "ver `PASSWORD_SEED` en `seed.py`" (consigna pág. 19); (6) la tarea 6.1 espera `{"estado":"vivo"}` y `{"estado":"lista"}`, que es el contrato de `CH-01_salud.http`.
>
> **Prohibido tocar**: `despliegue/` (Regla Dura 3), migraciones 1, 2 y 3 (Regla Dura 10), `parcial/app/modules/*/models.py`, `parcial/app/core/config.py`, `parcial/app/core/database.py`, `parcial/app/main.py` o routers existentes.

---

## 1. Limpieza de archivos heredados del TP en `parcial/` (Punto 5 + D3)

- [x] 1.1 **ROJO (comprobación previa de residuos del TP)**: desde `parcial/`, listar el contenido de `parcial/test/` y `parcial/scripts/` y verificar en ROJO que todavía existen los 8 archivos viejos `C-01.http`..`C-08.http` del TP y el paquete viejo `scripts/seed.py` + `scripts/__init__.py` (que rechaza correr si hay datos y usa el esquema viejo sin `TRUNCATE` ni `movimiento_stock`). Guardar la salida para `verify.md`.
- [x] 1.2 **[revisión] Implementación (borrado de residuos en `parcial/`)**: eliminar exactamente `parcial/test/C-01.http`, `parcial/test/C-02.http`, `parcial/test/C-03.http`, `parcial/test/C-04.http`, `parcial/test/C-05.http`, `parcial/test/C-06.http`, `parcial/test/C-07.http`, `parcial/test/C-08.http`, `parcial/scripts/seed.py` y `parcial/scripts/__init__.py` (y remover el directorio `parcial/scripts/` si queda vacío). No tocar `parcial/test/CH-01_salud.http` ni nada dentro de `despliegue/`.
- [x] 1.3 **VERDE (verificación de limpieza)**: listar `parcial/test/`, verificar que únicamente existe `CH-01_salud.http`, comprobar que `parcial/scripts/` ya no existe, y listar `despliegue/test/` para confirmar que `despliegue/test/C-01.http`..`C-08.http` y `despliegue/scripts/seed.py` siguen intactos (Regla Dura 3).

---

## 2. Migración 4 escrita a mano: disparador de sólo agregado sobre `movimiento_stock` (Punto 1 + M4, RN-12)

- [x] 2.1 **ROJO (demostrar que en la revisión 3 `movimiento_stock` aún permite `UPDATE` y `DELETE`)**: con la base en la revisión 3 (`be806bc23837`), ejecutar en `psql` un bloque envuelto en `BEGIN; ... ROLLBACK;` que inserte una fila temporal en `usuario`, `editorial`, `libro` y `movimiento_stock`, y luego ejecute `UPDATE movimiento_stock SET cantidad = 99;` y `DELETE FROM movimiento_stock;`. Verificar en ROJO que ambas sentencias se ejecutan sin error (`UPDATE 1` y `DELETE 1`) porque el disparador de RN-12 todavía no existe. Guardar la salida para `verify.md`.
- [x] 2.2 **[revisión] Implementación de la migración 4 escrita a mano**:
  - Desde `parcial/`, generar el esqueleto vacío corriendo `alembic revision -m "movimiento_stock_solo_agregado"` (**sin** `--autogenerate`).
  - Editar el archivo generado `parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py` imitando el encabezado de `parcial/migrations/versions/be806bc23837_acceso_y_movimiento_stock.py`, verificando que `down_revision: Union[str, None] = 'be806bc23837'` (corregido en `/opsx:apply`: es el tipo que usan la migración 3 y la plantilla).
  - Incluir en el docstring del archivo la nota explícita de que esta migración fue escrita a mano y leída antes de aplicarse (Regla Dura 9) porque `--autogenerate` de Alembic no detecta funciones PL/pgSQL ni disparadores (`CREATE TRIGGER`).
  - Implementar `def upgrade() -> None:` con dos llamadas `op.execute(...)` separadas (asyncpg no acepta múltiples sentencias en un mismo comando preparado si no están separadas):
    1. `CREATE OR REPLACE FUNCTION rechazar_modificacion_movimiento_stock() RETURNS TRIGGER AS $$ BEGIN RAISE EXCEPTION 'movimiento_stock es de sólo agregado: no se permite % sobre sus filas (RN-12)', TG_OP; END; $$ LANGUAGE plpgsql;`
    2. `CREATE TRIGGER trg_movimiento_stock_solo_agregado BEFORE UPDATE OR DELETE ON movimiento_stock FOR EACH ROW EXECUTE FUNCTION rechazar_modificacion_movimiento_stock();`
  - Implementar `def downgrade() -> None:` en orden inverso:
    1. `op.execute("DROP TRIGGER IF EXISTS trg_movimiento_stock_solo_agregado ON movimiento_stock;")`
    2. `op.execute("DROP FUNCTION IF EXISTS rechazar_modificacion_movimiento_stock();")`
  - Leer el archivo completo antes de aplicarlo (Regla Dura 9).
- [x] 2.3 **Prueba del ciclo completo de migraciones y `alembic check`**:
  - Desde `parcial/`, ejecutar en orden:
    1. `alembic upgrade head`
    2. `alembic downgrade base`
    3. `alembic upgrade head`
    4. `alembic check` (debe responder `"No new upgrade operations detected."`)
  - Probar además la reversibilidad puntual de la migración 4: correr `alembic downgrade -1`, verificar con `psql -c "\d movimiento_stock"` que `trg_movimiento_stock_solo_agregado` ya no figura en la tabla, y volver a correr `alembic upgrade head` verificando con `psql -c "\d movimiento_stock"` que el disparador vuelve a estar activo (`BEFORE DELETE OR UPDATE ON movimiento_stock FOR EACH ROW EXECUTE FUNCTION rechazar_modificacion_movimiento_stock()`).
- [x] 2.4 **VERDE (demostrar en `psql` que `INSERT` pasa y `UPDATE`/`DELETE` son rechazados por `trg_movimiento_stock_solo_agregado`)**: ejecutar en `psql`:
  1. Un bloque `BEGIN; ... ROLLBACK;` que inserte un movimiento válido → verificar que responde `INSERT 0 1`.
  2. Dentro de una transacción de prueba, ejecutar `UPDATE movimiento_stock SET cantidad = 99;` → verificar en VERDE que falla con `ERROR: movimiento_stock es de sólo agregado: no se permite UPDATE sobre sus filas (RN-12)`.
  3. Ejecutar `DELETE FROM movimiento_stock;` → verificar en VERDE que falla con `ERROR: movimiento_stock es de sólo agregado: no se permite DELETE sobre sus filas (RN-12)`.
  Guardar las salidas exactas para `verify.md`.

---

## 3. `parcial/seed.py` nuevo en la raíz de `parcial/` y actualización de `parcial/README.md` (Punto 2 + D1, D2, D3)

- [x] 3.1 **ROJO (comprobar que `python seed.py` falla antes de crearlo)**: desde `parcial/`, ejecutar `python seed.py` y verificar en ROJO que falla con `can't open file '.../parcial/seed.py': [Errno 2] No such file or directory`.
- [x] 3.2 **[revisión] Implementación de `parcial/seed.py`**:
  - Crear `parcial/seed.py` en la raíz de `parcial/`, imitando cómo `parcial/app/core/database.py` usa `init_resources()` y `dispose_resources(engine)` para abrir y cerrar el motor asincrónico, e importando los modelos de `parcial/app/modules/*/models.py` (`Usuario`, `AsignacionRol`, `IntentoAcceso`, `EventoSeguridad`, `Editorial`, `Genero`, `Autor`, `Libro`, `LibroAutor`, `Cliente`, `PerfilCliente`, `Venta`, `RenglonVenta`, `MovimientoStock`).
  - Definir arriba del archivo la constante documentada (D1, Regla Dura 2):
    - `PASSWORD_SEED = "Secreto1234!"`
  - Definir `def _hash_password_seed() -> str:` que calcule una sola vez el hash bcrypt con `bcrypt.hashpw(PASSWORD_SEED.encode("utf-8"), bcrypt.gensalt(rounds=settings.BCRYPT_COSTO)).decode("utf-8")`.
  - Definir `async def seed() -> None:` que:
    1. Obtenga `engine, session_maker = init_resources()` y abra `async with session_maker() as session:` dentro de `try ... finally: await dispose_resources(engine)`.
    2. Ejecute como primera sentencia `await session.execute(text("TRUNCATE TABLE evento_seguridad, intento_acceso, movimiento_stock, renglon_venta, venta, perfil_cliente, cliente, libro_autor, libro, autor, genero, editorial, asignacion_rol, usuario RESTART IDENTITY CASCADE"))` (un `TRUNCATE` a nivel de tabla no dispara triggers `FOR EACH ROW` y reinicia todas las secuencias en `1`).
    3. Inserte los **5 usuarios** de la consigna (`knowledge-base/04_modelo_de_datos.md` § Seed data inicial) y sus **5 `AsignacionRol` vigentes** (`revocada_en=None`, `vence_en=None`, `otorgada_por=None`):
       - `id=1`: `admin@example.com` (`nombre="Admin Principal"`, `activo=True`, `debe_cambiar_password=False`, rol `"ADMIN"`)
       - `id=2`: `admin2@example.com` (`nombre="Admin Secundario"`, `activo=True`, `debe_cambiar_password=False`, rol `"ADMIN"`)
       - `id=3`: `vendedor@example.com` (`nombre="Vendedor Mostrador"`, `activo=True`, `debe_cambiar_password=False`, rol `"VENDEDOR"`)
       - `id=4`: `ana@example.com` (`nombre="Ana Paz"`, `activo=True`, `debe_cambiar_password=False`, rol `"CLIENTE"`)
       - `id=5`: `nuevo@example.com` (`nombre="Vendedor Nuevo"`, `activo=True`, `debe_cambiar_password=True`, rol `"VENDEDOR"`)
    4. Inserte las **3 editoriales ficticias** (`1: "Letras del Río"`, `2: "Ediciones del Plata Sur"`, `3: "Editorial Sudamérica Austral"`, las tres con `pais="Argentina"`), los **3 géneros** (`1: "Novela"`, `2: "Cuento"`, `3: "Antología"`), los **6 autores** (`1: "Julio Cortázar"`, `2: "Jorge Luis Borges"`, `3: "Silvina Ocampo"`, `4: "Adolfo Bioy Casares"`, `5: "Ricardo Piglia"`, `6: "Juan José Saer"` — sin libro en el seed; los seis con `nacionalidad="Argentina"`), y los **5 libros** con sus vínculos `LibroAutor`:
       - Libro 1: `"Rayuela"`, ISBN `"978-950-00-0001-1"`, precio `Decimal("25000.00")`, `stock=10`, editorial 1 (`Letras del Río`), género 1 (`Novela`), autor 1 (`Cortázar`).
       - Libro 2: `"Antología de la literatura fantástica"`, ISBN `"978-950-00-0002-8"`, precio `Decimal("30000.00")`, `stock=5`, editorial 2 (`Ediciones del Plata Sur`), género 3 (`Antología`), autores 2, 3 y 4 (`Borges`, `Ocampo`, `Bioy Casares`) con `rol="coautor"` y `orden` 1, 2 y 3 (los demás libros: `rol="autor"`, `orden=1`).
       - Libro 3: `"Ficciones"`, ISBN `"978-950-00-0003-5"`, precio `Decimal("22000.00")`, `stock=8`, editorial 3 (`Editorial Sudamérica Austral`), género 2 (`Cuento`), autor 2 (`Borges`).
       - Libro 4: `"Respiración artificial"`, ISBN `"978-950-00-0004-2"`, precio `Decimal("27000.00")`, `stock=3`, editorial 2 (`Ediciones del Plata Sur`), género 1 (`Novela`), autor 5 (`Piglia`).
       - Libro 5: `"Bestiario"`, ISBN `"978-950-00-0005-9"`, precio `Decimal("18000.00")`, `stock=1`, editorial 3 (`Editorial Sudamérica Austral`), género 2 (`Cuento`), autor 1 (`Cortázar`).
    5. Inserte los **3 clientes** (D2):
       - Cliente 1: `"Lucía Fernández"`, `email="lucia@example.com"`, `usuario_id=None`, con `PerfilCliente(telefono="261-4000001", direccion="Av. San Martín 123, Mendoza")`.
       - Cliente 2: `"Tomás Ríos"`, `email="tomas@example.com"`, `usuario_id=None`, sin perfil (usado en C-02).
       - Cliente 3: `"Ana Paz"`, `email="ana@example.com"`, `usuario_id=4` (el `id` del usuario `ana@example.com`), sin perfil.
    6. Inserte la **Venta 1** de Lucía Fernández (`cliente_id=1`, `total=Decimal("69000.00")`) con sus **2 renglones**:
       - `1 ×` `"Rayuela"` (`libro_id=1`, `cantidad=1`, `precio_unitario=Decimal("25000.00")`)
       - `2 ×` `"Ficciones"` (`libro_id=3`, `cantidad=2`, `precio_unitario=Decimal("22000.00")`)
    7. Inserte los **7 `MovimientoStock`** que justifican el stock actual de los 5 libros (RN-09):
       - 5 movimientos con `motivo="Stock inicial"`, `usuario_id=1` (`admin@example.com`), `venta_id=None`: libro 1 `+11`, libro 2 `+5`, libro 3 `+10`, libro 4 `+3`, libro 5 `+1`.
       - 2 movimientos con `motivo="Venta"`, `usuario_id=3` (`vendedor@example.com`), `venta_id=1`: libro 1 `-1`, libro 3 `-2`.
    8. Inserte el **`EventoSeguridad`** inicial (`actor="SISTEMA"`, `accion="Carga de los datos iniciales"`), haga `await session.commit()` e imprima un resumen claro por consola.
  - Agregar el bloque `if __name__ == "__main__": asyncio.run(seed())`.
- [x] 3.3 **VERDE (correr `python seed.py` DOS veces seguidas y verificar en `psql` idempotencia, invariante de stock y disparador sobre filas reales)**:
  - Desde `parcial/`, ejecutar `python seed.py` una primera vez y, sin tocar nada en el medio, ejecutar `python seed.py` una **segunda vez seguida**.
  - Ejecutar en `psql` las siguientes consultas y guardar la salida para `verify.md`:
    1. **Invariante de stock y reinicio de IDs en 1**:
       `SELECT l.id, l.titulo, l.stock, COALESCE(SUM(m.cantidad), 0) AS suma_movimientos FROM libro l LEFT JOIN movimiento_stock m ON m.libro_id = l.id GROUP BY l.id ORDER BY l.id;`
       → Verificar que los `id` son `1, 2, 3, 4, 5` y que en las 5 filas `stock == suma_movimientos` (`10, 5, 8, 3, 1`).
    2. **Usuarios y roles del seed**:
       `SELECT u.id, u.email, u.activo, u.debe_cambiar_password, r.rol, r.otorgada_por, r.revocada_en FROM usuario u JOIN asignacion_rol r ON r.usuario_id = u.id ORDER BY u.id;`
       → Verificar los 5 usuarios con IDs `1..5` (`admin@example.com`, `admin2@example.com`, `vendedor@example.com`, `ana@example.com`, `nuevo@example.com`), sus roles y `otorgada_por IS NULL`.
    3. **Clientes, venta y evento de seguridad**:
       `SELECT id, nombre, email, usuario_id FROM cliente ORDER BY id;`
       `SELECT id, cliente_id, total FROM venta ORDER BY id;`
       `SELECT id, actor, accion FROM evento_seguridad ORDER BY id;`
       → Verificar IDs arrancando en `1`, `ana@example.com` con `usuario_id = 4`, `venta 1` con `total = 69000.00` y `evento_seguridad 1` con `actor = 'SISTEMA'`.
    4. **Disparador sobre las filas reales del seed**:
       Ejecutar `UPDATE movimiento_stock SET cantidad = 99 WHERE id = 1;` y `DELETE FROM movimiento_stock WHERE id = 1;` → verificar que ambos son rechazados por `trg_movimiento_stock_solo_agregado` y que las 7 filas de `movimiento_stock` siguen intactas.
- [x] 3.4 **Actualización de `parcial/README.md` (D1, D3)**:
  - Editar `parcial/README.md`:
    1. En el paso 10 de "Puesta en marcha", reemplazar `python -m scripts.seed` y `71000.00` por `python seed.py` (aclarando que vacía la base con `TRUNCATE ... RESTART IDENTITY CASCADE` y que la venta inicial de Lucía Fernández totaliza `69000.00`: `1 × Rayuela + 2 × Ficciones`).
    2. Agregar una subsección "Datos iniciales (`seed.py`)" que liste los 5 usuarios de prueba, sus roles, su estado (`activo` / `debe_cambiar_password`) y que la contraseña ficticia común está en `PASSWORD_SEED` de `seed.py`, sin repetir su valor (D1, consigna pág. 19).
    3. En la sección "Entrega", actualizar la referencia a `scripts/seed.py` por `seed.py` en la raíz de `parcial/`.
    4. **Ampliación aprobada por la integrante durante `/opsx:apply` (04/11/2026)**: corregir las líneas de "Verificación y notas de integración" que el borrado de la tarea 1.2 deja desactualizadas: la que dice que `test/C-01.http` a `test/C-08.http` "se conservan sin cambios" debe aclarar que esos casos siguen solo en `despliegue/test/`, y la que indica ejecutar `test/C-07.http` debe dejar de nombrar un archivo que ya no existe en `parcial/`.
  - Verificar leyendo `parcial/README.md` que ya no queda ninguna mención a `scripts.seed`, `scripts/seed.py` ni `71000.00`.

---

## 4. Traducción de errores de integridad: `parcial/app/core/errores.py` (Punto 4 + D4, D5, D9, RN-15)

- [x] 4.1 **ROJO (comprobar que `app.core.errores` aún no existe)**: desde `parcial/`, ejecutar:
  `python -c "from app.core.errores import MENSAJES_CONSTRAINT, traducir_integrity_error"`
  y verificar en ROJO que falla con `ModuleNotFoundError: No module named 'app.core.errores'`.
- [x] 4.2 **[revisión] Implementación de `parcial/app/core/errores.py`**:
  - Crear `parcial/app/core/errores.py` según las decisiones D4, D5 y D9. La cátedra no trata la traducción de `IntegrityError`; lo más cercano es `docs/catedra/cap2-contratos.md` §2.10 (Errores: un formato normado), que dice que el Router no traduce: para este examen prevalece la consigna pág. 9 (D9).
  - Documentar en el docstring del módulo la decisión **D9** (consigna pág. 9, *Estructura obligatoria*): el servicio recibe el `UnitOfWork`, lo abre con `async with uow:` y deja propagar `IntegrityError` (para que `UnitOfWork.__aexit__` ejecute `rollback()` sin saber nada de HTTP); el **Router** atrapa `except IntegrityError as exc:` y ejecuta `raise traducir_integrity_error(exc) from None`.
  - Definir `MENSAJES_CONSTRAINT: dict[str, str]` con todas las restricciones conocidas del esquema de CH-01 (D4):
    - `"uq_usuario_email": "Ya existe un usuario con ese email"`
    - `"uq_cliente_email": "Ya existe un cliente con ese email"`
    - `"uq_cliente_usuario_id": "Ese usuario ya está vinculado a otro cliente"`
    - `"ix_perfil_cliente_cliente_id": "El cliente ya tiene un perfil registrado"` (corregido en `/opsx:apply`: es el nombre real en la base, un índice único)
    - `"uq_editorial_nombre": "Ya existe una editorial con ese nombre"`
    - `"uq_genero_nombre": "Ya existe un género con ese nombre"`
    - `"uq_libro_isbn_vigente": "Ya existe un libro activo con ese ISBN"`
    - `"uq_asignacion_rol_abierta": "El usuario ya tiene ese rol activo asignado"`
    - `"ck_libro_precio_positivo": "El precio del libro debe ser mayor a cero"`
    - `"ck_libro_stock_no_negativo": "El stock del libro no puede quedar negativo"`
    - `"ck_movimiento_stock_cantidad_no_cero": "La cantidad del movimiento de stock no puede ser cero"`
    - `"ck_asignacion_rol_rol_valido": "El rol indicado no es válido"`
    - `"ck_libro_autor_orden_minimo": "El orden del autor debe ser al menos 1"`
    - `"ck_libro_autor_rol_valido": "El rol del autor en el libro no es válido"`
    - `"ck_venta_total_no_negativo": "El total de la venta no puede ser negativo"`
    - `"ck_renglon_cantidad_positiva": "La cantidad del renglón debe ser mayor a cero"`
    - `"ck_renglon_precio_unitario_positivo": "El precio unitario del renglón debe ser mayor a cero"`
  - Definir `def _nombre_constraint(exc: IntegrityError) -> str | None:` que lea `orig.__cause__.constraint_name` (corregido en `/opsx:apply`: con asyncpg, `orig` no tiene `constraint_name` ni `diag`; el nombre exacto está en la excepción envuelta) y, como respaldo, busque si alguna clave de `MENSAJES_CONSTRAINT` aparece en `str(orig)`.
  - Definir `def traducir_integrity_error(exc: IntegrityError, default: str = "Los datos enviados entran en conflicto con el estado actual") -> HTTPException:` (D5) que devuelva `HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)` usando exclusivamente mensajes propios en castellano y nunca `str(exc)` ni `str(exc.orig)` (RN-15, Regla Dura 19).
- [x] 4.3 **VERDE (probar `traducir_integrity_error` contra un `IntegrityError` real de PostgreSQL y contra una restricción desconocida)**:
  - Desde `parcial/`, ejecutar un comando `python -c` de una línea que abra una sesión real contra PostgreSQL, intente insertar `Editorial(nombre="Letras del Río", pais="Argentina")` + `await session.flush()`, capture el `IntegrityError` real de asyncpg, haga `await session.rollback()`, invoque `http_exc = traducir_integrity_error(exc)` y verifique con `assert` que:
    1. `http_exc.status_code == 409`
    2. `http_exc.detail == "Ya existe una editorial con ese nombre"`
    3. `"asyncpg"` y `"duplicate key"` no aparecen en `http_exc.detail`
  - En el mismo comando, construir un `IntegrityError("stmt", {}, Exception("violates unique constraint uq_desconocida"))` y verificar que `traducir_integrity_error(exc_desconocida).detail == "Los datos enviados entran en conflicto con el estado actual"`. Guardar la salida impresa para `verify.md`.

---

## 5. Clases base de `parcial/app/core/`: `repository.py`, `unit_of_work.py` y `paginacion.py` (Punto 3 + D6, D7, D8, D9, D10)

- [x] 5.1 **ROJO (comprobar que `repository.py`, `unit_of_work.py` y `paginacion.py` aún no existen)**: desde `parcial/`, ejecutar:
  `python -c "from app.core.repository import BaseRepository, SoftDeleteRepository; from app.core.unit_of_work import UnitOfWork; from app.core.paginacion import Pagina, ParamsPaginacion, validar_pagina, construir_pagina"`
  y verificar en ROJO que falla con `ModuleNotFoundError`.
- [x] 5.2 **[revisión] Implementación de `parcial/app/core/repository.py` (D6, D7, Reglas Duras 7 y 17)**:
  - Crear `parcial/app/core/repository.py` siguiendo `docs/catedra/cap6-uow-transacciones.md` §6.4.1 (Qué separa), §6.4.2 (Dos jerarquías, y por qué no una), §6.4.3 (Los genéricos que se borran) y §6.4.4 (El catálogo de métodos), `docs/catedra/cap4-persistencia.md` §4.9 (Borrado lógico) y las decisiones D6 y D7 (consigna pág. 12: *"Cada entidad tiene su repositorio, con métodos que se nombran por lo que traen, y la precarga se declara adentro del método que la necesita"*).
  - Implementar `class BaseRepository(Generic[T]):` con:
    - `def __init__(self, session: AsyncSession, model: type[T]) -> None:`
    - `async def get_by_id(self, entity_id: int) -> T | None:` (`await self.session.get(self.model, entity_id)`)
    - `async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:` (`select(self.model).order_by(self.model.id).offset(offset).limit(limit)`)
    - `async def count(self) -> int:` (`select(func.count()).select_from(self.model)`)
    - `async def add(self, entity: T) -> T:` (`self.session.add(entity)`, `await self.session.flush()`, `await self.session.refresh(entity)`, retorna `entity`)
    - `async def update(self, entity: T, cambios: dict[str, Any] | None = None) -> T:` (si `cambios` no es `None`, aplica `setattr(entity, campo, valor)` por cada par, luego `self.session.add(entity)`, `await self.session.flush()`, `await self.session.refresh(entity)`, retorna `entity`)
    - `async def delete(self, entity: T) -> None:` (`await self.session.delete(entity)`, `await self.session.flush()`)
  - Implementar `class SoftDeleteRepository(BaseRepository[T]):` para modelos con columna `borrado_en: datetime | None` (`Libro`):
    - `async def get_by_id(self, entity_id: int) -> T | None:` (filtra `self.model.id == entity_id` y `self.model.borrado_en.is_(None)`)
    - `async def get_by_id_including_deleted(self, entity_id: int) -> T | None:` (`await self.session.get(self.model, entity_id)`)
    - `async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:` (filtra `self.model.borrado_en.is_(None)`, ordenado por `self.model.id`)
    - `async def count(self) -> int:` (`select(func.count()).select_from(self.model).where(self.model.borrado_en.is_(None))`)
    - `async def soft_delete(self, entity: T) -> T:` (asigna `entity.borrado_en = datetime.now(timezone.utc)`, hace `self.session.add(entity)`, `await self.session.flush()`, `await self.session.refresh(entity)`, retorna `entity`)
  - No incluir parámetros genéricos `where` ni `options`, y no invocar `commit()` en ningún método.
- [x] 5.3 **[revisión] Implementación de `parcial/app/core/unit_of_work.py` (D9, Regla Dura 7)**:
  - Crear `parcial/app/core/unit_of_work.py` siguiendo `docs/catedra/cap6-uow-transacciones.md` §6.6 (El Unit of Work) y §6.7 (Quién crea, quién abre, quién confirma y quién cierra), y la decisión D9.
  - Implementar `class UnitOfWork:` con:
    - `def __init__(self, session: AsyncSession) -> None:` (`self.session = session`)
    - `async def __aenter__(self) -> Self:` (`return self`)
    - `async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:` que ejecute `await self.session.rollback()` si `exc_type is not None` y `await self.session.commit()` si `exc_type is None` (sin cerrar `self.session`, que pertenece a `get_session`, y sin importar nada de `fastapi` ni atrapar `IntegrityError`).
- [x] 5.4 **[revisión] Implementación de `parcial/app/core/paginacion.py` (D8, D10, RN-14)**:
  - Crear `parcial/app/core/paginacion.py` siguiendo `docs/catedra/cap2-contratos.md` §2.9 (Colecciones: envoltorio, paginación y ordenamiento) y las decisiones D8 y D10.
  - Implementar:
    - `class Pagina(SQLModel, Generic[T]):` con `items: list[T]`, `total: int`, `page: int`, `size: int`, `pages: int`.
    - `class ParamsPaginacion:` con `__init__(self, page: int = Query(default=1, ge=1, description="Número de página (arranca en 1)"), size: int = Query(default=20, ge=1, le=100, description="Tamaño de página (1..100)")) -> None`, propiedad `@property def offset(self) -> int: return (self.page - 1) * self.size`, y alias `PaginacionDep = Annotated[ParamsPaginacion, Depends()]`.
    - `def calcular_paginas(total: int, size: int) -> int:` (`max(1, ceil(total / size))`).
    - `def validar_pagina(total: int, page: int, size: int) -> int:` que calcule `pages = calcular_paginas(total, size)` y, si `page > pages`, lance `HTTPException(status_code=422, detail=f"La página {page} no existe: hay {pages}")` (literal, corregido en `/opsx:apply`: la constante `HTTP_422_UNPROCESSABLE_ENTITY` está obsoleta en la versión instalada), o retorne `pages` en caso contrario (permitiendo validar antes de consultar `items` según D10).
    - `def construir_pagina(items: Sequence[T], total: int, page: int, size: int) -> Pagina[T]:` que llame a `pages = validar_pagina(total=total, page=page, size=size)` y retorne `Pagina(items=list(items), total=total, page=page, size=size, pages=pages)`.
- [x] 5.5 **VERDE (verificar `repository.py`, `unit_of_work.py` y `paginacion.py` contra la base real con datos del seed)**:
  - Verificar que `repository.py` no contiene llamadas a `commit()` (ni una sola ocurrencia ejecutable).
  - Desde `parcial/`, ejecutar pruebas con `python -c` contra la base cargada por `seed.py` y guardar la salida para `verify.md`:
    1. **`BaseRepository[Editorial]`**: comprobar `count() == 3`, `len(get_all(offset=0, limit=2)) == 2` con IDs `[1, 2]`, `get_by_id(1).nombre == "Letras del Río"`, y que `add(Editorial(nombre="Temp", pais="Argentina"))` asigna `id` en `flush()` pero tras `await session.rollback()` `count()` sigue siendo `3`.
    2. **`SoftDeleteRepository[Libro]`**: comprobar `count() == 5`; aplicar `soft_delete` al libro 1 (`Rayuela`), verificar en la misma sesión que `get_by_id(1)` devuelve `None`, `count() == 4`, y `get_by_id_including_deleted(1)` devuelve el libro con `borrado_en is not None`; hacer `await session.rollback()` y verificar que `count()` vuelve a ser `5`.
    3. **`UnitOfWork` (atomicidad)**: abrir `async with UnitOfWork(session):`, agregar una editorial temporal (con `pais="Argentina"`) y provocar un `RuntimeError("fallo simulado")` antes de salir; verificar que el `UnitOfWork` hace `rollback()`, deja la sesión abierta y en una consulta posterior la editorial temporal no existe (`count() == 3`). Probar también el camino sin excepción creando y borrando una editorial temporal (con `pais="Argentina"`) en dos bloques `async with UnitOfWork(session):` sucesivos.
    4. **`paginacion.py` (RN-14)**:
       - `construir_pagina(["a", "b"], total=5, page=1, size=2)` → `pages == 3, total == 5, page == 1, size == 2`.
       - `construir_pagina([], total=0, page=1, size=20)` → `pages == 1, total == 0, items == []`.
       - `validar_pagina(total=5, page=4, size=2)` → lanza `HTTPException` con `status_code == 422` y `detail == "La página 4 no existe: hay 3"`.
       - `validar_pagina(total=0, page=2, size=20)` → lanza `HTTPException` con `status_code == 422` y `detail == "La página 2 no existe: hay 1"`.

---

## 6. Regresión de salud (`CH-01_salud.http`), evidencia en `verify.md` y cierre

- [x] 6.1 **Recarga limpia del seed y prueba de no regresión con `parcial/test/CH-01_salud.http`**:
  - Correr `python seed.py` desde `parcial/` para asegurar que la base queda exactamente con los datos iniciales del seed.
  - Levantar `uvicorn app.main:app` y ejecutar los casos de `parcial/test/CH-01_salud.http` (`GET /health/live` y `GET /health/ready`), verificando que responden `200 OK` con `{"estado":"vivo"}` y `{"estado":"lista"}` respectivamente.
- [x] 6.2 **Crear `openspec/changes/ch-02-migracion-4-seed-y-clases-base/verify.md` (Regla Propia 1)**:
  - Documentar la tabla completa `tarea → prueba (.http / psql / python -c) → esperado → obtenido` y pegar todas las salidas reales en ROJO y en VERDE obtenidas en las tareas 1.1, 1.3, 2.1, 2.3, 2.4, 3.1, 3.3, 4.1, 4.3, 5.1, 5.5 y 6.1.
- [x] 6.3 **Verificación de alcance (`git status`) y resumen en criollo (Reglas Propias 2 y 3)**:
  - Ejecutar `git status` para confirmar que solo fueron creados, modificados o eliminados los archivos permitidos de este change.
  - Entregar el resumen en criollo de no más de 10 líneas explicando qué se hizo, qué archivos se tocaron y por qué, más el mensaje para avisar al grupo que `python seed.py` (contraseña: ver `PASSWORD_SEED` en `seed.py`) y `app/core/` ya están listos. No hacer commit (Regla Dura 1).

## Workflow follow-up

- Archivar el change con `/opsx:archive ch-02-migracion-4-seed-y-clases-base` y marcar `[x]` en `CHANGES.md` una vez revisado `verify.md` por la integrante.
