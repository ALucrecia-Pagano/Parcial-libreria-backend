# autorizacion Specification

## Purpose

Define las reglas de autenticación del usuario actual a través de cookies exclusivas, autorización basada en roles consultados en base de datos en cada petición (RN-04), restricción preventiva por cambio obligatorio de contraseña (RN-06), cambio voluntario u obligatorio de contraseña con auditoría (RN-16, DD-30), administración de personal y roles con vigencia e historial (RN-03, RN-04, RN-16), autoprotección de administradores (RN-05), y la separación estructural de endpoints en grupo abierto y grupo protegido.

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

### Requirement: Alta de personal por administrador (RN-06, RN-16)
El sistema SHALL permitir a los usuarios con rol `ADMIN` dar de alta personal mediante `POST /usuarios`, recibiendo `email`, `nombre`, `password` (de tipo `PasswordBcrypt`, máx 72 bytes UTF-8) y `rol` (`ADMIN`, `VENDEDOR` o `CLIENTE`). La contraseña se hashea antes de abrir la transacción. En un único bloque transaccional se crea el usuario con `debe_cambiar_password = true`, se inserta la asignación del rol con `otorgada_por = admin.id` y se registra el evento en `evento_seguridad` con actor igual al email del administrador y acción `"Alta de personal"`. Si el email ya existe, se rechaza con 409 Conflict.

#### Scenario: Alta de personal exitosa
- **WHEN** un administrador envía `POST /usuarios` con datos válidos y contraseña provisoria de hasta 72 bytes
- **THEN** el sistema responde con código HTTP 201 Created, persiste el usuario con `debe_cambiar_password = true`, asigna el rol y registra el evento de seguridad en una sola transacción

#### Scenario: Alta de personal con contraseña provisoria de más de 72 bytes UTF-8
- **WHEN** un administrador envía `POST /usuarios` con una contraseña provisoria que supera los 72 bytes UTF-8
- **THEN** el sistema responde con código HTTP 422 Unprocessable Entity

### Requirement: Gestión de roles con vigencia e historial (RN-03, RN-04, RN-16)
El sistema SHALL permitir a los usuarios con rol `ADMIN` consultar el historial completo de roles de un usuario (`GET /usuarios/{id}/roles`), incluyendo asignaciones revocadas y vencidas. Asimismo, permitirá asignar roles (`POST /usuarios/{id}/roles`) con un campo opcional `vence_en`. El valor de `vence_en` SHALL contener información explícita de zona horaria y encontrarse en el futuro; de lo contrario el sistema SHALL responder con 422 Unprocessable Entity. Si el usuario ya cuenta con una asignación activa del mismo rol, el sistema SHALL responder con 409 Conflict. Si existiera una asignación previa vencida, el sistema SHALL revocar la anterior y registrar la nueva junto al evento de seguridad en la misma transacción.

#### Scenario: Consulta de historial con asignaciones revocadas
- **WHEN** un administrador consulta `GET /usuarios/{id}/roles` de un usuario que tuvo roles revocados
- **THEN** el sistema responde con código HTTP 200 OK y la lista incluye las asignaciones con su fecha de revocación

#### Scenario: Asignación de rol con fecha de vencimiento en el pasado o sin zona horaria
- **WHEN** un administrador envía `POST /usuarios/{id}/roles` con `vence_en` en el pasado o sin zona horaria
- **THEN** el sistema responde con código HTTP 422 Unprocessable Entity

#### Scenario: Asignación duplicada de rol activo
- **WHEN** un administrador envía `POST /usuarios/{id}/roles` para un rol que el usuario ya tiene activo
- **THEN** el sistema responde con código HTTP 409 Conflict con mensaje `"El usuario ya tiene ese rol activo asignado"`

### Requirement: Revocación de rol y autoprotección (RN-05, RN-16)
El sistema SHALL permitir a los usuarios con rol `ADMIN` revocar roles activos mediante `DELETE /usuarios/{id}/roles/{rol}`, marcando `revocada_en` con la fecha y hora actual sin eliminar físicamente el registro. El sistema SHALL impedir que un administrador se revoque su propio rol `ADMIN`, respondiendo con código HTTP 409 Conflict. Asimismo, el sistema SHALL impedir la revocación del rol `ADMIN` si dicha acción dejara al sistema con cero administradores vigentes, respondiendo con código HTTP 409 Conflict. La revocación exitosa SHALL registrarse en `evento_seguridad` en la misma transacción.

#### Scenario: Administrador intenta revocarse a sí mismo el rol ADMIN
- **WHEN** un administrador realiza `DELETE /usuarios/{su_id}/roles/ADMIN`
- **THEN** el sistema responde con código HTTP 409 Conflict e impide la revocación

#### Scenario: Revocación que dejaría cero administradores vigentes
- **WHEN** se intenta revocar el rol `ADMIN` al único administrador vigente restante en el sistema
- **THEN** el sistema responde con código HTTP 409 Conflict e impide la revocación

### Requirement: Consulta paginada de eventos de seguridad (RN-16)
El sistema SHALL permitir a los usuarios con rol `ADMIN` consultar el historial de auditoría mediante `GET /eventos`, aceptando parámetros de paginación `page` (>= 1) y `size` (1..100). Los eventos SHALL retornarse ordenados de más recientes a más antiguos en un envoltorio `{ items, total, page, size, pages }`. Peticiones con `size` superior a 100 SHALL responder con código HTTP 422 Unprocessable Entity.

#### Scenario: Consulta paginada de eventos exitosa
- **WHEN** un administrador consulta `GET /eventos?page=1&size=10`
- **THEN** el sistema responde con código HTTP 200 OK con la lista paginada ordenada cronológicamente de forma descendente
