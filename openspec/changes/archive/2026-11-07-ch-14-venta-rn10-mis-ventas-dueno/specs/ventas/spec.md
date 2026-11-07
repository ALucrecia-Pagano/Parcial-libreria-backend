# Spec Delta — ventas

## Purpose

Registrar una venta con sus renglones, el precio copiado del libro y el stock descontado en la misma transacción, y dejar que cada cliente vea solo sus ventas.

## ADDED Requirements

### Requirement: Alta atómica con precio del servidor
`POST /ventas` SHALL aceptar solo `cliente_id` y `renglones` (al menos uno, sin libros repetidos). SHALL responder 201 con el precio de cada renglón copiado del libro y el total calculado por el servidor. SHALL responder 422 si el cuerpo trae un campo no declarado, no trae renglones o repite un libro. SHALL responder 409, sin dejar venta, renglones, descuentos ni movimientos, si el cliente no existe, si un libro no existe, si un libro está dado de baja o si un libro no tiene stock suficiente.

#### Scenario: Dos renglones válidos
- **WHEN** un VENDEDOR vende 2 Rayuela y 1 Respiración artificial a Lucía
- **THEN** responde 201 con precios `25000.00` y `27000.00`, total `77000.00`, el stock de cada libro bajó y hay un movimiento «Venta» por renglón

#### Scenario: No alcanza el stock
- **WHEN** la venta pide 1 Rayuela y 2 Bestiario
- **THEN** responde 409, no hay venta nueva y el stock de Rayuela sigue en 10

#### Scenario: Referencia inválida
- **WHEN** el cliente no existe, el libro no existe o el libro está dado de baja
- **THEN** responde 409 y la cantidad de ventas no cambia

### Requirement: Lecturas de personal y de lo propio
`GET /ventas` y `GET /clientes/{id}/ventas` SHALL ser de VENDEDOR o ADMIN y devolver el envoltorio `{items, total, page, size, pages}`. `GET /clientes/{id}/ventas` SHALL responder 404 si el cliente no existe. `GET /ventas/{id}` SHALL responder 200 al personal o al cliente dueño, 403 a otro cliente y 404 si la venta no existe, sin exigir un rol fijo. `GET /mis-ventas` SHALL devolver solo las ventas cuya ficha pertenece al usuario autenticado.

#### Scenario: La cliente ve la suya y no la ajena
- **WHEN** Ana consulta su venta y la venta de Lucía
- **THEN** la propia responde 200 y la ajena responde 403

#### Scenario: Sin sesión
- **WHEN** se pide `GET /ventas` o `POST /ventas` sin cookie
- **THEN** responde 401
