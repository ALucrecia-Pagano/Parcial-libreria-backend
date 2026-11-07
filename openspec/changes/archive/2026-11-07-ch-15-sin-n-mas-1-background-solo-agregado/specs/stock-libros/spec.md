# Spec Delta — stock-libros

## ADDED Requirements

### Requirement: Solo agregado demostrado en SQL
Un `UPDATE` y un `DELETE` sobre `movimiento_stock`, ejecutados en psql, SHALL ser rechazados por el disparador de la base. El proyecto SHALL incluir `parcial/test/solo_agregado.sql` con esas dos sentencias.

#### Scenario: Las dos sentencias fallan
- **WHEN** se corre cada sentencia de `solo_agregado.sql`
- **THEN** las dos terminan en error del disparador y la tabla queda igual
