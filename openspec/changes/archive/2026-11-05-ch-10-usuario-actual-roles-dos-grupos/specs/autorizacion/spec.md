# autorizacion Specification

## Purpose

Define las reglas de autenticación del usuario actual a través de cookies exclusivas, autorización basada en roles consultados en base de datos en cada petición (RN-04), restricción preventiva por cambio obligatorio de contraseña (RN-06), y la separación estructural de endpoints en grupo abierto y grupo protegido.

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
