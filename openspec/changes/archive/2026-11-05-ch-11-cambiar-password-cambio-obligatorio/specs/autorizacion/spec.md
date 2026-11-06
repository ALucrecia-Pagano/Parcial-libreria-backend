# autorizacion Specification

## Purpose

Define las reglas de autenticación del usuario actual a través de cookies exclusivas, autorización basada en roles consultados en base de datos en cada petición (RN-04), restricción preventiva por cambio obligatorio de contraseña (RN-06), cambio voluntario u obligatorio de contraseña con auditoría (RN-16, DD-30), y la separación estructural de endpoints en grupo abierto y grupo protegido.

## Requirements

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
