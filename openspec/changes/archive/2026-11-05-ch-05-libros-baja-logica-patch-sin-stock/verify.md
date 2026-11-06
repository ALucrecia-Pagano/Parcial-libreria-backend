# Verify — CH-05 `libros-baja-logica-patch-sin-stock`

Corrido el 05/11/2026 en la PC del integrante (Windows 10, Python 3.12.10) contra **PostgreSQL 17.11 nativo** (puerto 5432, base `libreria_parcial`), con uvicorn levantado y `python seed.py` antes de cada corrida. Postgres nativo en lugar de Docker: ver la nota del `verify.md` de CH-04.

## Tabla de verificación

| Tarea | Prueba (`C-16_busqueda_paginacion_patch.http`) | Esperado | Obtenido |
|---|---|---|---|
| 1.2 rojo | 1.1–1.5 listados | Envoltorio; 1.3 y 1.4 con 422 | Lista suelta; 1.3 y 1.4 con 200 |
| 1.2 rojo | 3.2 `PATCH {"stock":99}` | 422 | 200, stock 99 sin movimiento |
| 1.2 rojo | 3.3 `PATCH {"isbn":...}` | 422 | 200, ISBN cambiado |
| 1.2 rojo | 4.1 `DELETE /libros/3` | 204 | 409 «No se puede borrar un libro utilizado en ventas» |
| 3.2 verde | 1.1 inyección `' OR '1'='1` | 200, `items` [], `total` 0 | Igual |
| 3.2 verde | 1.2 `titulo=FICC&size=1` | 200, total 1, pages 1 | Igual (sin distinguir mayúsculas) |
| 3.2 verde | 1.3 misma búsqueda `page=2` | 422 «La página 2 no existe: hay 1» | Igual |
| 3.2 verde | 1.4 `size=500` | 422 | Igual |
| 3.2 verde | 1.5 `genero_id=2` | 200, total 2 | Igual |
| 3.2 verde | 2.1 / 2.2 detalle | 422 / 200 con autores | Igual |
| 3.2 verde | 3.1 PATCH un campo | 200, precio y stock sin cambios | Igual (precio 25000.00, stock 10) |
| 3.2 verde | 3.2 / 3.3 / 3.4 | 422 | Igual (`extra_forbidden`, `greater_than`) |
| 3.2 verde | 3.5 inexistente | 404 | Igual |
| 3.2 verde | 4.1 baja de Ficciones | 204 | Igual |
| 3.2 verde | 4.2 / 4.5 / 4.6 dado de baja | 404 | Igual |
| 3.2 verde | 4.3 catálogo | total 4, sin Ficciones | Igual |
| 3.2 verde | 4.4 `GET /ventas/1` | Sigue mostrando «Ficciones» | Igual |
| 3.2 verde | 5.1–5.5 libros por entidad | Solo vigentes; 404 si no existe la entidad | Igual |
| 3.2 verde | Invariante final | Rayuela con stock 10 tras los PATCH | Igual |

## Lo que no se corrió

- **C-13** (reponer, volver a cargar el ISBN dado de baja, segundo vigente → 409): necesita `POST /libros` con `stock_inicial`, que es de CH-06.
- **Guardas de rol** en PATCH y DELETE: llegan con CH-10.

## Cómo leer la evidencia

- **`edici\u00f3n` en 3.1:** `curl` en Windows no manda las tildes en UTF-8, así que el script las escapa (JSON estándar). En una corrida previa (07:28) el script tenía la «ó» literal por un error de Claude y ese pedido dio 400; se corrigió y se repitió (07:30). Con REST Client el pedido da 200 sin escape.
- **Rayuela «(edición aniversario)» desde 4.3:** es el PATCH del 3.1; el stock sigue en 10.

## Salida completa (07:30)

