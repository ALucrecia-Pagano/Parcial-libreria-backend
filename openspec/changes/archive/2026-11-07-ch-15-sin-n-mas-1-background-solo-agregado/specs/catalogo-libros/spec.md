# Spec Delta — catalogo-libros

## ADDED Requirements

### Requirement: Listado con relaciones precargadas
`GET /libros` SHALL incluir, en cada ítem, la editorial, el género y los autores del libro, obtenidos con carga anticipada declarada en el repositorio. La lectura SHALL NOT depender de la carga perezosa.

#### Scenario: Un ítem del catálogo
- **WHEN** se pide `GET /libros` con los datos iniciales
- **THEN** responde 200 y cada libro trae su editorial, su género y su lista de autores
