# stock-libros Specification

## Purpose

Que el stock de un libro solo cambie a través de movimientos registrados, de modo que siempre valga `libro.stock = SUM(movimiento_stock.cantidad)`.

## Requirements

### Requirement: Punto único de escritura del stock
El sistema SHALL modificar `libro.stock` únicamente a través de `aplicar_movimiento`, que en la misma operación agrega la fila de `movimiento_stock` con cantidad, motivo, usuario y (si corresponde) venta.

#### Scenario: Invariante después de altas y reposiciones
- **GIVEN** los datos iniciales, una reposición y dos altas
- **WHEN** se compara el stock de cada libro vigente con la suma de sus movimientos
- **THEN** son iguales en todos

### Requirement: Alta con stock inicial
`POST /libros` SHALL recibir `stock_inicial` (≥ 0), crear el libro y, si `stock_inicial > 0`, registrar el movimiento «Stock inicial» a nombre del ADMIN autenticado; SHALL responder 422 si el cuerpo trae `stock` u otro campo no declarado, y 409 si ya hay un libro vigente con ese ISBN (RN-01).

#### Scenario: ISBN de un libro dado de baja
- **GIVEN** el libro 1 dado de baja
- **WHEN** se da de alta un libro con su ISBN
- **THEN** responde 201 y un segundo alta con el mismo ISBN responde 409 «Ya existe un libro activo con ese ISBN»

#### Scenario: Stock inicial 0
- **WHEN** se da de alta un libro con `stock_inicial` 0
- **THEN** responde 201 con stock 0 y el libro no tiene movimientos

### Requirement: Reposición
`POST /libros/{id}/reponer` SHALL sumar `cantidad` (> 0) con un movimiento «Reposición» y responder 200 con ese movimiento; 404 si el libro no existe, 409 si está dado de baja (RN-13), 422 si la cantidad no es positiva y 401 sin sesión.

#### Scenario: Reponer un libro dado de baja
- **GIVEN** Rayuela dada de baja
- **WHEN** se hace `POST /libros/1/reponer` con `{"cantidad": 5}`
- **THEN** responde 409 y no se registra ningún movimiento

### Requirement: Historial de movimientos
`GET /libros/{id}/movimientos` SHALL devolver los movimientos del libro en orden cronológico (también de libros dados de baja) y 404 si el libro no existe; los movimientos nunca se modifican ni se borran (RN-12).

#### Scenario: Movimientos de Rayuela
- **WHEN** se repone Rayuela con 5 y se piden sus movimientos
- **THEN** la lista es Stock inicial +11, Venta −1, Reposición +5