```text
Evidencia CH-05 (C-16) — 05/11/2026 07:30
seed: Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, 5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento.

### 1.1 Inyección ' OR '1'='1
# esperado: 200 items [] total 0
GET /libros?titulo=%27%20OR%20%271%27%3D%271 
-> obtenido: 200 {"items":[],"total":0,"page":1,"size":20,"pages":1}

### 1.2 FICC size=1
# esperado: 200 [Ficciones] total 1 pages 1
GET /libros?titulo=FICC&size=1 
-> obtenido: 200 {"items":[{"id":3,"isbn":"978-950-00-0003-5","titulo":"Ficciones","precio":"22000.00","stock":8,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}}],"total":1,"page":1,"size":1,"pages":1}

### 1.3 ficc size=1 page=2
# esperado: 422 La página 2 no existe: hay 1
GET /libros?titulo=ficc&size=1&page=2 
-> obtenido: 422 {"detail":"La página 2 no existe: hay 1"}

### 1.4 size=500
# esperado: 422
GET /libros?size=500 
-> obtenido: 422 {"detail":[{"type":"less_than_equal","loc":["query","size"],"msg":"Input should be less than or equal to 100","input":"500","ctx":{"le":100}}]}

### 1.5 genero_id=2
# esperado: 200 [Ficciones, Bestiario] total 2
GET /libros?genero_id=2 
-> obtenido: 200 {"items":[{"id":3,"isbn":"978-950-00-0003-5","titulo":"Ficciones","precio":"22000.00","stock":8,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}},{"id":5,"isbn":"978-950-00-0005-9","titulo":"Bestiario","precio":"18000.00","stock":1,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}}],"total":2,"page":1,"size":20,"pages":1}

### 2.1 id no entero
# esperado: 422
GET /libros/abc 
-> obtenido: 422 {"detail":[{"type":"int_parsing","loc":["path","libro_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}

### 2.2 Detalle Rayuela
# esperado: 200 con editorial, género y autores
GET /libros/1 
-> obtenido: 200 {"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela","precio":"25000.00","stock":10,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"},"autores":[{"autor_id":1,"rol":"autor","orden":1,"autor":{"id":1,"nombre":"Julio Cortázar","nacionalidad":"Argentina"}}]}

### 3.1 PATCH un campo
# esperado: 200 titulo nuevo, precio 25000.00, stock 10
PATCH /libros/1 {"titulo":"Rayuela (edici\u00f3n aniversario)"}
-> obtenido: 200 {"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela (edición aniversario)","precio":"25000.00","stock":10,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"},"autores":[{"autor_id":1,"rol":"autor","orden":1,"autor":{"id":1,"nombre":"Julio Cortázar","nacionalidad":"Argentina"}}]}

### 3.2 PATCH stock
# esperado: 422 extra_forbidden
PATCH /libros/1 {"stock":99}
-> obtenido: 422 {"detail":[{"type":"extra_forbidden","loc":["body","stock"],"msg":"Extra inputs are not permitted","input":99}]}

### 3.3 PATCH isbn
# esperado: 422 extra_forbidden
PATCH /libros/1 {"isbn":"978-950-00-9999-9"}
-> obtenido: 422 {"detail":[{"type":"extra_forbidden","loc":["body","isbn"],"msg":"Extra inputs are not permitted","input":"978-950-00-9999-9"}]}

### 3.4 PATCH precio 0
# esperado: 422
PATCH /libros/1 {"precio":"0"}
-> obtenido: 422 {"detail":[{"type":"greater_than","loc":["body","precio"],"msg":"Input should be greater than 0","input":"0","ctx":{"gt":0}}]}

### 3.5 PATCH inexistente
# esperado: 404 Libro no encontrado
PATCH /libros/9999 {"precio":"1000.00"}
-> obtenido: 404 {"detail":"Libro no encontrado"}

### 4.1 DELETE Ficciones
# esperado: 204
DELETE /libros/3 
-> obtenido: 204 

### 4.2 Detalle dado de baja
# esperado: 404
GET /libros/3 
-> obtenido: 404 {"detail":"Libro no encontrado"}

### 4.3 Catálogo sin Ficciones
# esperado: 200 total 4
GET /libros 
-> obtenido: 200 {"items":[{"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela (edición aniversario)","precio":"25000.00","stock":10,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}},{"id":2,"isbn":"978-950-00-0002-8","titulo":"Antología de la literatura fantástica","precio":"30000.00","stock":5,"editorial_id":2,"genero_id":3,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":3,"nombre":"Antología"}},{"id":4,"isbn":"978-950-00-0004-2","titulo":"Respiración artificial","precio":"27000.00","stock":3,"editorial_id":2,"genero_id":1,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}},{"id":5,"isbn":"978-950-00-0005-9","titulo":"Bestiario","precio":"18000.00","stock":1,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}}],"total":4,"page":1,"size":20,"pages":1}

### 4.4 Venta 1 sigue mostrando Ficciones
# esperado: 200 con titulo Ficciones
GET /ventas/1 
-> obtenido: 200 {"id":1,"fecha":"2026-11-05T10:30:08.961971Z","total":"69000.00","cliente":{"id":1,"nombre":"Lucía Fernández","email":"lucia@example.com"},"renglones":[{"libro_id":1,"titulo":"Rayuela (edición aniversario)","cantidad":1,"precio_unitario":"25000.00","subtotal":"25000.00"},{"libro_id":3,"titulo":"Ficciones","cantidad":2,"precio_unitario":"22000.00","subtotal":"44000.00"}]}

### 4.5 DELETE otra vez
# esperado: 404
DELETE /libros/3 
-> obtenido: 404 {"detail":"Libro no encontrado"}

### 4.6 PATCH dado de baja
# esperado: 404
PATCH /libros/3 {"precio":"1000.00"}
-> obtenido: 404 {"detail":"Libro no encontrado"}

### 5.1 Libros de editorial 1
# esperado: 200 [Rayuela]
GET /editoriales/1/libros 
-> obtenido: 200 [{"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela (edición aniversario)","precio":"25000.00","stock":10,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}}]

### 5.2 Libros de género 2
# esperado: 200 [Bestiario]
GET /generos/2/libros 
-> obtenido: 200 [{"id":5,"isbn":"978-950-00-0005-9","titulo":"Bestiario","precio":"18000.00","stock":1,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}}]

### 5.3 Género inexistente
# esperado: 404 Género no encontrado
GET /generos/9999/libros 
-> obtenido: 404 {"detail":"Género no encontrado"}

### 5.4 Libros de Borges
# esperado: 200 [Antología]
GET /autores/2/libros 
-> obtenido: 200 [{"id":2,"isbn":"978-950-00-0002-8","titulo":"Antología de la literatura fantástica","precio":"30000.00","stock":5,"editorial_id":2,"genero_id":3,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":3,"nombre":"Antología"}}]

### 5.5 Autor inexistente
# esperado: 404 Autor no encontrado
GET /autores/9999/libros 
-> obtenido: 404 {"detail":"Autor no encontrado"}


Invariante: el PATCH no tocó el stock (Rayuela debe seguir en 10):
{"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela (edición aniversario)","precio":"25000.00","stock":10,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"},"autores":[{"autor_id":1,"rol":"autor","orden":1,"autor":{"id":1,"nombre":"Julio Cortázar","nacionalidad":"Argentina"}}]}
```
