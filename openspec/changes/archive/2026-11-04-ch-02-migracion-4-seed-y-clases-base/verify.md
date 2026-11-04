# Verify — CH-02 `migracion-4-seed-y-clases-base`

Corrido el 04/11/2026 contra la base real `pg-parcial` (PostgreSQL en Docker, puerto 5433, base `libreria_parcial`), con el `.venv` de `parcial/`. Las salidas completas están al final de este archivo.

## Tabla de verificación

| Tarea | Prueba | Esperado | Obtenido |
|---|---|---|---|
| 1.1 rojo | `ls test scripts` | Están `C-01..C-08.http` y `scripts/` del TP | Están los 10 archivos |
| 1.3 verde | `ls`, `git status --short ../despliegue` | Solo `CH-01_salud.http`, sin `scripts/`, `despliegue/` intacto | Igual; `despliegue/` sin cambios |
| 2.1 rojo | psql en la revisión 3, con `ROLLBACK` | `UPDATE 1` y `DELETE 1`, sin disparador | `UPDATE 1`, `DELETE 1`, 0 disparadores |
| 2.3 | `upgrade head`, `downgrade base`, `upgrade head`, `check` | Sin errores; `No new upgrade operations detected.` | Igual (exit 0 en los cuatro) |
| 2.3 | `downgrade -1` y `upgrade head`, con `\d movimiento_stock` | El disparador y la función se van y vuelven | Función 0 y sin disparador; después función 1 y disparador activo |
| 2.4 verde | psql: `INSERT`, `UPDATE`, `DELETE` | `INSERT 0 1`; los otros dos, rechazados con el mensaje de RN-12 | Igual, mensajes exactos |
| 3.1 rojo | `python seed.py` | `[Errno 2] No such file or directory` | Igual (exit 2) |
| 3.3 verde | `python seed.py` dos veces | Ambas sin errores | Ambas exit 0 |
| 3.3 | psql: stock contra movimientos | ids 1..5; stock igual a la suma: 10, 5, 8, 3, 1 | Igual |
| 3.3 | psql: usuarios y roles | 5 usuarios, ids 1..5, `otorgada_por` nulo, hash bcrypt | Igual, prefijo `$2b$12$` en los 5 |
| 3.3 | psql: clientes, venta, evento | Ana Paz con `usuario_id` 4; venta 1 por 69000.00; actor `SISTEMA` | Igual |
| 3.3 | psql: disparador sobre filas del seed | `UPDATE` y `DELETE` rechazados; siguen las 7 filas | Rechazados; 7 filas, suma 27 |
| 3.4 | grep en `parcial/README.md` | Sin `scripts.seed`, `scripts/seed`, `71000`, `test/C-0`, ni el valor de la contraseña | Sin coincidencias (grep corrido durante el apply; su salida no quedó en la evidencia de abajo) |
| 4.1 rojo | `import app.core.errores` | `ModuleNotFoundError` | Igual |
| 4.3 verde | Nombre de editorial duplicado (real) | 409 `Ya existe una editorial con ese nombre`, sin texto de la base | Igual |
| 4.3 | Perfil duplicado (real) | 409 `El cliente ya tiene un perfil registrado` | Igual |
| 4.3 | Restricción desconocida y `NOT NULL` real | 409 con el mensaje genérico | Igual |
| 5.1 rojo | Importar los tres módulos | `ModuleNotFoundError` | Igual en los tres |
| 5.5 verde | `grep 'commit(' repository.py` | 0 | 0 (solo una mención en el docstring) |
| 5.5 | `BaseRepository[Editorial]` | `count` 3, ids `[1, 2]`, `add` con id y sin persistir tras `rollback` | Igual |
| 5.5 | `SoftDeleteRepository[Libro]` | La baja oculta el libro, `count` 4, la lectura histórica lo ve, `rollback` vuelve a 5 | Igual |
| 5.5 | `UnitOfWork` | Con excepción revierte, la propaga y deja la sesión abierta; sin excepción confirma | Igual, comprobado desde otra sesión |
| 5.5 | `construir_pagina` y `validar_pagina` | 5/2 da 3 páginas; vacío da 1; 422 con `La página 4 no existe: hay 3` y `La página 2 no existe: hay 1` | Igual |
| 5.5 | HTTP con app descartable | `page=0`, `size=0`, `size=101`, `size=500`, `page=abc`: 422; `size=100`: 200; `page=4&size=2`: 422 sin consultar ítems | Igual |
| 6.1 | `python seed.py` | Base con los datos iniciales | 3 editoriales (id máximo 3), 5 libros vigentes, 7 movimientos |
| 6.1 | `GET /health/live`, `GET /health/ready` | 200 `{"estado":"vivo"}`, 200 `{"estado":"lista"}` | Igual |
| 6.3 | `git status --short` | Solo archivos del alcance | Solo archivos del alcance, más `ch-03-despliegue-docker-vps/`, que no es de este change |
| 6.3 | `alembic check`, `alembic current` | Sin pendientes; en `head` | `No new upgrade operations detected.`; `33456ccaa692 (head)` |

