# Proposal

## Why

Para proteger al sistema contra ataques de fuerza bruta y denegación de servicio en el inicio de sesión, es necesario restringir los intentos fallidos consecutivos a un máximo de 5 por combinación de email e IP en una ventana móvil de 60 segundos (RN-07). Al alcanzar dicho umbral, el sistema debe responder de inmediato con código HTTP 429 y cabecera `Retry-After`, sin consumir recursos de CPU en cómputo de bcrypt. Asimismo, se debe registrar el historial de intentos en la tabla `intento_acceso` mediante una transacción independiente para que los fallos queden asentados aun cuando la petición de login termine en error.

## What Changes

- **Repositorio y Registro de Intentos (`app/modules/usuarios/repository.py`)**:
  - Implementación de `IntentoAccesoRepository` heredando de `BaseRepository[IntentoAcceso]`.
  - Método `contar_fallos_recientes(email, ip, ventana_segundos=60)`: cuenta fallos en los últimos 60 segundos ocurridos estrictamente después del último login exitoso (un éxito reinicia la cuenta de fallos).
  - Cálculo del tiempo restante en segundos para la expiración del intento fallido más antiguo en la ventana para proveer el valor de `Retry-After`.
  - Función `registrar_intento(session_factory, email, ip, exito)`: abre una sesión y transacción propia e independiente tomada de `app.state.session_factory`, asegurando que el intento sobreviva al ciclo de la petición.
- **Servicio de Autenticación (`app/modules/usuarios/service.py`)**:
  - En `login`, orden riguroso:
    1. Consulta previa de intentos fallidos para el `email` e `ip`.
    2. Si se alcanzaron 5 fallos: elevación inmediata de `HTTPException(429)` con cabecera `Retry-After`, sin ejecutar bcrypt y **sin registrar** el intento bloqueado por 429 en `intento_acceso` (P-14).
    3. Si no se superó el límite: ejecución del flujo de autenticación existente. Ante fallo (401), se asienta el registro con `exito=False`. Ante credenciales válidas, se asienta con `exito=True`.
- **Router (`app/modules/usuarios/router.py`)**:
  - Pasa la IP del cliente (`request.client.host`) y la fábrica de sesiones (`request.app.state.session_factory`) al servicio de login.
  - Asegura que ante código 429 la respuesta incluya la cabecera `Retry-After`.
- **Casos de Prueba**:
  - Creación de `parcial/test/C-05_limite_intentos.http` demostrando 5 fallos con 401, el 6º intento con 429 y `Retry-After`, ausencia del 429 en la tabla y reinicio de la ventana tras el paso del tiempo o login exitoso.

## Capabilities

### New Capabilities
<!-- Ninguna nueva -->

### Modified Capabilities
- `autenticacion-y-sesion`: Se incorporan los requisitos de limitación de tasa ante fallos reiterados (HTTP 429) y registro de auditoría independiente de intentos de acceso.

## Impact

- **APIs**: `POST /auth/login` puede retornar HTTP 429 con cabecera `Retry-After`.
- **Base de datos**: Escrituras concurrentes en la tabla `intento_acceso` en transacciones aisladas.
- **Rendimiento**: Se ahorra el cómputo de bcrypt (~250ms) en peticiones rechazadas por 429.
