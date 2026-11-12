## ADDED Requirements

### Requirement: Nombre del cliente en los listados de ventas
Los listados `GET /ventas`, `GET /clientes/{cliente_id}/ventas` y `GET /mis-ventas` SHALL incluir `cliente_nombre` en cada venta, además de `id`, `cliente_id`, `fecha` y `total`, sin requerir una petición adicional por venta.

#### Scenario: Listado de ventas con nombre
- **WHEN** un usuario VENDEDOR o ADMIN solicita `GET /ventas`
- **THEN** cada item de la página incluye `cliente_nombre` con el nombre del cliente de la venta

#### Scenario: Mis ventas con nombre
- **WHEN** un usuario autenticado solicita `GET /mis-ventas`
- **THEN** cada item incluye `cliente_nombre` correspondiente a su ficha de cliente

#### Scenario: Detalle sin cambios
- **WHEN** se solicita `GET /ventas/{venta_id}`
- **THEN** el detalle conserva `cliente: {id,nombre,email}` y los renglones, y no depende de `cliente_nombre`