## Lo que no se corrió

- **Tercer caso de `CH-01_salud.http`** (readiness con la base apagada, 503): la tarea 6.1 pide solo `live` y `ready`, y hacerlo exige detener `pg-parcial`. CH-02 no tocó la ruta de salud.

## Resuelto durante el apply, sin frenar

| Qué | Por qué |
|---|---|
| `status_code=422` literal en `paginacion.py`, en vez de `status.HTTP_422_UNPROCESSABLE_ENTITY` | La constante que nombra la tarea 5.4 emite una advertencia de obsoleta con la versión instalada, y su reemplazo no existe en el mínimo del stack (FastAPI 0.111). El código HTTP es el mismo |
| `ParamsPaginacion` con `Query(default=...)` en `__init__`, como la tarea 5.4 y no con `Annotated` como el ejemplo del `design.md` | Los dos dan el mismo contrato y los mismos 422; las pruebas HTTP lo confirman |
| Pruebas 5.5 en un script temporal fuera del repo, en vez de `python -c` | Eran demasiadas para una línea. No queda ningún `.py` de prueba en el repo (Regla 4); el script se copia abajo para poder repetirlo |
| `GET` de salud con `curl`, en vez de la extensión REST Client | Son los mismos pedidos de `CH-01_salud.http`, ejecutados desde la terminal para guardar la salida |
| Pruebas extra: perfil duplicado y `NOT NULL` en la 4.3; `update` y HTTP en la 5.5 | Cubren correcciones hechas durante el apply y el requisito de 422 de FastAPI |

## Cómo leer la evidencia

- **2.1** tiene dos intentos. El primero falló por un error del SQL de prueba, al que le faltaba `editorial.pais`; el `ROLLBACK` implícito no dejó nada. El rojo válido es el reintento.
- **2.4 y 3.3:** psql manda `ERROR` por stderr y el resto por stdout, así que los mensajes aparecen unas líneas corridos respecto de la sentencia que los causó.
- **4.3:** la línea `not null sin nombre` está mal rotulada: la prueba crea una editorial sin `pais`. El resultado no cambia.
- **5.5:** `add asigna id en flush 7` es correcto: las secuencias de PostgreSQL no retroceden con un `rollback`. El seed de la 6.1 las reinicia.

## Salidas completas

