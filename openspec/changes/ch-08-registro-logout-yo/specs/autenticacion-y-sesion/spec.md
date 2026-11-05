# Spec Delta

## ADDED Requirements

### Requirement: Auto-registro atómico de clientes
El sistema SHALL permitir el auto-registro de nuevos clientes mediante POST /auth/registro. La operación SHALL ejecutar en un único bloque de Unit of Work y transacción la creación del registro en usuario, la asignación del rol CLIENTE y la creación de la ficha en cliente con usuario_id vinculado. Ante colisión de unicidad en uq_usuario_email o uq_cliente_email, el sistema SHALL rechazar con código HTTP 409 y mensaje específico sin consulta previa. La respuesta 201 SHALL omitir password_hash.

#### Scenario: Registro exitoso de nuevo cliente
- **WHEN** un cliente envía una petición POST /auth/registro con datos válidos y un correo no registrado
- **THEN** el sistema crea atómicamente el usuario, le asigna el rol CLIENTE y crea su ficha de cliente, respondiendo con código HTTP 201 y cuerpo sin password_hash

#### Scenario: Intento de registro con correo de usuario existente
- **WHEN** se envía una petición POST /auth/registro con un correo ya existente en la tabla usuario
- **THEN** el sistema captura la violación de uq_usuario_email y responde con código HTTP 409 y mensaje descriptivo de usuario ya registrado

#### Scenario: Intento de registro con correo de ficha de cliente existente
- **WHEN** se envía una petición POST /auth/registro con un correo existente en la tabla cliente pero no en usuario
- **THEN** el sistema captura la violación de uq_cliente_email, responde con código HTTP 409 indicando que el correo pertenece a un cliente, revierte la transacción completa y no crea usuario ni asignación de rol

#### Scenario: Contrato estricto prohíbe atributos de rol o campos adicionales
- **WHEN** se envía una petición POST /auth/registro con campos no definidos en el contrato o intentando autoasignarse un rol
- **THEN** el sistema rechaza la petición con código HTTP 422 antes de procesar el registro

#### Scenario: Rechazo por contraseña mayor a 72 bytes en UTF-8
- **WHEN** se envía una petición POST /auth/registro con una contraseña cuya representación UTF-8 supera los 72 bytes
- **THEN** el sistema rechaza la petición con código HTTP 422 antes de calcular cualquier hash

### Requirement: Cierre de sesión e invalidación de cookie
El sistema SHALL permitir cerrar la sesión mediante POST /auth/logout. La operación SHALL eliminar la cookie HttpOnly access_token configurando una cabecera Set-Cookie con Max-Age=0 y expiración en época pasada. El endpoint SHALL ser accesible públicamente y responder siempre con código de estado HTTP 200, incluso ante peticiones sin cookie previa o con token inválido.

#### Scenario: Cierre de sesión con cookie activa
- **WHEN** un usuario autenticado realiza una petición POST /auth/logout
- **THEN** el sistema responde con código HTTP 200 y emite la cabecera Set-Cookie invalidando access_token con Max-Age=0

#### Scenario: Cierre de sesión idempotente sin sesión previa
- **WHEN** un cliente realiza POST /auth/logout sin enviar cookie access_token o con una sesión ya vencida
- **THEN** el sistema responde con código HTTP 200 y emite la cabecera de eliminación de cookie sin generar error

### Requirement: Consulta de identidad del usuario autenticado
El sistema SHALL proveer el endpoint GET /auth/yo para consultar los datos del usuario autenticado. La respuesta SHALL retornar la información básica del usuario, la lista de roles vigentes leída directamente de la base de datos y la lista de roles declarada en el token JWT. Si no existe una sesión válida o la cookie access_token está ausente, el sistema SHALL responder con código HTTP 401.

#### Scenario: Consulta de identidad con sesión válida
- **WHEN** un usuario con sesión activa realiza una petición GET /auth/yo
- **THEN** el sistema responde con código HTTP 200 devolviendo los datos del usuario, los roles vigentes en la base y los roles presentes en el token

#### Scenario: Consulta de identidad rechazada sin sesión activa
- **WHEN** un cliente invoca GET /auth/yo sin adjuntar la cookie de sesión o con un token revocado o inválido
- **THEN** el sistema responde con código HTTP 401 y mensaje de error de autenticación
