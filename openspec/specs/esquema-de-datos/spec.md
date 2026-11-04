# esquema-de-datos Specification

## Purpose

Define las tablas, columnas y restricciones que la base de datos de `parcial/` garantiza por sí misma (acceso, movimientos de stock, cambios en cliente y libro) y cómo ese esquema se crea y se revierte con migraciones versionadas.

## Requirements

### Requirement: Tabla usuario
La base SHALL tener la tabla `usuario` con `id`, `email`, `nombre`, `password_hash`, `activo` y `debe_cambiar_password`, sin columna `rol`; `email` SHALL ser único mediante el constraint `uq_usuario_email`.

#### Scenario: Correo de usuario repetido
- **WHEN** se inserta un segundo `usuario` con un `email` ya existente
- **THEN** la base rechaza la fila con una violación de `uq_usuario_email`

### Requirement: Tabla asignacion_rol con una sola asignación abierta por rol
La base SHALL tener `asignacion_rol` (`id`, `usuario_id`, `rol`, `desde`, `vence_en`, `revocada_en`, `otorgada_por`) con `rol` restringido a `ADMIN`, `VENDEDOR`, `CLIENTE` y el índice único parcial `uq_asignacion_rol_abierta` sobre `(usuario_id, rol)` donde `revocada_en IS NULL` (RN-03).

#### Scenario: Segunda asignación abierta del mismo rol
- **WHEN** un usuario ya tiene una asignación `VENDEDOR` con `revocada_en` nulo y se inserta otra `VENDEDOR` abierta
- **THEN** la base la rechaza por `uq_asignacion_rol_abierta`

#### Scenario: Reasignación tras revocar
- **WHEN** la asignación anterior tiene `revocada_en` con fecha y se inserta una nueva abierta del mismo rol
- **THEN** la base la acepta

#### Scenario: Rol inválido
- **WHEN** se inserta una asignación con `rol = 'SUPERUSUARIO'`
- **THEN** la base la rechaza por el CHECK de rol

#### Scenario: Otorgante opcional
- **WHEN** se inserta una asignación con `otorgada_por` nulo
- **THEN** la base la acepta (actor SISTEMA)

### Requirement: Tablas de auditoría aisladas
La base SHALL tener `intento_acceso` (`id`, `cuando`, `email`, `ip`, `exito`) con índice `(email, ip, cuando)` y `evento_seguridad` (`id`, `cuando`, `actor`, `accion`), ambas sin claves foráneas.

#### Scenario: Intento con correo inexistente
- **WHEN** se inserta un `intento_acceso` cuyo `email` no corresponde a ningún usuario
- **THEN** la base lo acepta

#### Scenario: Evento con actor SISTEMA
- **WHEN** se inserta un `evento_seguridad` con `actor = 'SISTEMA'`
- **THEN** la base lo acepta

### Requirement: Tabla movimiento_stock
La base SHALL tener `movimiento_stock` (`id`, `libro_id`, `venta_id`, `usuario_id`, `cantidad`, `motivo`, `cuando`) con `usuario_id` obligatorio, `venta_id` nulo permitido, CHECK `cantidad <> 0` e índice en cada clave foránea.

#### Scenario: Cantidad cero
- **WHEN** se inserta un movimiento con `cantidad = 0`
- **THEN** la base lo rechaza por el CHECK

#### Scenario: Movimiento sin usuario
- **WHEN** se inserta un movimiento con `usuario_id` nulo
- **THEN** la base lo rechaza

#### Scenario: Reposición sin venta
- **WHEN** se inserta un movimiento con `cantidad = 5`, `venta_id` nulo y un usuario existente
- **THEN** la base lo acepta

### Requirement: Cliente con acceso web opcional
`cliente` SHALL tener `usuario_id` nulo permitido, clave foránea a `usuario` y único por `uq_cliente_usuario_id`; `cliente.email` SHALL seguir siendo único por `uq_cliente_email`. Un cliente se vincula a lo sumo con un usuario y viceversa.

