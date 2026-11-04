# Spec Delta — esquema-de-datos

## ADDED Requirements

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

