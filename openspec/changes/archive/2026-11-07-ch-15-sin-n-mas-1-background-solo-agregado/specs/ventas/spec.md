# Spec Delta — ventas

## MODIFIED Requirements

### Requirement: Lecturas de personal y de lo propio
`GET /ventas` y `GET /clientes/{id}/ventas` SHALL ser de VENDEDOR o ADMIN y devolver el envoltorio `{items, total, page, size, pages}`. `GET /clientes/{id}/ventas` SHALL responder 404 si el cliente no existe. `GET /ventas/{id}` SHALL responder 200 al personal o al cliente dueño, 403 a otro cliente y 404 si no existe, sin exigir un rol fijo, e incluir cliente, renglones y el libro de cada renglón aunque ese libro esté dado de baja. Esa lectura SHALL usar una cantidad fija de consultas, igual para 2 y para 4 renglones. `GET /mis-ventas` SHALL devolver solo las ventas cuya ficha pertenece al usuario autenticado.

#### Scenario: La cliente ve la suya y no la ajena
- **WHEN** Ana consulta su venta y la venta de Lucía
- **THEN** la propia responde 200 y la ajena responde 403

#### Scenario: Sin sesión
- **WHEN** se pide `GET /ventas` o `POST /ventas` sin cookie
- **THEN** responde 401

#### Scenario: La misma cantidad de consultas
- **WHEN** se pide el detalle de una venta de 2 renglones y el de una de 4, con `SQL_ECHO=true`
- **THEN** la consola muestra la misma cantidad de SELECT en los dos pedidos
