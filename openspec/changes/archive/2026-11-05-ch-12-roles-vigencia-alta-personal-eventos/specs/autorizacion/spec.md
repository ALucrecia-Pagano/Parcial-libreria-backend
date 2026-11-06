## ADDED Requirements

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