#### Scenario: Dos clientes con el mismo usuario
- **WHEN** se vincula un segundo cliente a un `usuario_id` ya usado
- **THEN** la base lo rechaza por `uq_cliente_usuario_id`

#### Scenario: Varios clientes sin usuario
- **WHEN** existen varios clientes con `usuario_id` nulo
- **THEN** la base los acepta

#### Scenario: Correo de cliente repetido
- **WHEN** se inserta un cliente con un `email` ya existente
- **THEN** la base lo rechaza por `uq_cliente_email`

### Requirement: Libro con baja lógica e ISBN único entre vigentes
`libro` SHALL tener `borrado_en` (timestamptz, nulo); el ISBN SHALL ser único solo entre libros con `borrado_en` nulo, mediante el índice único parcial `uq_libro_isbn_vigente` (RN-01). Siguen vigentes los CHECK de precio y stock.

#### Scenario: ISBN repetido entre vigentes
- **WHEN** existe un libro vigente con un ISBN y se inserta otro vigente con el mismo ISBN
- **THEN** la base lo rechaza por `uq_libro_isbn_vigente`

#### Scenario: Recargar un ISBN dado de baja
- **WHEN** el único libro con ese ISBN tiene `borrado_en` con fecha y se inserta uno nuevo vigente con el mismo ISBN
- **THEN** la base lo acepta

### Requirement: Nombres únicos de editorial y género con nombre explícito
La unicidad de `editorial.nombre` y `genero.nombre` SHALL estar garantizada por constraints llamados `uq_editorial_nombre` y `uq_genero_nombre` (RN-01), con el mismo nombre declarado en el modelo y en la base, de modo que la comparación automática no informe diferencias.

#### Scenario: Editorial repetida
- **WHEN** se inserta una editorial con un nombre ya existente
- **THEN** la base la rechaza nombrando el constraint `uq_editorial_nombre`

#### Scenario: Género repetido
- **WHEN** se inserta un género con un nombre ya existente
- **THEN** la base lo rechaza nombrando el constraint `uq_genero_nombre`

### Requirement: Navegación declarada en los dos extremos
Cada relación nueva SHALL poder navegarse desde los dos extremos: usuario↔cliente (objeto único de cada lado), usuario↔asignaciones propias, usuario↔asignaciones otorgadas, libro↔movimientos, venta↔movimientos y usuario↔movimientos. Asignar un extremo SHALL reflejarse en el otro.

#### Scenario: Usuario y cliente se ven como objetos únicos
- **WHEN** un cliente queda vinculado a un usuario
- **THEN** desde el cliente se obtiene ese usuario (un objeto, no una lista) y desde el usuario se obtiene ese cliente (un objeto, no una lista)

#### Scenario: Asignaciones propias y otorgadas
- **WHEN** el usuario A otorga a B una asignación de rol
- **THEN** la asignación figura entre las asignaciones de B, su otorgante es A y figura entre las asignaciones otorgadas por A

#### Scenario: Movimiento visible desde libro, venta y usuario
- **WHEN** existe un movimiento de stock de un libro, asociado a una venta y registrado por un usuario
- **THEN** el movimiento figura en los movimientos del libro, de la venta y del usuario, y desde el movimiento se llega a cada uno de los tres

#### Scenario: Movimiento sin venta
- **WHEN** un movimiento tiene `venta_id` nulo
- **THEN** su venta es nula y no figura en los movimientos de ninguna venta

### Requirement: Migración 3 reversible y documentada
El esquema anterior SHALL obtenerse solo con migraciones Alembic. La migración 3 SHALL seguir a la 2, declarar en un comentario que fue leída antes de aplicarse, llevar un comentario explicativo junto a cada corrección manual hecha sobre lo autogenerado, y permitir `upgrade head`, `downgrade base` y otra vez `upgrade head` sobre base vacía sin errores.

