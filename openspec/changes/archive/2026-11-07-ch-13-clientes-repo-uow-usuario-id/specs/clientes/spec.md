# Spec Delta — clientes

## Purpose

Ficha de cliente que el personal crea y edita, con perfil uno a uno y vínculo opcional a un usuario de acceso web, sin que ese vínculo se pueda asignar desde el alta ni el PATCH.

## ADDED Requirements

### Requirement: Alta de cliente sin acceso web
`POST /clientes` SHALL crear un cliente con `usuario_id` nulo y responder 201. El cuerpo SHALL aceptar solo `nombre` y `email`. Un campo no declarado, incluido `usuario_id`, SHALL responder 422. Un correo ya usado por otro cliente SHALL responder 409 con mensaje propio, sin texto de la base y sin dejar una fila nueva.

#### Scenario: Alta válida
- **WHEN** un VENDEDOR envía `POST /clientes` con nombre y correo nuevos
- **THEN** responde 201 y el cliente creado tiene `usuario_id` nulo

#### Scenario: Correo repetido
- **WHEN** se envía el correo de un cliente ya existente
- **THEN** responde 409 con el mensaje de `uq_cliente_email` y no queda un cliente nuevo

#### Scenario: Campo no declarado
- **WHEN** el cuerpo incluye `usuario_id` o cualquier otro campo no declarado
- **THEN** responde 422

### Requirement: Lectura de la ficha con perfil
`GET /clientes/{id}` SHALL devolver el cliente, su perfil si existe y su `usuario_id`. SHALL responder 404 si el id no existe.

#### Scenario: Cliente con perfil y sin usuario
- **GIVEN** los datos iniciales
- **WHEN** se pide `GET /clientes/1`
- **THEN** responde 200 con el perfil de Lucía Fernández y `usuario_id` nulo

#### Scenario: Cliente con usuario
- **WHEN** se pide `GET /clientes/3`
- **THEN** responde 200 y `usuario_id` tiene valor

#### Scenario: Cliente inexistente
- **WHEN** se pide `GET /clientes/9999`
- **THEN** responde 404

### Requirement: Modificación parcial
`PATCH /clientes/{id}` SHALL aplicar solo los campos enviados, conservar lo omitido y responder 200. SHALL responder 404 si el cliente no existe, 409 si el correo choca con otro cliente y 422 si el cuerpo trae un campo no declarado, un `null` explícito o ningún campo.

#### Scenario: Un solo campo
- **WHEN** se hace `PATCH /clientes/2` con solo un nombre nuevo
- **THEN** responde 200 y el correo de Tomás Ríos no cambia

#### Scenario: Correo de otro cliente
- **WHEN** el PATCH usa el correo de otro cliente
- **THEN** responde 409 y la ficha queda como estaba

### Requirement: Perfil uno a uno
`POST /clientes/{id}/perfil` SHALL crear el perfil y responder 201. SHALL responder 404 si el cliente no existe y 409 si ese cliente ya tiene perfil. El cuerpo SHALL aceptar solo `telefono` y `direccion`.

#### Scenario: Primer perfil
- **WHEN** se hace `POST /clientes/2/perfil` con teléfono y dirección
- **THEN** responde 201

#### Scenario: Perfil repetido
- **WHEN** se vuelve a crear el perfil del mismo cliente
- **THEN** responde 409 y sigue habiendo un solo perfil

#### Scenario: Cliente inexistente
- **WHEN** se hace `POST /clientes/9999/perfil`
- **THEN** responde 404

### Requirement: Solo personal
Las rutas de clientes SHALL responder 401 sin sesión y 403 si la sesión es de un CLIENTE.

#### Scenario: Sin sesión
- **WHEN** se hace `POST /clientes` sin cookie
- **THEN** responde 401

#### Scenario: Sesión de cliente
- **WHEN** Ana Paz hace `POST /clientes`
- **THEN** responde 403
