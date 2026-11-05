# catalogo-auxiliar Specification

## Purpose

Mantener el catálogo auxiliar (editoriales, géneros y autores) con capas Router → Service → UoW → Repository → Model, listados paginados con envoltorio, contratos de entrada estrictos y unicidad garantizada por la base.

## Requirements

### Requirement: Listados paginados con envoltorio
`GET /editoriales` y `GET /generos` SHALL devolver `{items, total, page, size, pages}`, con `page` desde 1, `size` de 1 a 100 (por defecto 20), 422 si la página pedida no existe y una página vacía cuando no hay resultados.

#### Scenario: Página válida
- **GIVEN** los datos iniciales (3 editoriales)
- **WHEN** se pide `GET /editoriales?size=2`
- **THEN** responde 200 con 2 ítems, `total` 3, `page` 1, `size` 2 y `pages` 2

#### Scenario: Página inexistente o tamaño fuera de rango
- **WHEN** se pide `GET /editoriales?page=99` o `GET /editoriales?size=500`
- **THEN** responde 422; en el primer caso con «La página 99 no existe: hay 1»

### Requirement: Alta con unicidad garantizada por la base
`POST /editoriales`, `/generos` y `/autores` SHALL responder 201 con el recurso creado, 422 si el cuerpo no cumple el contrato (incluido un campo no declarado) y 409 con mensaje propio si el nombre de una editorial o de un género ya existe (RN-01), sin consulta previa y sin texto de la base (RN-15).

#### Scenario: Nombre repetido
- **WHEN** se hace `POST /generos` con `{"nombre": "Novela"}`
- **THEN** responde 409 `{"detail": "Ya existe un género con ese nombre"}` y no queda ninguna fila nueva

#### Scenario: Campo no declarado
- **WHEN** se hace `POST /generos` con un campo extra
- **THEN** responde 422 (`extra_forbidden`)

### Requirement: Modificación parcial
`PATCH /editoriales/{id}` y `PATCH /autores/{id}` SHALL aplicar solo los campos enviados, responder 404 si el recurso no existe, 409 si el nombre choca con otra editorial y 422 ante un campo no declarado o un `null` explícito.

#### Scenario: Un solo campo
- **WHEN** se hace `PATCH /editoriales/1` con `{"pais": "Uruguay"}`
- **THEN** responde 200 y el nombre de la editorial no cambia

### Requirement: Rutas fuera del parcial
El sistema SHALL NOT exponer `PATCH /generos/{id}` ni `DELETE` de editoriales, géneros o autores.

#### Scenario: Método no permitido
- **WHEN** se pide `PATCH /generos/1` o `DELETE /editoriales/3`
- **THEN** responde 405

### Requirement: Capas con Unit of Work
Cada módulo del catálogo auxiliar SHALL tener un repositorio que herede de `BaseRepository` recibiendo la clase del modelo, y un Unit of Work que lo componga con la sesión de la petición; el router SHALL construir el Unit of Work y el servicio SHALL abrirlo con `async with`, sin que ningún repositorio confirme.

#### Scenario: Escritura rechazada no deja nada
- **GIVEN** un alta cuyo `flush()` viola `uq_editorial_nombre`
- **WHEN** la excepción sale del bloque `async with uow:`
- **THEN** el Unit of Work revierte, el router responde 409 y la base queda como estaba
