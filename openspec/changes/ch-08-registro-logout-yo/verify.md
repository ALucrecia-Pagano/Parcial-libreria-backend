# Verificación en vivo: CH-08 (`registro-logout-yo`)

## Entorno de Ejecución
- **Fecha**: 2026-11-05 14:34 UTC-3
- **Base de datos**: PostgreSQL 17 (localhost:5432, base: `libreria`)
- **Servidor API**: Uvicorn con FastAPI sobre `http://localhost:8000`
- **Suite ejecutada**: `parcial/test/C-02_registro.http`

---

## Evidencia de Pruebas de Integración (C-02)

### 1. Registro exitoso de nuevo cliente
- **Petición**: `POST /auth/registro`
  ```json
  {
    "nombre": "Carlos Alumno",
    "email": "carlos_alumno@example.com",
    "password": "Password123!"
  }
  ```
- **Código de estado**: `201 Created`
- **Cuerpo retornado**:
  ```json
  {
    "id": 6,
    "nombre": "Carlos Alumno",
    "email": "carlos_alumno@example.com",
    "cliente_id": 4,
    "mensaje": "Registro completado exitosamente"
  }
  ```
- **Comprobación**: `password_hash` omitido en el cuerpo de la respuesta.

### 2. Login con el usuario recién registrado
- **Petición**: `POST /auth/login` con credenciales de Carlos Alumno
- **Código de estado**: `200 OK`
- **Cabecera**: `Set-Cookie: access_token=...; HttpOnly; Path=/; SameSite=lax; Max-Age=1800`
- **Cuerpo retornado**:
  ```json
  {
    "mensaje": "Sesión iniciada",
    "debe_cambiar_password": false,
    "expira_en_segundos": 1800
  }
  ```

### 3. Registro con correo de usuario existente
- **Petición**: `POST /auth/registro` con `email: "carlos_alumno@example.com"`
- **Código de estado**: `409 Conflict`
- **Cuerpo retornado**:
  ```json
  {
    "detail": "Ya existe un usuario con ese email"
  }
  ```
- **Comprobación**: Se atrapa `IntegrityError` en `uq_usuario_email` sin consulta previa.

### 4. Registro con correo de cliente existente (Tomás Ríos, sin usuario vinculado)
- **Petición**: `POST /auth/registro` con `email: "tomas@example.com"`
- **Código de estado**: `409 Conflict`
- **Cuerpo retornado**:
  ```json
  {
    "detail": "Ya existe un cliente con ese email"
  }
  ```
- **Comprobación**: Se atrapa `IntegrityError` en `uq_cliente_email`. Transacción revertida en su totalidad.

### 5. Intento de inyectar rol en el payload
- **Petición**: `POST /auth/registro` con `{"rol": "ADMIN", ...}`
- **Código de estado**: `422 Unprocessable Entity`
- **Cuerpo retornado**:
  ```json
  {
    "detail": [
      {
        "type": "extra_forbidden",
        "loc": ["body", "rol"],
        "msg": "Extra inputs are not permitted",
        "input": "ADMIN"
      }
    ]
  }
  ```
- **Comprobación**: `extra="forbid"` rechaza campos arbitrarios.

### 6. Contraseña mayor a 72 bytes en UTF-8
- **Petición**: `POST /auth/registro` con 37 eñes (74 bytes UTF-8)
- **Código de estado**: `422 Unprocessable Entity`
- **Cuerpo retornado**:
  ```json
  {
    "detail": [
      {
        "type": "value_error",
        "loc": ["body", "password"],
        "msg": "Value error, La contraseña no puede superar los 72 bytes",
        "input": "ñññññññññññññññññññññññññññññññññññññ",
        "ctx": {"error": {}}
      }
    ]
  }
  ```
- **Comprobación**: `PasswordBcrypt` valida antes de invocar bcrypt; no genera 500.

### 7. Cierre de sesión sin sesión previa (idempotente)
- **Petición**: `POST /auth/logout` anónimo
- **Código de estado**: `200 OK`
- **Cabecera**: `Set-Cookie: access_token=; Max-Age=0; Path=/; HttpOnly; SameSite=lax`
- **Cuerpo retornado**:
  ```json
  {
    "mensaje": "Sesión cerrada exitosamente"
  }
  ```

