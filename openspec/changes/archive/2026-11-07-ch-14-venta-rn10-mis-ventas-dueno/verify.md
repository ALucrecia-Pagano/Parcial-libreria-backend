# Verificación CH-14

2026-11-07. PostgreSQL 16 local, base `libreria`, API en http://127.0.0.1:8000.
`python seed.py` antes de cada archivo.

- `C-10_venta_valida.http`: 7/7. Venta 201, total 77000.00, stock de Rayuela 8 y de Respiración artificial 2, movimientos «Venta».
- `C-11_venta_sin_stock.http`: 4/4. 409 por stock, Rayuela sigue en 10 y sigue habiendo una sola venta.
- `C-12_venta_referencias_invalidas.http`: 10/10. Cliente o libro inválido y libro dado de baja dan 409. Libro repetido, renglones vacíos y `total` en el cuerpo dan 422. Sigue habiendo una sola venta.
- `C-06_401_vs_403.http`: los pedidos ejecutables coincidieron, incluida la venta de Ana (200 la propia, 403 la de Lucía, `GET /mis-ventas` solo la suya, `GET /ventas/9999` 404). El pedido de usuario desactivado queda como está en el archivo: pide un `UPDATE` manual y no se corrió.
