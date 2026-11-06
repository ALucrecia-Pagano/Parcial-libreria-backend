# autorizacion Specification

## Purpose

Define las reglas de autenticación del usuario actual a través de cookies exclusivas, autorización basada en roles consultados en base de datos en cada petición (RN-04), restricción preventiva por cambio obligatorio de contraseña (RN-06), cambio voluntario u obligatorio de contraseña con auditoría (RN-16, DD-30), y la separación estructural de endpoints en grupo abierto y grupo protegido.

## Requirements

### Requirement: Extracción de usuario actual exclusivamente desde cookie HttpOnly
El sistema SHALL leer el token de sesión únicamente desde la cookie `access_token` presente en la cabecera `Cookie`. El sistema NUNCA SHALL aceptar tokens enviados en la cabecera `Authorization: Bearer`. Si la cookie está ausente, el token es inválido o expirado, o el usuario referenciado no existe o posee `activo=false`, el sistema SHALL responder con código HTTP 401 Unauthorized.

#### Scenario: Petición sin cookie de sesión
- **WHEN** un cliente realiza una petición a una ruta que requiere usuario actual sin enviar la cookie `access_token`
- **THEN** el sistema responde con código HTTP 401 Unauthorized

#### Scenario: Petición enviando token en cabecera Authorization
- **WHEN** un cliente realiza una petición enviando un token JWT válido en `Authorization: Bearer <token>` pero sin cookie `access_token`
- **THEN** el sistema responde con código HTTP 401 Unauthorized

#### Scenario: Usuario desactivado en base de datos
- **WHEN** un cliente envía una cookie con firma válida pero el usuario correspondiente tiene `activo=false` en la tabla `usuario`
- **THEN** el sistema responde con código HTTP 401 Unauthorized

### Requirement: Autorización basada en roles vigentes en base de datos en cada petición (RN-04)
El sistema SHALL verificar los roles del usuario consultando las asignaciones vigentes en la tabla `asignacion_rol` (`revocada_en IS NULL` y fecha `vence_en` nula o posterior al instante actual) en cada petición protegida. Si el usuario no cuenta con al menos uno de los roles requeridos, el sistema SHALL responder con código HTTP 403 Forbidden.

#### Scenario: Usuario sin el rol requerido
- **WHEN** un usuario con rol VENDEDOR intenta invocar un endpoint reservado para ADMIN
- **THEN** el sistema responde con código HTTP 403 Forbidden

#### Scenario: Revocación de rol efectiva de inmediato
- **WHEN** a un usuario se le revoca un rol en la base de datos mientras mantiene una sesión iniciada
- **THEN** en la siguiente petición con la misma cookie, el sistema consulta la base y responde HTTP 403 Forbidden

### Requirement: Bloqueo de acceso al grupo protegido por cambio obligatorio de contraseña (RN-06)
El sistema SHALL bloquear con código HTTP 403 Forbidden el acceso a cualquier endpoint del grupo protegido a todo usuario autenticado cuyo atributo `debe_cambiar_password` sea `true`. Los endpoints del grupo abierto (`/health/*`, `/auth/*`, lecturas públicas de catálogo) SHALL permanecer accesibles para permitir la operación de cambio de contraseña.

#### Scenario: Usuario con cambio obligatorio intenta acceder al grupo protegido
- **WHEN** un usuario con `debe_cambiar_password=true` realiza una petición a una ruta del grupo protegido
- **THEN** el sistema responde con código HTTP 403 Forbidden

#### Scenario: Usuario con cambio obligatorio accede a rutas públicas o de autenticación
- **WHEN** un usuario con `debe_cambiar_password=true` realiza una petición a `/libros` o `/auth/yo`
- **THEN** el sistema permite la ejecución de la petición respondiendo con código HTTP 200 OK

### Requirement: Cambio de contraseña y desbloqueo obligatorio (RN-06, RN-16, DD-30)
El sistema SHALL permitir a cualquier usuario autenticado actualizar su contraseña mediante `POST /auth/cambiar-password`, enviando `password_actual` y `password_nueva`. Ambas contraseñas SHALL cumplir con la restricción de hasta 72 bytes en UTF-8 (`PasswordBcrypt`). Si la contraseña actual no coincide, el sistema SHALL responder con código HTTP 401 Unauthorized sin alterar el estado. Ante credenciales válidas, el sistema SHALL actualizar el hash de la contraseña, establecer `debe_cambiar_password = false` y registrar el evento de auditoría en la tabla `evento_seguridad` con actor igual al email del usuario y acción `"Cambio de contraseña"`, todo dentro de la misma transacción. La sesión activa (cookie previa) SHALL continuar siendo válida para acceder inmediatamente al grupo protegido sin requerir reautenticación.

#### Scenario: Cambio de contraseña exitoso por usuario con cambio pendiente
- **WHEN** un usuario con `debe_cambiar_password=true` envía `POST /auth/cambiar-password` con su contraseña actual correcta y una nueva de hasta 72 bytes
- **THEN** el sistema responde con código HTTP 200 OK, desactiva la marca en la base de datos, registra el evento en `evento_seguridad` y la misma cookie permite invocar endpoints protegidos en la petición inmediatamente posterior

#### Scenario: Contraseña actual incorrecta en cambio de contraseña (DD-30)
- **WHEN** un usuario autenticado envía `POST /auth/cambiar-password` con una contraseña actual incorrecta
- **THEN** el sistema responde con código HTTP 401 Unauthorized y la contraseña permanece sin cambios

#### Scenario: Contraseña nueva superior a 72 bytes UTF-8
- **WHEN** un usuario intenta cambiar su contraseña enviando una clave nueva que excede 72 bytes en codificación UTF-8
- **THEN** el sistema responde con código HTTP 422 Unprocessable Entity