### 8. Consulta de identidad sin sesión activa
- **Petición**: `GET /auth/yo` sin cookie
- **Código de estado**: `401 Unauthorized`
- **Cuerpo retornado**:
  ```json
  {
    "detail": "No autenticado"
  }
  ```

### 9. Consulta de identidad con sesión activa
- **Petición**: `GET /auth/yo` con cookie `access_token` de Carlos Alumno
- **Código de estado**: `200 OK`
- **Cuerpo retornado**:
  ```json
  {
    "id": 6,
    "email": "carlos_alumno@example.com",
    "nombre": "Carlos Alumno",
    "activo": true,
    "roles_base": ["CLIENTE"],
    "roles_token": ["CLIENTE"]
  }
  ```

### 10. Cierre de sesión autenticado
- **Petición**: `POST /auth/logout` con cookie
- **Código de estado**: `200 OK`
- **Cabecera**: `Set-Cookie: access_token=; Max-Age=0; Path=/; HttpOnly; SameSite=lax`

---

## Verificación de Integridad en Base de Datos

Consulta directa a PostgreSQL post-ejecución:
- **Tomás Ríos**:
  - `Cliente`: `id=2, usuario_id=None, nombre='Tomás Ríos', email='tomas@example.com'` (intacto, no apropiado).
  - `Usuario`: `select * from usuario where email='tomas@example.com'` -> `None` (no se crearon filas huérfanas tras el 409).
- **Carlos Alumno**:
  - `Usuario`: `id=6, email='carlos_alumno@example.com', activo=True, debe_cambiar_password=False`.
  - `AsignacionRol`: `usuario_id=6, rol='CLIENTE', revocada_en=None`.
  - `Cliente`: `id=4, usuario_id=6, nombre='Carlos Alumno', email='carlos_alumno@example.com'`.

### Resumen de Cumplimiento TDD con .http
| Tarea | Archivo / Endpoint | Código Esperado | Código Obtenido | Resultado |
|---|---|---|---|---|
| 1.1 / 3.1 | `POST /auth/registro` (nuevo) | 201 | 201 | PASS |
| 1.1 / 3.1 | `POST /auth/login` | 200 | 200 | PASS |
| 1.2 / 3.1 | `POST /auth/registro` (correo usuario existente) | 409 | 409 | PASS |
| 1.2 / 3.1 | `POST /auth/registro` (correo cliente existente) | 409 | 409 | PASS |
| 1.1 | `POST /auth/registro` (campo extra `rol`) | 422 | 422 | PASS |
| 1.1 | `POST /auth/registro` (clave 74 bytes) | 422 | 422 | PASS |
| 3.2 | `POST /auth/logout` (anónimo) | 200 | 200 | PASS |
| 3.3 | `GET /auth/yo` (anónimo) | 401 | 401 | PASS |
| 3.3 | `GET /auth/yo` (autenticado) | 200 | 200 | PASS |
| 3.2 | `POST /auth/logout` (autenticado) | 200 | 200 | PASS |

### Corrida adicional y comprobación SQL

En una corrida posterior, el primer registro de
`carlos_alumno@example.com` ya existía por una ejecución anterior. Por eso los
reintentos de ese registro respondieron `409 Conflict`, como exige la
restricción de unicidad. El login del usuario existente respondió `200 OK`, y
los casos de validación, logout y `/auth/yo` conservaron los códigos esperados.

Consultas ejecutadas:

```sql
SELECT id, email, usuario_id
FROM cliente
WHERE email IN ('carlos_alumno@example.com', 'tomas@example.com');

SELECT id, email
FROM usuario
WHERE email IN ('carlos_alumno@example.com', 'tomas@example.com');
```

Resultado:

```text
cliente:
 id |           email           | usuario_id
----+---------------------------+-----------
  2 | tomas@example.com         |
  4 | carlos_alumno@example.com | 6

usuario:
 id |           email
----+---------------------------
  6 | carlos_alumno@example.com
```

La salida confirma que Carlos tiene un único usuario y una única ficha
vinculada, mientras que Tomás continúa sin `usuario_id` y sin usuario asociado.
No se creó ningún usuario huérfano ni se apropió la ficha existente de Tomás.
