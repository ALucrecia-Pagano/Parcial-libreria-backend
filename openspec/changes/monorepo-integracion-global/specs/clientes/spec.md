## ADDED Requirements

### Requirement: Listado paginado de clientes
El sistema SHALL exponer `GET /clientes` para usuarios con rol VENDEDOR o ADMIN, devolviendo una página de clientes ordenada por `id` ascendente, con `id`, `nombre`, `email`, `usuario_id` y `perfil` (o `null`), y SHALL rechazar la petición con 401 sin sesión y 403 para el rol CLIENTE.

#### Scenario: Listado con sesión de staff
- **WHEN** un usuario VENDEDOR o ADMIN solicita `GET /clientes?page=1&size=20`
- **THEN** el sistema responde 200 con `{items,total,page,size,pages}` y cada item incluye `perfil` (o `null`)

#### Scenario: Listado sin sesión
- **WHEN** un cliente sin cookie `access_token` solicita `GET /clientes`
- **THEN** el sistema responde 401

#### Scenario: Listado con rol CLIENTE
- **WHEN** un usuario con rol CLIENTE solicita `GET /clientes`
- **THEN** el sistema responde 403

#### Scenario: Página fuera de rango
- **WHEN** se solicita `GET /clientes?page=99&size=20` y hay menos páginas
- **THEN** el sistema responde 422 con el mensaje de página inexistente
