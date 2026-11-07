-- C-14 · movimiento_stock es de solo agregado.
-- Correr cada sentencia por separado en psql, contra la base ya migrada y con seed.
-- Las dos las rechaza el disparador de la migración 4. No tienen que dejar cambios.

-- esperado: ERROR, el disparador no permite UPDATE
UPDATE movimiento_stock SET cantidad = cantidad WHERE id = 1;

-- esperado: ERROR, el disparador no permite DELETE
DELETE FROM movimiento_stock WHERE id = 1;
