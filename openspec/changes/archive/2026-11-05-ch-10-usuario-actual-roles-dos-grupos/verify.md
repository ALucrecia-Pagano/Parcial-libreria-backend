# Verificación: CH-10 — Usuario actual, roles y dos grupos de rutas

## Pruebas Ejecutadas

Se ejecutó `python seed.py` y se verificaron los casos de prueba C-01, C-03 y C-06 contra la base de datos real en PostgreSQL:

### Caso C-01: Parámetro de ruta no entero con sesión iniciada
Archivo: `parcial/test/C-01_param_no_entero.http`

| Petición | Código Esperado | Código Obtenido | Detalle de Respuesta |
|---|---|---|---|
| `POST /auth/login` (admin) | 200 OK | 200 OK | `{"mensaje": "Sesión iniciada", "debe_cambiar_password": false, "expira_en_segundos": 1800}` |
| `GET /libros/abc` (con cookie) | 422 Unprocessable | 422 Unprocessable | `{"detail": [{"loc": ["path", "libro_id"], "msg": "Input should be a valid integer...", "type": "int_parsing"}]}` |
| `GET /clientes/abc` (con cookie) | 422 Unprocessable | 422 Unprocessable | `{"detail": [{"loc": ["path", "cliente_id"], "msg": "Input should be a valid integer...", "type": "int_parsing"}]}` |

### Caso C-03: Exclusividad de la cookie HttpOnly y rechazo de cabecera Authorization
Archivo: `parcial/test/C-03_cookie.http`

| Petición | Código Esperado | Código Obtenido | Detalle de Respuesta |
|---|---|---|---|
| `GET /auth/yo` sin cookie | 401 Unauthorized | 401 Unauthorized | `{"detail": "No autenticado"}` |
| `GET /auth/yo` con Bearer | 401 Unauthorized | 401 Unauthorized | `{"detail": "No autenticado"}` |
| `GET /auth/yo` con cookie | 200 OK | 200 OK | `{"id": 1, "email": "admin@example.com", "nombre": "Admin Principal", "activo": true, "debe_cambiar_password": false, "roles_base": ["ADMIN"], "roles_token": ["ADMIN"]}` |

### Caso C-06: 401 vs 403, guardas de rol y usuario inactivo
Archivo: `parcial/test/C-06_401_vs_403.http`

| Petición | Código Esperado | Código Obtenido | Detalle de Respuesta |
|---|---|---|---|
| `POST /libros` sin sesión | 401 Unauthorized | 401 Unauthorized | `{"detail": "No autenticado"}` |
| `POST /libros` con vendedor | 403 Forbidden | 403 Forbidden | `{"detail": "Permisos insuficientes. Requiere uno de los siguientes roles: ['ADMIN']"}` |
| `POST /libros` con admin | 201 Created | 201 Created | `{"id": 6, "isbn": "978-950-00-0006-6", "titulo": "Los que aman, odian", ...}` |
| `GET /ventas` con cliente Ana | 403 Forbidden | 403 Forbidden | `{"detail": "Permisos insuficientes. Requiere uno de los siguientes roles: ['VENDEDOR', 'ADMIN']"}` |
| `GET /auth/yo` (usuario inactivo) | 401 Unauthorized | 401 Unauthorized | `{"detail": "Usuario no encontrado o inactivo"}` |
