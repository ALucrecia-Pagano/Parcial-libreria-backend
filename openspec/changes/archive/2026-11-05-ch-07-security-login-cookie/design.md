# Design

## Context

El modelo de datos y las migraciones necesarias para usuarios y asignación de roles fueron introducidos en CH-01, y el dataset inicial fue cargado en el seed de CH-02. La configuración del sistema (`app.core.config.settings`) ya define `JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO` y `COOKIE_SECURE`. Se requiere ahora dotar al sistema del núcleo de seguridad y autenticación mediante login con cookie. Ver `proposal.md` y `specs/autenticacion-y-sesion/spec.md`.

## Goals / Non-Goals

**Goals:**
- Proveer funciones criptográficas seguras y asíncronas (`hashear_password`, `verificar_password`) ejecutando bcrypt en hilos secundarios coordinados por un semáforo.
- Diseñar el tipo reutilizable `PasswordBcrypt` que valide el límite físico de 72 bytes de bcrypt respondiendo 422 ante desbordes.
- Implementar la emisión y decodificación de tokens JWT firmados con HMAC-SHA256 utilizando `PyJWT`.
- Precalcular un hash ficticio en el arranque de la aplicación (`app.state.hash_ficticio`) para mitigar ataques de enumeración y temporización.
- Implementar la capa de persistencia de usuarios: `UsuarioRepository` (búsqueda por email), `AsignacionRolRepository` (consulta de roles vigentes con filtro de fecha y revocación), `EventoSeguridadRepository` y `UsuariosUnitOfWork`.
- Implementar `POST /auth/login` con transporte exclusivo del token mediante la cookie HttpOnly `access_token`.

**Non-Goals:**
- Rate limiting por IP o email y registro de auditoría en `intento_acceso` (alcance específico de CH-09).
- Endpoints de auto-registro (`POST /auth/registro`), logout y consulta de identidad (`GET /auth/yo`) (alcance de CH-08).
- Extracción de usuario autenticado en dependencias (`get_usuario_actual`) y validación de roles vigentes en endpoints protegidos (alcance de CH-10).
- Flujo de cambio obligatorio de contraseña (`POST /auth/cambiar-password`) (alcance de CH-11).

## Decisions

### 1. Bcrypt en worker threads con semáforo
- **Decisión**: Ejecutar `bcrypt.hashpw` y `bcrypt.checkpw` delegándolos a `asyncio.to_thread` protegidos por una instancia global de `asyncio.Semaphore(4)`.
- **Razón**: Bcrypt es intensivo en CPU (~150-300 ms con factor de costo 12). Ejecutarlo de forma síncrona en el hilo principal bloquearía el event loop de FastAPI (violando EA-01). El semáforo limita la concurrencia para no saturar los cores de la CPU ni agotar el ThreadPoolExecutor ante ráfagas de autenticación.
- **Alternativas consideradas**: Usar `passlib` (desaconsejado por estar abandonado y tener incompatibilidades con versiones recientes de bcrypt) o ejecutar directo sin semáforo (riesgo de starvation del servidor).

### 2. Hash ficticio en `app.state` durante el Lifespan
- **Decisión**: Durante el `lifespan` en `app/main.py`, se invoca `hashear_password` con una clave arbitraria y se guarda el resultado en `app.state.hash_ficticio`.
- **Razón**: Si una petición envía un correo inexistente y el sistema retorna 401 de inmediato sin hashear, la respuesta tomaría ~5 ms frente a ~250 ms de un usuario existente, permitiendo a un atacante inferir qué correos están registrados (ataque de enumeración por tiempo). Al verificar contra el hash ficticio, ambas ramas consumen el mismo tiempo.

### 3. Verificación de hash fuera de la transacción de base de datos
- **Decisión**: El flujo del servicio de login busca al usuario en la base de datos (lectura rápida), cierra o desvincula la consulta, y luego realiza la verificación de la contraseña con bcrypt antes de abrir cualquier transacción de escritura.
- **Razón**: Retener una conexión del pool de PostgreSQL abierta e inactiva durante los 250 ms que toma bcrypt provocaría agotamiento prematuro del connection pool (`DB_POOL_SIZE = 5`).

### 4. Validador centralizado `PasswordBcrypt`
- **Decisión**: Crear en `app/core/security.py` el tipo `PasswordBcrypt = Annotated[str, AfterValidator(_validar_limite_72_bytes)]`.
- **Razón**: Bcrypt trunca silenciosamente las contraseñas a 72 bytes en muchas implementaciones o lanza excepciones no controladas. La consigna y las reglas de negocio exigen rechazar explícitamente con 422 cualquier contraseña que exceda 72 bytes en su codificación UTF-8. Al definirlo en el core, todos los esquemas (login, registro, cambio de contraseña, alta de personal) reusan la misma validación sin duplicar lógica.

### 5. Token transportado exclusivamente en cookie HttpOnly
- **Decisión**: El JWT nunca se incluye en el cuerpo JSON de respuesta de `POST /auth/login`. Se adjunta en la cabecera `Set-Cookie` con directivas `HttpOnly=True`, `SameSite=Lax`, `Max-Age=JWT_MINUTOS * 60` y `Secure=COOKIE_SECURE`.
- **Razón**: Cumplimiento estricto de RN-08 y mitigación de robo de tokens ante eventuales vulnerabilidades XSS en clientes web.

## Risks / Trade-offs

- **[Riesgo] Congestión de hilos ante ataques DoS de login** → *Mitigación*: El semáforo encola las peticiones excedentes sin tumbar el event loop. CH-09 completará esta defensa incorporando el limitador de 5 intentos fallidos antes de invocar bcrypt.
- **[Riesgo] Exposición accidental de contraseñas o hashes en logs** → *Mitigación*: `Settings` tiene `hide_input_in_errors=True` y los esquemas `LoginIn` y `LoginOut` no tienen representaciones de cadenas que incluyan hashes ni devuelven contraseñas.
