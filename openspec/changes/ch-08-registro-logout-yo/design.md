# Design

## Context

El sistema de autenticación ya cuenta con emisión de cookies `access_token` (`CH-07`) y limitador de intentos fallidos (`CH-09`). Sin embargo, los nuevos clientes aún no pueden registrarse por sí mismos en la plataforma. La regla de negocio RN-02 y los requerimientos del parcial exigen que el auto-registro cree de forma atómica el usuario, su rol inicial CLIENTE y la ficha del cliente en una única transacción de base de datos. Además, se debe proveer cierre de sesión (`POST /auth/logout`) que funcione con o sin sesión previa (DD-18), y la consulta de identidad (`GET /auth/yo`) que contrasta roles en base vs roles en token.

Ver detalles de motivación en `proposal.md` y especificaciones normativas en `specs/autenticacion-y-sesion/spec.md`.

## Goals / Non-Goals

**Goals:**
- Implementar `POST /auth/registro` con contrato estricto (`extra="forbid"`), validación de contraseña de hasta 72 bytes UTF-8 (`PasswordBcrypt`) y creación atómica de usuario + asignación de rol CLIENTE + ficha de cliente en un único bloque `async with uow:`.
- Garantizar que el hash bcrypt se compute **antes** de abrir la transacción del UoW, protegiendo el pool de conexiones (`DB_POOL_SIZE = 5`).
- Asegurar unicidad mediante captura de `IntegrityError` en `uq_usuario_email` y `uq_cliente_email` (RN-01, RN-15), devolviendo 409 con mensaje específico y rollback total.
- Implementar `POST /auth/logout` que responda 200 siempre y elimine la cookie `access_token` con `Max-Age=0`.
- Diseñar y preparar `GET /auth/yo` que expone los datos de usuario y la comparación entre roles vigentes en la base y roles del token.
- Verificar el comportamiento mediante la suite de pruebas `parcial/test/C-02_registro.http`.

**Non-Goals:**
- Implementar la dependencia completa de extracción y validación de cookie `get_usuario_actual` (alcance de `CH-10`).
- Implementar endpoints administrativos de gestión de clientes (alcance de `CH-13`).
- Implementar cambio de contraseña (alcance de `CH-11`).

## Decisions

### Decision 1: Cómputo de hash bcrypt previo a la transacción de base de datos
- **Decisión**: La contraseña recibida en `RegistroClienteRequest` se hashea mediante `hashear_password` (ejecutado en `asyncio.to_thread` bajo `BCRYPT_SEMAFORO`) *antes* de iniciar `async with uow:`.
- **Razón**: Con un pool pequeño de conexiones a PostgreSQL (`DB_POOL_SIZE = 5`), retener una conexión abierta durante los ~250ms que tarda bcrypt provocaría contención y agotamiento de conexiones en entornos concurrentes.
- **Alternativas consideradas**: Hashear dentro del bloque `async with uow:` (descartada por retención innecesaria de recursos de base de datos).

### Decision 2: Creación atómica en un único bloque `async with uow:`
- **Decisión**: La creación de `Usuario`, `AsignacionRol` (con `Rol.CLIENTE`) y `Cliente` se ejecuta dentro de un único bloque transaccional en `UsuariosService.registrar_cliente`.
- **Razón**: Cumple estrictamente con la regla RN-02. Si cualquier operación falla (por ejemplo, si el email ya existe en la tabla `cliente`), la transacción revierte por completo evitando usuarios creados sin ficha o fichas sin rol.
- **Alternativas consideradas**: Múltiples bloques o servicios separados (descartadas porque violan la garantía atómica de RN-02).

### Decision 3: Repositorio genérico para la entidad Cliente en `UsuariosUnitOfWork`
- **Decisión**: Inyectar `self.clientes = BaseRepository[Cliente](session, Cliente)` directamente en `UsuariosUnitOfWork`.
- **Razón**: Permite persistir la ficha del cliente durante el auto-registro sin necesidad de acoplar el módulo de usuarios con el repositorio específico de `clientes` de CH-13 ni generar dependencias circulares.
- **Alternativas consideradas**: Importar un repositorio especializado no disponible aún (descartada porque CH-13 no está implementado).

### Decision 4: Captura de `IntegrityError` y traducción centralizada en `app/core/errores.py`
- **Decisión**: No realizar consultas previas (`SELECT`) para verificar disponibilidad de correo (RN-01). En su lugar, se deja que PostgreSQL aplique los índices únicos `uq_usuario_email` y `uq_cliente_email`, capturando `IntegrityError` y traduciéndolo a HTTP 409 en `app/core/errores.py`:
  - `uq_usuario_email`: `"El correo ya se encuentra registrado por un usuario"`
  - `uq_cliente_email`: `"El correo ya pertenece a un cliente existente"`
- **Razón**: Evita condiciones de carrera tipo Time-of-Check to Time-of-Use (TOCTOU) y satisface la regla dura de atrapar excepciones de unicidad sin consultas previas.
- **Alternativas consideradas**: Consultas previas `get_by_email` (descartadas por violar RN-01 y las reglas del proyecto).

### Decision 5: Cierre de sesión idempotente (`POST /auth/logout`)
- **Decisión**: `POST /auth/logout` emite la cabecera `Set-Cookie` para `access_token` con `Max-Age=0`, `Path=/`, `HttpOnly=True` y `SameSite=lax`. Responde siempre HTTP 200 sin exigir cookie previa.
- **Razón**: Cumple con DD-18 (cerrar sesión sin estar autenticado no debe fallar) y asegura la remoción limpia de la credencial en el navegador del usuario.

## Risks / Trade-offs

- **[Riesgo] Intento de auto-registro con correo de cliente existente pero sin usuario vinculado (ej. "Tomás Ríos")**:
  → **Mitigación**: La restricción de unicidad `uq_cliente_email` detona el rollback atómico del UoW, devolviendo 409 y asegurando que la ficha preexistente conserve su estado (`usuario_id = null`) sin ser apropiada indebidamente.
- **[Riesgo] Exposición accidental de `password_hash` en la respuesta 201**:
  → **Mitigación**: `RegistroClienteResponse` define explícitamente los campos retornados (`id`, `nombre`, `email`, `cliente_id`, etc.) omitiendo `password_hash` y configurando `extra="forbid"`.
- **[Riesgo] Dependencia de CH-10 para `/auth/yo`**:
  → **Mitigación**: El endpoint y servicio se estructuran con su contrato completo; la integración de la dependencia `get_usuario_actual` se sincronizará cuando CH-10 ingrese al repositorio antes de archivar.
