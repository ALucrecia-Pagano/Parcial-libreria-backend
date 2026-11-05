# Proposal

## Why

El sistema actual no cuenta con mecanismos de autenticación ni gestión de sesiones para los usuarios. Para dar soporte a los roles y restricciones del parcial (E4, RN-08), es necesario incorporar autenticación mediante correo y contraseña sin bloquear el event loop (bcrypt en worker thread con concurrencia controlada), emitir tokens JWT con vigencia acotada transportados exclusivamente en cookies HttpOnly seguras, y proteger al sistema contra ataques de fuerza bruta y enumeración de usuarios mediante tiempos de respuesta homogéneos (hash ficticio en memoria).

## What Changes

- **Core de Seguridad (`app/core/security.py`)**:
  - Funciones `hashear_password` y `verificar_password` asíncronas que ejecutan `bcrypt` mediante `asyncio.to_thread` coordinadas por un semáforo (`asyncio.Semaphore`) para evitar el agotamiento de recursos del event loop por concurrencia de hashing.
  - Factor de costo configurable tomado de `settings.BCRYPT_COSTO`.
  - Tipo validado reusable `PasswordBcrypt` (`Annotated[str, AfterValidator(...)]`) con `extra="forbid"` que rechaza contraseñas de más de 72 bytes en UTF-8 (`len(v.encode('utf-8')) > 72`) con código HTTP 422.
  - Funciones `crear_token` y `decodificar_token` utilizando `PyJWT` con clave `settings.JWT_SECRET`, algoritmo HS256 y claims estándar (`sub`, `exp`, `roles`).
- **Ciclo de Vida de la Aplicación (`app/main.py`)**:
  - En el arranque (`lifespan`), generación de un hash bcrypt ficticio almacenado en `app.state.hash_ficticio` para igualar los tiempos de verificación ante usuarios inexistentes.
  - Registro del `router_abierto` del módulo de usuarios bajo el prefijo `/auth`.
- **Capa de Datos de Usuarios (`app/modules/usuarios/`)**:
  - Repositorio `UsuarioRepository` (heredado de `BaseRepository[Usuario]`) con búsqueda por email.
  - Repositorio `AsignacionRolRepository` con método `roles_vigentes` (filtrando asignaciones no revocadas y con vencimiento nulo o futuro).
  - Repositorio `EventoSeguridadRepository` como base para auditoría.
  - `UsuariosUnitOfWork` que agrupa los repositorios bajo una misma sesión transaccional.
- **Servicio y Router de Autenticación**:
  - Contrato de entrada `LoginIn` (`email`, `password: PasswordBcrypt`, `extra="forbid"`).
  - Contrato de salida `LoginOut` (`mensaje`, `debe_cambiar_password`, `expira_en_segundos`) garantizando que el token JWT nunca se devuelva en el cuerpo.
  - Endpoint `POST /auth/login` que verifica credenciales (contra hash real o ficticio), emite la cookie `access_token` (`HttpOnly`, `SameSite=Lax`, `Max-Age`, `Secure`) y responde 401 con mensaje genérico («Credenciales inválidas») ante cualquier fallo o usuario inactivo.
- **Casos de Prueba**:
  - Creación de `parcial/test/C-03_cookie.http` (caso de login con cookie y ausencia de token en JSON).
  - Creación de `parcial/test/C-04_anti_enumeracion.http` (verificación de tiempos y mensajes idénticos ante email erróneo o password errónea, y rechazo 422 ante contraseñas > 72 bytes).

## Capabilities

### New Capabilities
- `autenticacion-y-sesion`: Especificación del flujo de autenticación, restricciones de hashing no bloqueante, contratos de login, protección anti-enumeración y manejo de tokens de sesión mediante cookies.

### Modified Capabilities
<!-- Ninguna modificada -->

## Impact

- **APIs**: Se publica la ruta `POST /auth/login`.
- **Dependencias**: Se hace uso efectivo de `bcrypt` y `PyJWT` (declaradas en `requirements.txt`).
- **Estado de Aplicación**: Se añade `hash_ficticio` al estado global (`app.state`).
- **Rendimiento**: Se previene el bloqueo del event loop mediante delegación de bcrypt a hilos con semáforo.
