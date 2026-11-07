# Verificación CH-13

2026-11-07. PostgreSQL 16 local, base `libreria`, API en http://127.0.0.1:8000.
Antes del archivo: `python seed.py`.

`parcial/test/CH-13_clientes.http`: 16 pedidos con código esperado, todos coincidieron.

- Alta 201 con `usuario_id` nulo.
- Mismo correo 409 «Ya existe un cliente con ese email».
- Cuerpo con `usuario_id` 422.
- Sin nombre 422.
- `GET /clientes/1` 200 con perfil y `usuario_id` nulo.
- `GET /clientes/3` 200 con `usuario_id`.
- `GET /clientes/9999` 404.
- PATCH parcial 200 y el correo no cambia.
- PATCH con correo ajeno 409.
- Perfil nuevo 201, repetido 409, cliente inexistente 404.
- Sin sesión 401. Ana (CLIENTE) 403.
