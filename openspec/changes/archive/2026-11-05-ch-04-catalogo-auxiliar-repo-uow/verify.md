# Verify — CH-04 `catalogo-auxiliar-repo-uow`

Corrido el 05/11/2026 en la PC del integrante (Windows 10, Python 3.12.10) contra **PostgreSQL 17.11 nativo** (puerto 5432, base `libreria_parcial`), con uvicorn levantado y `python seed.py` antes de cada corrida.

> **Postgres nativo en lugar de Docker:** Docker Desktop no se puede instalar en Windows 10 LTSC 1809. La consigna pide PostgreSQL 16 como mínimo; se usó la 17. Equivalencia comprobada el 04/11: `alembic current` = `33456ccaa692 (head)`, el seed carga los mismos datos y `CH-01_salud.http` da 200/200.

## Tabla de verificación

| Tarea | Prueba (`CH-04_editoriales_generos_autores.http`) | Esperado | Obtenido |
|---|---|---|---|
| 1.2 rojo | 1.1 / 1.4 listados | Envoltorio | 200 con lista suelta |
| 1.2 rojo | 1.2 `page=99` / 1.3 `size=500` | 422 | 200 (parámetros ignorados) |
| 1.2 rojo | 3.2 PATCH con campo extra | 422 | 200 |
| 1.2 rojo | 4.1 `PATCH /generos/1` | 405 | 200 |
| 3.2 verde | 1.1 `GET /editoriales?size=2` | 200, total 3, pages 2 | Igual |
| 3.2 verde | 1.2 `page=99` | 422 «La página 99 no existe: hay 1» | Igual |
| 3.2 verde | 1.3 `size=500` | 422 | Igual (`less_than_equal`) |
| 3.2 verde | 1.4 `GET /generos` | 200, size 20, pages 1 | Igual |
| 3.2 verde | 2.1 / 2.4 nombre repetido | 409 con mensaje propio | Igual, sin texto de la base |
| 3.2 verde | 2.2 / 2.5 / 2.7 altas | 201 (ids 5, 5 y 7) | Igual |
| 3.2 verde | 2.3 / 3.2 campo extra | 422 | Igual (`extra_forbidden`) |
| 3.2 verde | 2.6 autor sin nombre | 422 | Igual (`missing`) |
| 3.2 verde | 3.1 / 3.5 PATCH parcial | 200, solo cambia lo enviado | Igual |
| 3.2 verde | 3.3 / 3.6 inexistente | 404 | Igual |
| 3.2 verde | 3.4 PATCH nombre repetido | 409 | Igual |
| 3.2 verde | 4.1 / 4.2 rutas quitadas | 405 | Igual |
| 3.2 verde | 4.3 `GET /editoriales/abc` | 422 | Igual (`int_parsing`) |

## Lo que no se corrió

- **Guardas de rol**: los POST y PATCH todavía no piden sesión; llegan con CH-10. Cuando esté en main, el `.http` suma el login de `admin@example.com`.
- **Rutas `/{x}/{id}/libros`**: fuera del alcance (CH-05).

## Cómo leer la evidencia

- **Ids 5 en 2.2 y 2.5**: los INSERT rechazados en 2.1 y 2.4 consumieron el 4 de la secuencia; PostgreSQL no lo devuelve. El 2.7 da 7 porque el 422 de 2.6 lo frena el contrato y nunca llega a la base.
- **`Río` en 2.4 y 3.4**: en la primera corrida (06:49) esos dos pedidos dieron **400** porque `curl` en Windows no manda la «í» en UTF-8. Se escapó como `í` (JSON estándar) y se repitió (06:55). Con REST Client dan 409 sin escape. Un cuerpo ilegible da 400, no 500 (RN-15).
- **«Poesia» sin tilde** en 2.3: mismo motivo; el resultado esperado (422 por el campo extra) no depende del nombre.

## Salida completa (06:55)