#### Scenario: Comentarios de lectura y de corrección
- **WHEN** se lee el archivo de la migración 3
- **THEN** su encabezado dice que fue leída antes de aplicarse y cada operación corregida a mano tiene al lado un comentario que explica qué generó el autogenerate y por qué se cambió

#### Scenario: Ida y vuelta completa
- **WHEN** sobre una base vacía se ejecuta `alembic upgrade head`, luego `alembic downgrade base` y luego `alembic upgrade head`
- **THEN** los tres comandos terminan sin error y el esquema final tiene las tablas y constraints de este spec

#### Scenario: Revertir solo la 3
- **WHEN** se ejecuta `alembic downgrade -1` desde la 3
- **THEN** desaparecen las tablas nuevas, `cliente.usuario_id` y `libro.borrado_en`, y `libro.isbn` vuelve a ser único sin predicado

#### Scenario: Sin diferencias pendientes
- **WHEN** tras `upgrade head` se ejecuta `alembic check`
- **THEN** no informa operaciones nuevas entre los modelos y la base

### Requirement: Movimientos de stock de sólo agregado por disparador
La tabla `movimiento_stock` SHALL ser de sólo agregado: un disparador de base de datos instalado por la cuarta migración SHALL rechazar cualquier `UPDATE` o `DELETE` sobre sus filas, venga de donde venga (RN-12), mientras que `INSERT` y `TRUNCATE` SHALL seguir permitidos.

#### Scenario: Rechazo de modificación de un movimiento existente
- **GIVEN** existe una fila en `movimiento_stock`
- **WHEN** se ejecuta un `UPDATE` sobre `movimiento_stock` cambiando su `cantidad` o su `motivo`
- **THEN** la base rechaza la operación con el error del disparador y la fila conserva sus valores originales

#### Scenario: Rechazo de borrado de un movimiento existente
- **GIVEN** existe una fila en `movimiento_stock`
- **WHEN** se ejecuta un `DELETE` sobre `movimiento_stock`
- **THEN** la base rechaza la operación con el error del disparador y la fila permanece en la tabla

#### Scenario: Inserción permitida de nuevos movimientos
- **GIVEN** existen un libro y un usuario en la base
- **WHEN** se ejecuta un `INSERT` en `movimiento_stock` con `cantidad` distinta de cero
- **THEN** la base acepta la fila sin intervención del disparador

### Requirement: Migración 4 escrita a mano y reversible
La cuarta migración SHALL seguir a la tercera (`be806bc23837`), estar escrita a mano (sin autogeneración) con un comentario que indique que fue leída antes de aplicarse y explique por qué la comparación automática no ve funciones ni disparadores, y SHALL revertir el disparador y la función en `downgrade` permitiendo `upgrade head`, `downgrade base` y `upgrade head` sin errores.

#### Scenario: Comentario de migración escrita a mano y leída
- **GIVEN** el archivo de la cuarta migración en `parcial/migrations/versions/`
- **WHEN** se inspecciona su contenido
- **THEN** declara `down_revision = 'be806bc23837'` y contiene un comentario explícito de que fue escrita a mano y leída antes de aplicarse porque la comparación automática no detecta funciones ni disparadores

#### Scenario: Reversión limpia de la cuarta migración
- **GIVEN** la base está en la cuarta migración (`head`)
- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** el disparador y su función desaparecen de la base y la tabla `movimiento_stock` continúa existiendo en la revisión 3

#### Scenario: Ida y vuelta completa hasta base y check limpio
- **GIVEN** la base tiene aplicadas las cuatro migraciones
- **WHEN** se ejecuta `alembic downgrade base`, luego `alembic upgrade head` y finalmente `alembic check`
- **THEN** los tres comandos terminan sin errores y `alembic check` informa que no hay operaciones pendientes
