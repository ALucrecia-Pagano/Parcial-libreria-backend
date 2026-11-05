# Verificación — CH-07 `security-login-cookie`

## Evidencia ejecutada

Servidor utilizado: `http://localhost:8000`  
Verificación realizada con REST Client sobre PostgreSQL local y la API
levantada con Uvicorn.

| Prueba | Esperado | Obtenido |
|---|---|---|
| C-03 login de `admin@example.com` | `200`, cookie `access_token`, cuerpo sin token | `200`; cookie con `HttpOnly`, `SameSite=lax`, `Max-Age=1800`; cuerpo con `mensaje`, `debe_cambiar_password=false` y `expira_en_segundos=1800` |
| C-03 login de `nuevo@example.com` | `200`, `debe_cambiar_password=true` | `200`; cuerpo con `debe_cambiar_password=true` y `expira_en_segundos=1800` |
| C-04 contraseña incorrecta para usuario existente | `401` y mensaje genérico | `401` con `{"detail":"Credenciales inválidas"}` |
| C-04 correo inexistente | `401` con el mismo cuerpo | `401` con `{"detail":"Credenciales inválidas"}` |
| C-04 contraseña de más de 72 bytes | `422` antes de bcrypt | `422` por validación del campo `password` |
| C-04 campo adicional | `422` por `extra="forbid"` | `422` con `type="extra_forbidden"` |

## Salidas relevantes

### C-03 — Login válido

```text
HTTP/1.1 200 OK
set-cookie: access_token=[REDACTED]; HttpOnly; Max-Age=1800; Path=/; SameSite=lax
```

```json
{
  "mensaje": "Sesión iniciada",
  "debe_cambiar_password": false,
  "expira_en_segundos": 1800
}
```

El segundo login respondió `200` con `debe_cambiar_password=true`.

### C-04 — Credenciales inválidas

Los dos casos respondieron:

```text
HTTP/1.1 401 Unauthorized
```

```json
{
  "detail": "Credenciales inválidas"
}
```

### C-04 — Contraseña demasiado larga

```text
HTTP/1.1 422 Unprocessable Entity
```

El error indicó que la contraseña supera los 72 bytes en UTF-8.

### C-04 — Campo adicional

```text
HTTP/1.1 422 Unprocessable Entity
```

El error indicó `extra_forbidden` para `campo_extra`.

## Observaciones

- Los valores de `access_token` fueron redactados; no se guarda ninguna
  credencial de sesión en la evidencia.
- Se confirmó que el cuerpo de login no contiene el token.
- REST Client mostró respuestas `401` en ambos casos de anti-enumeración, pero no
  se registraron mediciones numéricas de duración. La comparación temporal queda
  pendiente de una medición explícita si el auditor la exige.