```text
Evidencia CH-04 — 05/11/2026 06:55
seed: Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, 5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento.

### 1.1 Editoriales paginadas
GET /editoriales?size=2
-> obtenido: 200 {"items":[{"id":1,"nombre":"Letras del Río","pais":"Argentina"},{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"}],"total":3,"page":1,"size":2,"pages":2}

### 1.2 Página que no existe
GET /editoriales?page=99
-> obtenido: 422 {"detail":"La página 99 no existe: hay 1"}

### 1.3 size fuera de rango
GET /editoriales?size=500
-> obtenido: 422 {"detail":[{"type":"less_than_equal","loc":["query","size"],"msg":"Input should be less than or equal to 100","input":"500","ctx":{"le":100}}]}

### 1.4 Géneros por defecto
GET /generos
-> obtenido: 200 {"items":[{"id":1,"nombre":"Novela"},{"id":2,"nombre":"Cuento"},{"id":3,"nombre":"Antología"}],"total":3,"page":1,"size":20,"pages":1}

### 2.1 Género repetido
POST /generos {"nombre":"Novela"}
-> obtenido: 409 {"detail":"Ya existe un género con ese nombre"}

### 2.2 Género nuevo
POST /generos {"nombre":"Ensayo"}
-> obtenido: 201 {"id":5,"nombre":"Ensayo"}

### 2.3 Género con campo extra
POST /generos {"nombre":"Poesia","descripcion":"no existe"}
-> obtenido: 422 {"detail":[{"type":"extra_forbidden","loc":["body","descripcion"],"msg":"Extra inputs are not permitted","input":"no existe"}]}

### 2.4 Editorial repetida
POST /editoriales {"nombre":"Letras del Río","pais":"Argentina"}
-> obtenido: 409 {"detail":"Ya existe una editorial con ese nombre"}

### 2.5 Editorial nueva
POST /editoriales {"nombre":"Ediciones Cuyo","pais":"Argentina"}
-> obtenido: 201 {"id":5,"nombre":"Ediciones Cuyo","pais":"Argentina"}

### 2.6 Autor sin nombre
POST /autores {"nacionalidad":"Argentina"}
-> obtenido: 422 {"detail":[{"type":"missing","loc":["body","nombre"],"msg":"Field required","input":{"nacionalidad":"Argentina"}}]}

### 2.7 Autor nuevo
POST /autores {"nombre":"Antonio Di Benedetto","nacionalidad":"Argentina"}
-> obtenido: 201 {"id":7,"nombre":"Antonio Di Benedetto","nacionalidad":"Argentina"}

### 3.1 PATCH editorial un campo
PATCH /editoriales/1 {"pais":"Uruguay"}
-> obtenido: 200 {"id":1,"nombre":"Letras del Río","pais":"Uruguay"}

### 3.2 PATCH editorial campo extra
PATCH /editoriales/1 {"pais":"Chile","stock":5}
-> obtenido: 422 {"detail":[{"type":"extra_forbidden","loc":["body","stock"],"msg":"Extra inputs are not permitted","input":5}]}

### 3.3 PATCH editorial inexistente
PATCH /editoriales/9999 {"pais":"Chile"}
-> obtenido: 404 {"detail":"Editorial no encontrada"}

### 3.4 PATCH editorial nombre repetido
PATCH /editoriales/2 {"nombre":"Letras del Río"}
-> obtenido: 409 {"detail":"Ya existe una editorial con ese nombre"}

### 3.5 PATCH autor un campo
PATCH /autores/6 {"nacionalidad":"Argentino-francesa"}
-> obtenido: 200 {"id":6,"nombre":"Juan José Saer","nacionalidad":"Argentino-francesa"}

### 3.6 PATCH autor inexistente
PATCH /autores/9999 {"nacionalidad":"Chilena"}
-> obtenido: 404 {"detail":"Autor no encontrado"}

### 4.1 PATCH /generos no existe
PATCH /generos/1 {"nombre":"Novela larga"}
-> obtenido: 405 {"detail":"Method Not Allowed"}

### 4.2 DELETE editorial no existe
DELETE /editoriales/3
-> obtenido: 405 {"detail":"Method Not Allowed"}

### 4.3 id no entero
GET /editoriales/abc
-> obtenido: 422 {"detail":[{"type":"int_parsing","loc":["path","editorial_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}
```
