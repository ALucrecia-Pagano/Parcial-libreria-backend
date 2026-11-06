# Verificación: CH-11 — Cambiar contraseña y cambio obligatorio

## Pruebas Ejecutadas

Se ejecutó `python seed.py` y se corrió la suite `parcial/test/C-09_cambio_obligatorio.http` contra la base de datos real en PostgreSQL:

### Caso C-09: Cambio obligatorio y auditoría
Archivo: `parcial/test/C-09_cambio_obligatorio.http`
Usuario de prueba: `nuevo@example.com` (inicialmente con `debe_cambiar_password = True`)

| Paso | Operación | Código Esperado | Código Obtenido | Resultado |
|---|---|---|---|---|
| 1 | `POST /auth/login` (nuevo@example.com) | 200 OK | 200 OK | `{"mensaje": "Sesión iniciada", "debe_cambiar_password": true, "expira_en_segundos": 1800}` |
| 2 | `GET /libros` (grupo abierto) | 200 OK | 200 OK | Petición pública permitida |
| 3 | `GET /auth/yo` | 200 OK | 200 OK | `{"debe_cambiar_password": true, ...}` |
| 4 | `GET /ventas` (grupo protegido) | 403 Forbidden | 403 Forbidden | `{"detail": "Debe cambiar su contraseña antes de operar en el sistema"}` |
| 5 | `POST /auth/cambiar-password` sin sesión | 401 Unauthorized | 401 Unauthorized | `{"detail": "No autenticado"}` |
| 6 | `POST /auth/cambiar-password` con contraseña actual incorrecta | 401 Unauthorized | 401 Unauthorized | `{"detail": "Contraseña actual incorrecta"}` (DD-30) |
| 7 | `POST /auth/cambiar-password` con clave > 72 bytes | 422 Unprocessable | 422 Unprocessable | Validador `PasswordBcrypt` rechaza longitud excesiva |
| 8 | `POST /auth/cambiar-password` exitoso | 200 OK | 200 OK | `{"mensaje": "Contraseña actualizada correctamente"}` |
| 9 | `GET /auth/yo` con la MISMA cookie | 200 OK | 200 OK | `{"debe_cambiar_password": false, ...}` |
| 10 | `GET /ventas` con la MISMA cookie | 200 OK | 200 OK | Desbloqueo inmediato sin relogueo |

### Verificación en Base de Datos (Auditoría RN-16)
Consulta:
```sql
SELECT actor, accion, cuando FROM evento_seguridad WHERE actor = 'nuevo@example.com';
```
Salida obtenida:
```
       actor       |        accion        |            cuando             
-------------------+----------------------+-------------------------------
 nuevo@example.com | Cambio de contraseña | 2026-11-06 00:07:50.185889+00
(1 row)
```
