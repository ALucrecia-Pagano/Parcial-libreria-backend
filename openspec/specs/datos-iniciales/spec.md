# datos-iniciales Specification

## Purpose

Define la puesta en marcha inicial y reproducible de la base de datos de `parcial/` mediante `seed.py` en la raíz del proyecto, dejando el estado exacto que esperan los casos de prueba C-01 a C-16 y garantizando el invariante contable del stock.

## Requirements

### Requirement: Vaciado y reinicio de identidades idempotente
El script `parcial/seed.py` SHALL vaciar todas las tablas del esquema mediante `TRUNCATE ... RESTART IDENTITY CASCADE` antes de insertar los datos iniciales, de modo que pueda ejecutarse múltiples veces seguidas sobre una base con datos —incluidos movimientos de stock protegidos por el disparador de sólo agregado— y los identificadores autogenerados arranquen siempre en `1`.

#### Scenario: Dos ejecuciones seguidas producen los mismos identificadores
- **GIVEN** la base está en `head` y ya tiene los datos iniciales cargados
- **WHEN** se ejecuta `python seed.py` por segunda vez consecutiva
- **THEN** el comando finaliza sin errores del disparador ni de unicidad, y los registros principales conservan sus identificadores fijos (`libro 1 = Rayuela`, `venta 1 = 69000.00`, `cliente 3 = Ana Paz`)

### Requirement: Usuarios iniciales, roles y contraseña ficticia única
El script `parcial/seed.py` SHALL crear los cinco usuarios iniciales de la consigna con una única contraseña ficticia declarada en la constante `PASSWORD_SEED` de `seed.py`, hasheada con `bcrypt` según el costo de la configuración, y con sus asignaciones de rol iniciales vigentes (`revocada_en` nulo y `otorgada_por` nulo).

#### Scenario: Cinco usuarios creados con sus roles y banderas
- **GIVEN** una base migrada a `head`
- **WHEN** se ejecuta `python seed.py`
- **THEN** existen los 5 usuarios activos (`admin@example.com` y `admin2@example.com` con rol `ADMIN`, `vendedor@example.com` con rol `VENDEDOR`, `ana@example.com` con rol `CLIENTE`, y `nuevo@example.com` con rol `VENDEDOR` y `debe_cambiar_password = true`, los otros cuatro con `false`), con `password_hash` en formato bcrypt y cada uno con su fila abierta en `asignacion_rol` (`otorgada_por` nulo)

### Requirement: Catálogo ficticio, clientes, venta inicial e invariante de stock
El script `parcial/seed.py` SHALL cargar las 3 editoriales, los 3 géneros, los 6 autores (el sexto sin libro), los 5 libros vigentes, los 3 clientes (dos sin acceso web y `Ana Paz` vinculada a `ana@example.com`), la venta 1 de Lucía Fernández por `69000.00` y los 7 movimientos de stock iniciales y de venta, cumpliendo en los cinco libros el invariante `libro.stock == SUM(movimiento_stock.cantidad)`.

#### Scenario: Invariante de stock frente a suma de movimientos en los cinco libros
- **GIVEN** se ejecutó `python seed.py`
- **WHEN** se consulta por cada libro su `stock` y la suma de `movimiento_stock.cantidad`
- **THEN** en los 5 libros (`1 Rayuela = 10`, `2 Antología de la literatura fantástica = 5`, `3 Ficciones = 8`, `4 Respiración artificial = 3`, `5 Bestiario = 1`) ambos valores coinciden exactamente y existen 7 filas en `movimiento_stock` (5 `"Stock inicial"` por `admin@example.com` con `+11, +5, +10, +3, +1` y 2 `"Venta"` por `vendedor@example.com` con `-1` y `-2` en la venta 1)

#### Scenario: Clientes con y sin acceso web y venta 1
- **GIVEN** se ejecutó `python seed.py`
- **WHEN** se consultan `cliente`, `perfil_cliente`, `venta` y `renglon_venta`
- **THEN** `Lucía Fernández` (`id = 1`, `lucia@example.com`) tiene perfil y `usuario_id` nulo, `Tomás Ríos` (`id = 2`, `tomas@example.com`) no tiene perfil ni usuario, `Ana Paz` (`id = 3`, `ana@example.com`) tiene `usuario_id` apuntando al usuario `ana@example.com`, y la venta 1 pertenece a Lucía con total `69000.00` (1 Rayuela + 2 Ficciones)

### Requirement: Registro de auditoría inicial del sistema y limpieza de archivos del TP
El script `parcial/seed.py` SHALL insertar una fila en `evento_seguridad` con `actor = 'SISTEMA'` y `accion = 'Carga de los datos iniciales'` (RN-16); además, en `parcial/` SHALL eliminarse el seed viejo del TP (`parcial/scripts/`) y los archivos `parcial/test/C-01.http` a `C-08.http` del TP.

#### Scenario: Evento inicial de seguridad registrado con actor SISTEMA
- **GIVEN** se ejecutó `python seed.py`
- **WHEN** se consulta la tabla `evento_seguridad`
- **THEN** existe una única fila con `actor = 'SISTEMA'` y `accion = 'Carga de los datos iniciales'`

#### Scenario: Ausencia de casos .http y seed heredados del TP en parcial/
- **GIVEN** el árbol de archivos de `parcial/`
- **WHEN** se listan `parcial/test/` y `parcial/`
- **THEN** no existen `C-01.http` a `C-08.http` del TP en `parcial/test/` (siguen en `despliegue/test/`) ni existe `parcial/scripts/seed.py`
