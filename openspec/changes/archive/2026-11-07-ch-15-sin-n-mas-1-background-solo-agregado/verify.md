# Verificación CH-15

2026-11-07. PostgreSQL 16 local, base `libreria`. API levantada con `SQL_ECHO=true`.

- `C-15_sin_n_mas_1.http`: 5/5. El detalle de la venta de 2 renglones y el de la de 4 renglones hicieron los mismos 4 SELECT (usuario, venta con cliente, renglones con libro, roles). No hay un SELECT por renglón. Evidencia en `parcial/evidencia/C-15-detalle-venta.txt`.
- El aviso del comprobante apareció en la consola después del 201 de cada alta.
- `solo_agregado.sql`: UPDATE y DELETE rechazados por el disparador. Evidencia en `parcial/evidencia/C-14-solo-agregado.txt`.