```text
=== 1.1 ROJO 2026-11-04 09:36:45
$ ls -la test scripts
scripts:
total 8
drwxr-xr-x 1 hp 197121    0 Nov  3 11:25 ./
drwxr-xr-x 1 hp 197121    0 Nov  4 08:39 ../
-rw-r--r-- 1 hp 197121    0 Nov  3 11:24 __init__.py
-rw-r--r-- 1 hp 197121 2941 Nov  3 11:24 seed.py

test:
total 17
drwxr-xr-x 1 hp 197121   0 Nov  3 17:21 ./
drwxr-xr-x 1 hp 197121   0 Nov  4 08:39 ../
-rw-r--r-- 1 hp 197121 160 Nov  3 11:24 C-01.http
-rw-r--r-- 1 hp 197121 235 Nov  3 11:24 C-02.http
-rw-r--r-- 1 hp 197121 241 Nov  3 11:24 C-03.http
-rw-r--r-- 1 hp 197121 364 Nov  3 11:24 C-04.http
-rw-r--r-- 1 hp 197121 260 Nov  3 11:24 C-05.http
-rw-r--r-- 1 hp 197121 354 Nov  3 11:24 C-06.http
-rw-r--r-- 1 hp 197121 347 Nov  3 11:24 C-07.http
-rw-r--r-- 1 hp 197121 207 Nov  3 11:24 C-08.http
-rw-r--r-- 1 hp 197121 409 Nov  3 17:21 CH-01_salud.http
$ grep (seed viejo)
21:                    raise RuntimeError("La carga inicial requiere una base vacía; no se borraron datos")

=== 1.3 VERDE 2026-11-04 09:49:22
$ ls -a test
./
../
CH-01_salud.http
$ ls scripts
ls: cannot access 'scripts': No such file or directory
$ ls ../despliegue/test ../despliegue/scripts
../despliegue/scripts:
__init__.py
seed.py

../despliegue/test:
C-01.http
C-02.http
C-03.http
C-04.http
C-05.http
C-06.http
C-07.http
C-08.http
$ git status --short ../despliegue
(fin status despliegue)

=== 2.1 ROJO 2026-11-04 09:49:52
SELECT version_num FROM alembic_version;
 version_num  
--------------
 be806bc23837
(1 row)

SELECT tgname FROM pg_trigger WHERE tgrelid = 'movimiento_stock'::regclass AND NOT tgisinternal;
 tgname 
--------
(0 rows)

BEGIN;
BEGIN
INSERT INTO usuario (email, nombre, password_hash, activo, debe_cambiar_password) VALUES ('rojo@example.com', 'Rojo', 'x', true, false);
INSERT 0 1
INSERT INTO editorial (nombre) VALUES ('Editorial Rojo');
ERROR:  null value in column "pais" of relation "editorial" violates not-null constraint
DETAIL:  Failing row contains (3, Editorial Rojo, null).

=== 2.1 ROJO (reintento con pais; el intento anterior falló por NOT NULL de editorial.pais en el SQL de prueba) 2026-11-04 09:50:06
BEGIN;
BEGIN
INSERT INTO usuario (email, nombre, password_hash, activo, debe_cambiar_password) VALUES ('rojo@example.com', 'Rojo', 'x', true, false);
INSERT 0 1
INSERT INTO editorial (nombre, pais) VALUES ('Editorial Rojo', 'Argentina');
INSERT 0 1
INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) VALUES ('978-000-ROJO', 'Libro Rojo', 100, 1, (SELECT id FROM editorial WHERE nombre = 'Editorial Rojo'));
INSERT 0 1
INSERT INTO movimiento_stock (libro_id, usuario_id, cantidad, motivo, cuando) VALUES ((SELECT id FROM libro WHERE isbn = '978-000-ROJO'), (SELECT id FROM usuario WHERE email = 'rojo@example.com'), 1, 'Prueba rojo', now());
INSERT 0 1
UPDATE movimiento_stock SET cantidad = 99;
UPDATE 1
DELETE FROM movimiento_stock;
DELETE 1
ROLLBACK;
ROLLBACK
SELECT count(*) AS movimientos_despues FROM movimiento_stock;
 movimientos_despues 
---------------------
                   0
(1 row)

SELECT count(*) AS usuarios_rojo FROM usuario WHERE email = 'rojo@example.com';
 usuarios_rojo 
---------------
             0
(1 row)


=== 2.3 2026-11-04 09:53:25
$ .venv/Scripts/python -m alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade be806bc23837 -> 33456ccaa692, movimiento stock solo agregado
[exit=0]
$ .venv/Scripts/python -m alembic downgrade base
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 33456ccaa692 -> be806bc23837, movimiento stock solo agregado
INFO  [alembic.runtime.migration] Running downgrade be806bc23837 -> 0f5ab569096b, acceso y movimiento stock
INFO  [alembic.runtime.migration] Running downgrade 0f5ab569096b -> 95dd46a75b66, Agrega tabla genero y relacion con libro
INFO  [alembic.runtime.migration] Running downgrade 95dd46a75b66 -> , esquema inicial sin genero
[exit=0]
$ .venv/Scripts/python -m alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 95dd46a75b66, esquema inicial sin genero
INFO  [alembic.runtime.migration] Running upgrade 95dd46a75b66 -> 0f5ab569096b, Agrega tabla genero y relacion con libro
INFO  [alembic.runtime.migration] Running upgrade 0f5ab569096b -> be806bc23837, acceso y movimiento stock
INFO  [alembic.runtime.migration] Running upgrade be806bc23837 -> 33456ccaa692, movimiento stock solo agregado
[exit=0]
$ .venv/Scripts/python -m alembic check
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
INFO  [alembic.ddl.postgresql] Detected sequence named 'intento_acceso_id_seq' as owned by integer column 'intento_acceso(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'movimiento_stock_id_seq' as owned by integer column 'movimiento_stock(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'editorial_id_seq' as owned by integer column 'editorial(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'perfil_cliente_id_seq' as owned by integer column 'perfil_cliente(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'genero_id_seq' as owned by integer column 'genero(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'usuario_id_seq' as owned by integer column 'usuario(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'evento_seguridad_id_seq' as owned by integer column 'evento_seguridad(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'asignacion_rol_id_seq' as owned by integer column 'asignacion_rol(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'cliente_id_seq' as owned by integer column 'cliente(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'venta_id_seq' as owned by integer column 'venta(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'autor_id_seq' as owned by integer column 'autor(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'renglon_venta_id_seq' as owned by integer column 'renglon_venta(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'libro_id_seq' as owned by integer column 'libro(id)', assuming SERIAL and omitting
No new upgrade operations detected.
[exit=0]
--- reversibilidad puntual
$ .venv/Scripts/python -m alembic downgrade -1
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 33456ccaa692 -> be806bc23837, movimiento stock solo agregado
[exit=0]
$ docker exec pg-parcial psql -U postgres -d libreria_parcial -c \d movimiento_stock
                                       Table "public.movimiento_stock"
   Column   |           Type           | Collation | Nullable |                   Default                    
------------+--------------------------+-----------+----------+----------------------------------------------
 id         | integer                  |           | not null | nextval('movimiento_stock_id_seq'::regclass)
 libro_id   | integer                  |           | not null | 
 venta_id   | integer                  |           |          | 
 usuario_id | integer                  |           | not null | 
 cantidad   | integer                  |           | not null | 
 motivo     | character varying        |           | not null | 
 cuando     | timestamp with time zone |           | not null | 
Indexes:
    "movimiento_stock_pkey" PRIMARY KEY, btree (id)
    "ix_movimiento_stock_libro_id" btree (libro_id)
    "ix_movimiento_stock_usuario_id" btree (usuario_id)
    "ix_movimiento_stock_venta_id" btree (venta_id)
Check constraints:
    "ck_movimiento_stock_cantidad_no_cero" CHECK (cantidad <> 0)
Foreign-key constraints:
    "movimiento_stock_libro_id_fkey" FOREIGN KEY (libro_id) REFERENCES libro(id)
    "movimiento_stock_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    "movimiento_stock_venta_id_fkey" FOREIGN KEY (venta_id) REFERENCES venta(id)

[exit=0]
funcion_presente=0
$ .venv/Scripts/python -m alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade be806bc23837 -> 33456ccaa692, movimiento stock solo agregado
[exit=0]
$ docker exec pg-parcial psql -U postgres -d libreria_parcial -c \d movimiento_stock
                                       Table "public.movimiento_stock"
   Column   |           Type           | Collation | Nullable |                   Default                    
------------+--------------------------+-----------+----------+----------------------------------------------
 id         | integer                  |           | not null | nextval('movimiento_stock_id_seq'::regclass)
 libro_id   | integer                  |           | not null | 
 venta_id   | integer                  |           |          | 
 usuario_id | integer                  |           | not null | 
 cantidad   | integer                  |           | not null | 
 motivo     | character varying        |           | not null | 
 cuando     | timestamp with time zone |           | not null | 
Indexes:
    "movimiento_stock_pkey" PRIMARY KEY, btree (id)
    "ix_movimiento_stock_libro_id" btree (libro_id)
    "ix_movimiento_stock_usuario_id" btree (usuario_id)
    "ix_movimiento_stock_venta_id" btree (venta_id)
Check constraints:
    "ck_movimiento_stock_cantidad_no_cero" CHECK (cantidad <> 0)
Foreign-key constraints:
    "movimiento_stock_libro_id_fkey" FOREIGN KEY (libro_id) REFERENCES libro(id)
    "movimiento_stock_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    "movimiento_stock_venta_id_fkey" FOREIGN KEY (venta_id) REFERENCES venta(id)
Triggers:
    trg_movimiento_stock_solo_agregado BEFORE DELETE OR UPDATE ON movimiento_stock FOR EACH ROW EXECUTE FUNCTION rechazar_modificacion_movimiento_stock()

[exit=0]
funcion_presente=1
$ .venv/Scripts/python -m alembic current
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
33456ccaa692 (head)
[exit=0]

=== 2.4 VERDE 2026-11-04 09:54:05
BEGIN;
BEGIN
INSERT INTO usuario (email, nombre, password_hash, activo, debe_cambiar_password) VALUES ('verde@example.com', 'Verde', 'x', true, false);
INSERT 0 1
INSERT INTO editorial (nombre, pais) VALUES ('Editorial Verde', 'Argentina');
INSERT 0 1
INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) VALUES ('978-000-VERDE', 'Libro Verde', 100, 1, (SELECT id FROM editorial WHERE nombre = 'Editorial Verde'));
INSERT 0 1
INSERT INTO movimiento_stock (libro_id, usuario_id, cantidad, motivo, cuando) VALUES ((SELECT id FROM libro WHERE isbn = '978-000-VERDE'), (SELECT id FROM usuario WHERE email = 'verde@example.com'), 1, 'Prueba verde', now());
INSERT 0 1
ROLLBACK;
ROLLBACK
BEGIN;
BEGIN
INSERT INTO usuario (email, nombre, password_hash, activo, debe_cambiar_password) VALUES ('verde@example.com', 'Verde', 'x', true, false);
INSERT 0 1
INSERT INTO editorial (nombre, pais) VALUES ('Editorial Verde', 'Argentina');
INSERT 0 1
INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) VALUES ('978-000-VERDE', 'Libro Verde', 100, 1, (SELECT id FROM editorial WHERE nombre = 'Editorial Verde'));
INSERT 0 1
INSERT INTO movimiento_stock (libro_id, usuario_id, cantidad, motivo, cuando) VALUES ((SELECT id FROM libro WHERE isbn = '978-000-VERDE'), (SELECT id FROM usuario WHERE email = 'verde@example.com'), 1, 'Prueba verde', now());
INSERT 0 1
UPDATE movimiento_stock SET cantidad = 99;
ROLLBACK;
ROLLBACK
BEGIN;
BEGIN
INSERT INTO usuario (email, nombre, password_hash, activo, debe_cambiar_password) VALUES ('verde@example.com', 'Verde', 'x', true, false);
ERROR:  movimiento_stock es de sólo agregado: no se permite UPDATE sobre sus filas (RN-12)
CONTEXT:  PL/pgSQL function rechazar_modificacion_movimiento_stock() line 3 at RAISE
INSERT 0 1
INSERT INTO editorial (nombre, pais) VALUES ('Editorial Verde', 'Argentina');
INSERT 0 1
INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) VALUES ('978-000-VERDE', 'Libro Verde', 100, 1, (SELECT id FROM editorial WHERE nombre = 'Editorial Verde'));
INSERT 0 1
INSERT INTO movimiento_stock (libro_id, usuario_id, cantidad, motivo, cuando) VALUES ((SELECT id FROM libro WHERE isbn = '978-000-VERDE'), (SELECT id FROM usuario WHERE email = 'verde@example.com'), 1, 'Prueba verde', now());
INSERT 0 1
DELETE FROM movimiento_stock;
ERROR:  movimiento_stock es de sólo agregado: no se permite DELETE sobre sus filas (RN-12)
CONTEXT:  PL/pgSQL function rechazar_modificacion_movimiento_stock() line 3 at RAISE
ROLLBACK;
ROLLBACK
SELECT count(*) AS movimientos_despues FROM movimiento_stock;
 movimientos_despues 
---------------------
                   0
(1 row)


=== 3.1 ROJO 2026-11-04 09:54:05
$ python seed.py
C:\Users\hp\OneDrive\Escritorio\PROGRAMACIONIII_GIULIANO\Parcial_Libreria\parcial\.venv\Scripts\python.exe: can't open file 'C:\\Users\\hp\\OneDrive\\Escritorio\\PROGRAMACIONIII_GIULIANO\\Parcial_Libreria\\parcial\\seed.py': [Errno 2] No such file or directory
[exit=2]

=== 3.3 VERDE 2026-11-04 09:57:50
$ python seed.py (1)
Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, 5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento.
[exit=0]
$ python seed.py (2)
Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, 5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento.
[exit=0]
SELECT l.id, l.titulo, l.stock, COALESCE(SUM(m.cantidad), 0) AS suma_movimientos FROM libro l LEFT JOIN movimiento_stock m ON m.libro_id = l.id GROUP BY l.id ORDER BY l.id;
 id |                titulo                 | stock | suma_movimientos 
----+---------------------------------------+-------+------------------
  1 | Rayuela                               |    10 |               10
  2 | Antología de la literatura fantástica |     5 |                5
  3 | Ficciones                             |     8 |                8
  4 | Respiración artificial                |     3 |                3
  5 | Bestiario                             |     1 |                1
(5 rows)

SELECT u.id, u.email, u.activo, u.debe_cambiar_password, r.rol, r.otorgada_por, r.revocada_en FROM usuario u JOIN asignacion_rol r ON r.usuario_id = u.id ORDER BY u.id;
 id |        email         | activo | debe_cambiar_password |   rol    | otorgada_por | revocada_en 
----+----------------------+--------+-----------------------+----------+--------------+-------------
  1 | admin@example.com    | t      | f                     | ADMIN    |              | 
  2 | admin2@example.com   | t      | f                     | ADMIN    |              | 
  3 | vendedor@example.com | t      | f                     | VENDEDOR |              | 
  4 | ana@example.com      | t      | f                     | CLIENTE  |              | 
  5 | nuevo@example.com    | t      | t                     | VENDEDOR |              | 
(5 rows)

SELECT left(password_hash, 7) AS prefijo_hash, count(*) FROM usuario GROUP BY 1;
 prefijo_hash | count 
--------------+-------
 $2b$12$      |     5
(1 row)

SELECT id, nombre, email, usuario_id FROM cliente ORDER BY id;
 id |     nombre      |       email       | usuario_id 
----+-----------------+-------------------+------------
  1 | Lucía Fernández | lucia@example.com |           
  2 | Tomás Ríos      | tomas@example.com |           
  3 | Ana Paz         | ana@example.com   |          4
(3 rows)

SELECT cliente_id, telefono, direccion FROM perfil_cliente;
 cliente_id |  telefono   |          direccion          
------------+-------------+-----------------------------
          1 | 261-4000001 | Av. San Martín 123, Mendoza
(1 row)

SELECT id, cliente_id, total FROM venta ORDER BY id;
 id | cliente_id |  total   
----+------------+----------
  1 |          1 | 69000.00
(1 row)

SELECT venta_id, libro_id, cantidad, precio_unitario FROM renglon_venta ORDER BY id;
 venta_id | libro_id | cantidad | precio_unitario 
----------+----------+----------+-----------------
        1 |        1 |        1 |        25000.00
        1 |        3 |        2 |        22000.00
(2 rows)

SELECT id, libro_id, venta_id, usuario_id, cantidad, motivo FROM movimiento_stock ORDER BY id;
 id | libro_id | venta_id | usuario_id | cantidad |    motivo     
----+----------+----------+------------+----------+---------------
  1 |        1 |          |          1 |       11 | Stock inicial
  2 |        2 |          |          1 |        5 | Stock inicial
  3 |        3 |          |          1 |       10 | Stock inicial
  4 |        4 |          |          1 |        3 | Stock inicial
  5 |        5 |          |          1 |        1 | Stock inicial
  6 |        1 |        1 |          3 |       -1 | Venta
  7 |        3 |        1 |          3 |       -2 | Venta
(7 rows)

SELECT id, actor, accion FROM evento_seguridad ORDER BY id;
 id |  actor  |            accion            
----+---------+------------------------------
  1 | SISTEMA | Carga de los datos iniciales
(1 row)

SELECT (SELECT count(*) FROM editorial) editoriales, (SELECT count(*) FROM genero) generos, (SELECT count(*) FROM autor) autores, (SELECT count(*) FROM libro_autor) libro_autor;
 editoriales | generos | autores | libro_autor 
-------------+---------+---------+-------------
           3 |       3 |       6 |           7
(1 row)

SELECT la.libro_id, a.nombre, la.rol, la.orden FROM libro_autor la JOIN autor a ON a.id = la.autor_id ORDER BY 1, 4;
 libro_id |       nombre        |   rol   | orden 
----------+---------------------+---------+-------
        1 | Julio Cortázar      | autor   |     1
        2 | Jorge Luis Borges   | coautor |     1
        2 | Silvina Ocampo      | coautor |     2
        2 | Adolfo Bioy Casares | coautor |     3
        3 | Jorge Luis Borges   | autor   |     1
        4 | Ricardo Piglia      | autor   |     1
        5 | Julio Cortázar      | autor   |     1
(7 rows)

UPDATE movimiento_stock SET cantidad = 99 WHERE id = 1;
DELETE FROM movimiento_stock WHERE id = 1;
ERROR:  movimiento_stock es de sólo agregado: no se permite UPDATE sobre sus filas (RN-12)
CONTEXT:  PL/pgSQL function rechazar_modificacion_movimiento_stock() line 3 at RAISE
ERROR:  movimiento_stock es de sólo agregado: no se permite DELETE sobre sus filas (RN-12)
CONTEXT:  PL/pgSQL function rechazar_modificacion_movimiento_stock() line 3 at RAISE
SELECT count(*) AS movimientos, sum(cantidad) AS suma FROM movimiento_stock;
 movimientos | suma 
-------------+------
           7 |   27
(1 row)


=== 4.1 ROJO 2026-11-04 09:58:42
$ python -c "from app.core.errores import MENSAJES_CONSTRAINT, traducir_integrity_error"
ModuleNotFoundError: No module named 'app.core.errores'

=== 4.3 VERDE 2026-11-04 10:02:32
unico: 409 Ya existe una editorial con ese nombre
indice perfil: 409 El cliente ya tiene un perfil registrado
not null sin nombre: 409 Los datos enviados entran en conflicto con el estado actual
desconocida: 409 Los datos enviados entran en conflicto con el estado actual
respaldo por texto: 409 Ya existe un género con ese nombre
OK 4.3
[exit=0]
editoriales=3
perfiles=1

=== 5.1 ROJO 2026-11-04 10:02:35
$ python -c "from app.core.repository import BaseRepository, SoftDeleteRepository"
ModuleNotFoundError: No module named 'app.core.repository'
$ python -c "from app.core.unit_of_work import UnitOfWork"
ModuleNotFoundError: No module named 'app.core.unit_of_work'
$ python -c "from app.core.paginacion import Pagina, ParamsPaginacion, validar_pagina, construir_pagina"
ModuleNotFoundError: No module named 'app.core.paginacion'

=== 5.5 VERDE 2026-11-04 10:08:33
$ grep -n commit app/core/repository.py
6:Ningún repositorio hace commit: add, update, delete y soft_delete solo hacen
$ grep commit( en repository.py:
0
--- 1. BaseRepository[Editorial]
OK   count == 3 
OK   get_all(0,2) ids [1,2] [1, 2]
OK   get_by_id(1) 
OK   add asigna id en flush 7
OK   count dentro de la transaccion == 4 
OK   update aplica cambios 
OK   tras rollback count == 3 
--- 2. SoftDeleteRepository[Libro]
OK   count == 5 
OK   get_by_id(1) None 
OK   count == 4 
OK   get_all sin el 1 
OK   including_deleted con borrado_en 2026-11-04 13:08:36.980914+00:00
OK   tras rollback count == 5 
--- 3. UnitOfWork
OK   la excepcion original se propaga 
OK   sesion sigue usable y count == 3 
OK   commit visible desde otra sesion, count == 4 
OK   borrada en segundo bloque, count == 3 
--- 4. paginacion
OK   5/2 -> pages 3 {'items': ['a', 'b'], 'total': 5, 'page': 1, 'size': 2, 'pages': 3}
OK   vacia -> pages 1 {'items': [], 'total': 0, 'page': 1, 'size': 20, 'pages': 1}
OK   La página 4 no existe: hay 3 (422, 'La página 4 no existe: hay 3')
OK   La página 2 no existe: hay 1 (422, 'La página 2 no existe: hay 1')
--- 5. HTTP: ParamsPaginacion y Pagina[T] con app descartable
OK   GET /x -> 200 200
OK   GET /x?page=0 -> 422 422
OK   GET /x?size=0 -> 422 422
OK   GET /x?size=101 -> 422 422
OK   GET /x?size=500 -> 422 422
OK   GET /x?size=100 -> 200 200
OK   GET /x?page=abc -> 422 422
OK   offset (2-1)*2 == 2 {'items': [{'id': 0}, {'id': 1}], 'total': 5, 'page': 2, 'size': 2, 'pages': 3}
OK   page 4 -> 422 mensaje exacto {'detail': 'La página 4 no existe: hay 3'}
OK   no se consultaron items (validacion temprana) 
schema OpenAPI incluye Pagina: ['Pagina_Salida_']
OK 5.5
[exit=0]

=== 6.1 2026-11-04 10:09:16
$ python seed.py
Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, 5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento.
[exit=0]
editoriales=3 max_id=3
libros_vigentes=5
movimientos=7
$ uvicorn app.main:app --port 8000
$ GET /health/live
HTTP/1.1 200 OK
{"estado":"vivo"}

$ GET /health/ready
HTTP/1.1 200 OK
{"estado":"lista"}

--- uvicorn.log
INFO:     Started server process [25704]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:52132 - "GET /health/live HTTP/1.1" 200 OK
INFO:     127.0.0.1:52135 - "GET /health/live HTTP/1.1" 200 OK
INFO:     127.0.0.1:52136 - "GET /health/ready HTTP/1.1" 200 OK

=== 6.3 alcance 2026-11-04 10:09:54
$ git status --short
 M parcial/README.md
 D parcial/scripts/__init__.py
 D parcial/scripts/seed.py
 D parcial/test/C-01.http
 D parcial/test/C-02.http
 D parcial/test/C-03.http
 D parcial/test/C-04.http
 D parcial/test/C-05.http
 D parcial/test/C-06.http
 D parcial/test/C-07.http
 D parcial/test/C-08.http
?? openspec/changes/ch-02-migracion-4-seed-y-clases-base/
?? openspec/changes/ch-03-despliegue-docker-vps/
?? parcial/app/core/errores.py
?? parcial/app/core/paginacion.py
?? parcial/app/core/repository.py
?? parcial/app/core/unit_of_work.py
?? parcial/migrations/versions/33456ccaa692_movimiento_stock_solo_agregado.py
?? parcial/seed.py
$ git status --short despliegue | wc -l
0
$ alembic check / current
No new upgrade operations detected.
33456ccaa692 (head)
$ commits nuevos desde dae0385 en esta tarea (no debe haber de CH-02)
26b9fc2 chore: ignorar skills generadas a partir de los comandos opsx
dae0385 feat(CH-01): configuración con Settings, modelos de acceso y stock, y migración 3
aa4d899 chore(fundacion): knowledge-base, roadmap, skills y reglas de agentes
```

