# Verificación: CH-12 — Roles con vigencia, autoprotección, alta de personal y eventos de seguridad

## Evidencia de Pruebas de Integración (PostgreSQL Real + Uvicorn)

Se ejecutaron los casos de prueba `parcial/test/C-07_revocar_rol.http` y `parcial/test/C-08_autoproteccion.http` contra el servidor FastAPI corriendo con Uvicorn y PostgreSQL 16 local (`citas-postgres` en puerto 5433).

### Matriz de Casos Verificados

#### 1. Caso C-07 (`C-07_revocar_rol.http`)

| Paso | Operación | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| 1 | `POST /auth/login` (vendedor) | 200 OK, Set-Cookie | 200 OK | OK |
| 2 | `POST /clientes` (con cookie vendedor) | 201 Created | 201 Created | OK |
| 3 | `POST /auth/login` (admin) | 200 OK, Set-Cookie | 200 OK | OK |
| 4 | `DELETE /usuarios/3/roles/VENDEDOR` (por admin) | 200 OK | 200 OK (`{"mensaje": "Rol revocado correctamente"}`) | OK |
| 5 | `POST /clientes` (misma cookie vendedor, sin reautenticar) | 403 Forbidden (RN-04) | 403 Forbidden | OK |
| 6 | `GET /auth/yo` (vendedor, misma cookie) | 200 OK: `roles_token=["VENDEDOR"]`, `roles_base=[]` | 200 OK | OK |
| 7 | `GET /usuarios/3/roles` (admin) | 200 OK, conserva fila con `revocada_en != null` | 200 OK (1 rol histórico con revocada_en) | OK |
| 8 | `POST /usuarios/3/roles` (`vence_en` en el pasado) | 422 Unprocessable Entity | 422 Unprocessable Entity | OK |
| 9 | `POST /usuarios/3/roles` (`vence_en` naive sin tzinfo) | 422 Unprocessable Entity | 422 Unprocessable Entity | OK |
| 10 | `POST /usuarios/3/roles` (válido con fecha futura) | 201 Created | 201 Created (`otorgada_por = 1`) | OK |
| 11 | `POST /usuarios/3/roles` (rol ya asignado abierto, RN-03) | 409 Conflict | 409 Conflict (`"El usuario ya tiene ese rol activo asignado"`) | OK |

#### 2. Caso C-08 (`C-08_autoproteccion.http`)

| Paso | Operación | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| 1 | `POST /auth/login` (Admin 1, id=1) | 200 OK | 200 OK | OK |
| 2 | `DELETE /usuarios/1/roles/ADMIN` (Admin 1 a sí mismo) | 409 Conflict (RN-05) | 409 Conflict (`"Un administrador no puede revocarse su propio rol ADMIN"`) | OK |
| 3 | `POST /auth/login` (Admin 2, id=2) | 200 OK | 200 OK | OK |
| 4 | `DELETE /usuarios/1/roles/ADMIN` (Admin 2 revoca a Admin 1) | 200 OK | 200 OK (`{"mensaje": "Rol revocado correctamente"}`) | OK |
| 5 | `DELETE /usuarios/2/roles/ADMIN` (Admin 2 revoca al último admin) | 409 Conflict (RN-05) | 409 Conflict (`"No se puede revocar el rol: no pueden quedar cero administradores vigentes en el sistema"`) | OK |
| 6 | `POST /usuarios` (contraseña provisoria > 72 bytes) | 422 Unprocessable Entity | 422 Unprocessable Entity | OK |
| 7 | `POST /usuarios` (alta de personal válida) | 201 Created | 201 Created (`debe_cambiar_password = true`) | OK |
| 8 | `POST /usuarios` (email duplicado) | 409 Conflict (RN-01) | 409 Conflict (`"Ya existe un usuario con ese email"`) | OK |
| 9 | `POST /auth/login` (nuevo personal creado) | 200 OK (`debe_cambiar_password = true`) | 200 OK | OK |
| 10 | `GET /eventos?page=1&size=10` (por ADMIN) | 200 OK, paginado cronológico inverso | 200 OK (total=5, items=5, último evento: "Alta de personal") | OK |
| 11 | `GET /eventos?size=500` (size > 100) | 422 Unprocessable Entity | 422 Unprocessable Entity | OK |
