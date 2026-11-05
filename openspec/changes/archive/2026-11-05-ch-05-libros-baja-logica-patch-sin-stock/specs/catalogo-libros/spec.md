# Spec Delta — catalogo-libros

## Purpose

Catálogo público de libros con baja lógica: solo los vigentes se listan, se buscan y se muestran; el PATCH no toca el stock; las ventas viejas siguen viendo los libros dados de baja.

## ADDED Requirements

### Requirement: Catálogo paginado con búsqueda segura
`GET /libros` SHALL devolver `{items, total, page, size, pages}` con los libros vigentes, filtrables por `titulo` (parte del título, sin distinguir mayúsculas, con parámetros ligados) y `genero_id`, donde `total` cuenta con los mismos filtros que la página.

#### Scenario: Intento de inyección
- **WHEN** se pide `GET /libros?titulo=' OR '1'='1`
- **THEN** responde 200 con `items` vacío y `total` 0

#### Scenario: Paginación con filtro
- **WHEN** se pide `GET /libros?titulo=ficc&size=1`
- **THEN** responde 200 con `total` 1 y `pages` 1, y con `page=2` responde 422

### Requirement: PATCH sin stock
`PATCH /libros/{id}` SHALL aceptar solo `titulo` y `precio`, aplicar solo lo enviado y responder 422 ante cualquier otro campo (RN-11).

#### Scenario: Intento de editar el stock
- **WHEN** se hace `PATCH /libros/1` con `{"stock": 99}`
- **THEN** responde 422 y el stock del libro no cambia

### Requirement: Baja lógica
`DELETE /libros/{id}` SHALL marcar `borrado_en` sin borrar la fila y responder 204; un libro dado de baja SHALL NOT aparecer en el catálogo, el detalle ni las listas por editorial, género o autor, y SHALL seguir apareciendo en las ventas que lo incluyen (RN-13).

#### Scenario: Libro con ventas dado de baja
- **GIVEN** la venta 1 incluye Ficciones (libro 3)
- **WHEN** se hace `DELETE /libros/3`
- **THEN** responde 204, `GET /libros/3` responde 404, `GET /libros` ya no lo lista y `GET /ventas/1` sigue mostrando «Ficciones»

### Requirement: Libros de una editorial, un género o un autor
`GET /editoriales/{id}/libros`, `/generos/{id}/libros` y `/autores/{id}/libros` SHALL devolver los libros vigentes de esa entidad y responder 404 si la entidad no existe.

#### Scenario: Género inexistente
- **WHEN** se pide `GET /generos/9999/libros`
- **THEN** responde 404 con mensaje propio