## Script de la 5.5

```python
import asyncio, warnings
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from app.core.database import init_resources, dispose_resources
from app.core.repository import BaseRepository, SoftDeleteRepository
from app.core.unit_of_work import UnitOfWork
from app.core.paginacion import Pagina, PaginacionDep, construir_pagina, validar_pagina
from app.modules.editoriales.models import Editorial
from app.modules.libros.models import Libro

def ok(nombre, cond, valor=''):
    print(('OK  ' if cond else 'FALLA'), nombre, valor)
    assert cond, nombre

async def main():
    engine, fab = init_resources()
    try:
        print('--- 1. BaseRepository[Editorial]')
        async with fab() as s:
            r = BaseRepository(s, Editorial)
            ok('count == 3', await r.count() == 3)
            todos = await r.get_all(offset=0, limit=2)
            ok('get_all(0,2) ids [1,2]', [e.id for e in todos] == [1, 2], [e.id for e in todos])
            ok('get_by_id(1)', (await r.get_by_id(1)).nombre == 'Letras del Río')
            t = await r.add(Editorial(nombre='Temp', pais='Argentina'))
            ok('add asigna id en flush', t.id is not None, t.id)
            ok('count dentro de la transaccion == 4', await r.count() == 4)
            u = await r.update(t, {'pais': 'Chile'})
            ok('update aplica cambios', u.pais == 'Chile')
            await s.rollback()
            ok('tras rollback count == 3', await r.count() == 3)
        print('--- 2. SoftDeleteRepository[Libro]')
        async with fab() as s:
            r = SoftDeleteRepository(s, Libro)
            ok('count == 5', await r.count() == 5)
            l = await r.get_by_id(1)
            await r.soft_delete(l)
            ok('get_by_id(1) None', await r.get_by_id(1) is None)
            ok('count == 4', await r.count() == 4)
            ok('get_all sin el 1', [x.id for x in await r.get_all()] == [2, 3, 4, 5])
            h = await r.get_by_id_including_deleted(1)
            ok('including_deleted con borrado_en', h is not None and h.borrado_en is not None, h.borrado_en)
            await s.rollback()
            ok('tras rollback count == 5', await r.count() == 5)
        print('--- 3. UnitOfWork')
        async with fab() as s:
            uow = UnitOfWork(s)
            repo = BaseRepository(s, Editorial)
            try:
                async with uow:
                    await repo.add(Editorial(nombre='TempFalla', pais='Argentina'))
                    raise RuntimeError('fallo simulado')
            except RuntimeError as e:
                ok('la excepcion original se propaga', str(e) == 'fallo simulado')
            ok('sesion sigue usable y count == 3', await repo.count() == 3)
            async with uow:
                t = await repo.add(Editorial(nombre='TempOk', pais='Argentina'))
            tid = t.id
        async with fab() as s2:
            repo2 = BaseRepository(s2, Editorial)
            ok('commit visible desde otra sesion, count == 4', await repo2.count() == 4)
            async with UnitOfWork(s2):
                await repo2.delete(await repo2.get_by_id(tid))
        async with fab() as s3:
            ok('borrada en segundo bloque, count == 3', await BaseRepository(s3, Editorial).count() == 3)
    finally:
        await dispose_resources(engine)

    print('--- 4. paginacion')
    p = construir_pagina(['a', 'b'], total=5, page=1, size=2)
    ok('5/2 -> pages 3', (p.pages, p.total, p.page, p.size, p.items) == (3, 5, 1, 2, ['a', 'b']), p.model_dump())
    p = construir_pagina([], total=0, page=1, size=20)
    ok('vacia -> pages 1', (p.pages, p.total, p.items) == (1, 0, []), p.model_dump())
    for kw, msg in ((dict(total=5, page=4, size=2), 'La página 4 no existe: hay 3'),
                    (dict(total=0, page=2, size=20), 'La página 2 no existe: hay 1')):
        try:
            validar_pagina(**kw)
            ok(msg, False)
        except HTTPException as e:
            ok(msg, e.status_code == 422 and e.detail == msg, (e.status_code, e.detail))

    print('--- 5. HTTP: ParamsPaginacion y Pagina[T] con app descartable')
    class Salida(SQLModel):
        id: int
    app = FastAPI()
    consultas = []
    @app.get('/x', response_model=Pagina[Salida])
    async def x(params: PaginacionDep):
        total = 5
        validar_pagina(total, params.page, params.size)
        consultas.append(params.offset)
        return construir_pagina([Salida(id=i) for i in range(params.size)][:2], total, params.page, params.size)
    c = TestClient(app)
    for q, code in (('', 200), ('?page=0', 422), ('?size=0', 422), ('?size=101', 422), ('?size=500', 422), ('?size=100', 200), ('?page=abc', 422)):
        r = c.get('/x' + q)
        ok(f'GET /x{q} -> {code}', r.status_code == code, r.status_code)
    r = c.get('/x?page=2&size=2')
    ok('offset (2-1)*2 == 2', consultas[-1] == 2 and r.json()['pages'] == 3, r.json())
    n = len(consultas)
    r = c.get('/x?page=4&size=2')
    ok('page 4 -> 422 mensaje exacto', r.status_code == 422 and r.json() == {'detail': 'La página 4 no existe: hay 3'}, r.json())
    ok('no se consultaron items (validacion temprana)', len(consultas) == n)
    print('schema OpenAPI incluye Pagina:', [k for k in app.openapi()['components']['schemas'] if 'Pagina' in k])

warnings.simplefilter('error', DeprecationWarning) if False else None
asyncio.run(main())
print('OK 5.5')
```
