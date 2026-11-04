# salud Specification

## Purpose

Expone el estado de la aplicación para quien la opera o la orquesta: si el proceso está vivo y si está listo para atender porque la base de datos contesta.

## Requirements

### Requirement: Vida del proceso
`GET /health/live` SHALL responder 200 mientras el proceso atienda pedidos, sin consultar la base, y sin requerir sesión.

#### Scenario: Proceso vivo con base disponible
- **WHEN** se pide `GET /health/live` con la base encendida
- **THEN** responde 200 con un cuerpo JSON que indica que está vivo

#### Scenario: Proceso vivo con base apagada
- **WHEN** se pide `GET /health/live` con la base apagada
- **THEN** responde 200 igual, porque no depende de la base

### Requirement: Disponibilidad de la base
`GET /health/ready` SHALL ejecutar una consulta trivial contra la base y responder 200 si contesta o 503 si no, sin requerir sesión.

#### Scenario: Base disponible
- **WHEN** se pide `GET /health/ready` con la base encendida
- **THEN** responde 200 con un cuerpo JSON que indica que está lista

#### Scenario: Base apagada
- **WHEN** se pide `GET /health/ready` con la base apagada o inaccesible
- **THEN** responde 503 con un mensaje propio, sin texto del motor de base ni traza

#### Scenario: La base vuelve
- **WHEN** la base se enciende de nuevo tras un 503 y se vuelve a pedir `GET /health/ready`
- **THEN** responde 200 sin reiniciar la aplicación
