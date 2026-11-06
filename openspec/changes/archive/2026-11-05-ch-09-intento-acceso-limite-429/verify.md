# Verify — CH-09 `intento-acceso-limite-429`

Evidencia real ejecutada contra la API FastAPI (`uvicorn app.main:app`) y PostgreSQL 17 local (puerto 5432, base `libreria`) el 05/11/2026.
Dataset inicial restablecido previamente con `seed.py`.

---

## Tabla tarea → .http / comando → esperado → obtenido

| Tarea | .http / caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| **1.1 / 1.2** | Consulta inicial SQL | 0 filas para `vendedor@example.com` | `ESTADO INICIAL: 0 filas para vendedor@example.com` | ✅ PASÓ |
| **2.1 / 2.2** | Intentos 1 a 5 (`C-05_limite_intentos.http`) | Cinco respuestas `401 Unauthorized` con `{"detail":"Credenciales inválidas"}` y cómputo de bcrypt (~0.23-0.62s) | 5 respuestas 401 consecutivas (`INTENTO 1..5: HTTP 401`) | ✅ PASÓ |
| **2.1** | Intento 6 (`C-05_limite_intentos.http`) | `429 Too Many Requests`, cabecera `Retry-After: 59s`, respuesta instantánea (sin bcrypt, < 0.05s) | `INTENTO 6: HTTP 429 \| Retry-After: 59s \| Tiempo: 0.006s` | ✅ PASÓ |
| **1.2** | Verificación SQL tras Intento 6 | Exactamente 5 filas en `intento_acceso` con `exito = False`. El 6º intento (429) no se registra (P-14). | `Total filas = 5`. Filas 1 a 5 con `exito=False`. Ninguna fila para el intento 429. | ✅ PASÓ |
| **3.2** | Expiración de ventana (60s) + Login de recuperación | `200 OK`, cabecera `Set-Cookie: access_token=...; HttpOnly; SameSite=lax`, reinicio de ventana | `LOGIN EXITOSO: HTTP 200 \| Cookie emitida: True \| Tiempo: 0.509s` | ✅ PASÓ |
| **3.2** | Fallo posterior tras éxito | `401 Unauthorized` (no 429), demostrando que el éxito reinició la cuenta | `FALLO POSTERIOR: HTTP 401 (no 429) \| Body: {'detail': 'Credenciales inválidas'}` | ✅ PASÓ |
| **1.2** | Verificación final SQL | 7 filas totales en `intento_acceso` (5 fallos iniciales + 1 éxito + 1 fallo posterior) | `Total filas = 7` (5 fallos + 1 éxito + 1 fallo) | ✅ PASÓ |

---

## Salida Real de la Ejecución en Consola

```text
ESTADO INICIAL: 0 filas para vendedor@example.com

INTENTO 1: HTTP 401 | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.622s
INTENTO 2: HTTP 401 | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.227s
INTENTO 3: HTTP 401 | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.225s
INTENTO 4: HTTP 401 | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.230s
INTENTO 5: HTTP 401 | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.231s
INTENTO 6: HTTP 429 | Retry-After: 59s | Body: {'detail': 'Demasiados intentos fallidos. Intente más tarde.'} | Tiempo: 0.006s

VERIFICACIÓN BD TRAS INTENTO 6: Total filas = 5 (el 429 no se registra)
  id=1 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=2 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=3 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=4 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=5 | email=vendedor@example.com | ip=127.0.0.1 | exito=False

Esperando 60 segundos para que expire la ventana móvil de 60s...
LOGIN EXITOSO RECUPERACIÓN: HTTP 200 | Cookie emitida: True | Body: {'mensaje': 'Sesión iniciada', 'debe_cambiar_password': False, 'expira_en_segundos': 1800} | Tiempo: 0.509s
FALLO POSTERIOR (REINICIO CONTADOR): HTTP 401 (no 429) | Body: {'detail': 'Credenciales inválidas'} | Tiempo: 0.230s

VERIFICACIÓN FINAL BD: Total filas = 7
  id=1 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=2 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=3 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=4 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=5 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
  id=6 | email=vendedor@example.com | ip=127.0.0.1 | exito=True
  id=7 | email=vendedor@example.com | ip=127.0.0.1 | exito=False
```

---

## Log del Servidor Uvicorn durante la Prueba

```text
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 429 Too Many Requests
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 401 Unauthorized
```
