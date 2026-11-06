# Verify — CH-06 `stock-punto-unico-reponer-movimientos`

Corrido el 06/11/2026 en la PC del integrante (Windows 10, Python 3.12.10) contra **PostgreSQL 17.11 nativo** (ver la nota del `verify.md` de CH-04), con uvicorn levantado. El script de evidencia corre `python seed.py` antes de los pedidos.

## Tabla de verificación

| Tarea | Prueba (`C-13_baja_reposicion_isbn.http`) | Esperado | Obtenido |
|---|---|---|---|
| 1.2 rojo | 1.1–1.5, 2.3, 3.2 `/reponer` y `/movimientos` | 200/422/404/401/409 | 404 (las rutas no existían) |
| 1.2 rojo | 4.1 alta con `"stock": 3` | 422 | 201 con stock 3 **sin movimiento** |
| 3.2 verde | 0 login ADMIN | 200 + cookie | Igual |
| 3.2 verde | 1.1 reponer 5 | 200 movimiento «Reposición» +5, `usuario_id` 1 | Igual |
| 3.2 verde | 1.2 movimientos | Stock inicial +11, Venta −1, Reposición +5 | Igual (suma 15) |
| 3.2 verde | 1.3 / 1.4 / 1.5 | 422 / 404 / 401 | Igual |
| 3.2 verde | 2.1 / 2.2 baja | 204; catálogo total 4 sin Rayuela | Igual |
| 3.2 verde | 2.3 reponer dado de baja | 409 | Igual («No se puede reponer un libro dado de baja») |
| 3.2 verde | 3.1 / 3.2 alta con el mismo ISBN | 201 stock 4; movimiento «Stock inicial» +4 | Igual (id 6) |
| 3.2 verde | 3.3 segundo vigente | 409 «Ya existe un libro activo con ese ISBN» | Igual |
| 3.2 verde | 3.4 venta 1 | Sigue mostrando «Rayuela» (libro 1) | Igual |
| 3.2 verde | 4.1 alta con `stock` | 422 `extra_forbidden` | Igual |
| 3.2 verde | 4.2 / 4.3 alta con `stock_inicial` 0 | 201 stock 0, sin movimientos | Igual (id 8) |
| 3.2 verde | Invariante en los 6 libros vigentes | stock = suma de movimientos | **OK en todos** |

## Cómo leer la evidencia

- **Id 8 en 4.2 (no 7):** el INSERT rechazado en 3.3 consumió el 7 de la secuencia (mismo caso que en CH-04).
- **`seed:` vacío:** el script captura la salida de `seed.py` y en la consola de Windows llegó vacía (codificación de la tubería). El seed sí corrió: los movimientos 1–7 tienen la marca de hora de esa corrida (10:48:06) y el estado inicial coincide (Rayuela con +11 y −1).
- **El invariante no incluye a Rayuela (libro 1)** porque está dado de baja y el catálogo no la lista; su suma se ve en 1.2 (15 = 11 − 1 + 5) antes de la baja.
- La guarda de ADMIN de los POST y del GET de movimientos la pone `main.py` (CH-10); el 401 de 1.5 lo confirma.

## Salida completa (07:48)

```text
Evidencia CH-06 (C-13) — 06/11/2026 07:48
seed: 

### 0 Login admin
# esperado: 200 + cookie access_token
POST /auth/login {"email": "admin@example.com", "password": "Secreto1234!"}
-> obtenido: 200 {"mensaje":"Sesión iniciada","debe_cambiar_password":false,"expira_en_segundos":1800}

### 1.1 Reponer 5 Rayuela
# esperado: 200 movimiento Reposición +5
POST /libros/1/reponer {"cantidad": 5}
-> obtenido: 200 {"id":8,"libro_id":1,"venta_id":null,"usuario_id":1,"cantidad":5,"motivo":"Reposición","cuando":"2026-11-06T10:48:09.603495Z"}

### 1.2 Movimientos Rayuela
# esperado: 200 [Stock inicial +11, Venta -1, Reposición +5]
GET /libros/1/movimientos
-> obtenido: 200 [{"id":1,"libro_id":1,"venta_id":null,"usuario_id":1,"cantidad":11,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:06.845981Z"},{"id":6,"libro_id":1,"venta_id":1,"usuario_id":3,"cantidad":-1,"motivo":"Venta","cuando":"2026-11-06T10:48:06.845981Z"},{"id":8,"libro_id":1,"venta_id":null,"usuario_id":1,"cantidad":5,"motivo":"Reposición","cuando":"2026-11-06T10:48:09.603495Z"}]

### 1.3 Reponer 0
# esperado: 422
POST /libros/1/reponer {"cantidad": 0}
-> obtenido: 422 {"detail":[{"type":"greater_than","loc":["body","cantidad"],"msg":"Input should be greater than 0","input":0,"ctx":{"gt":0}}]}

### 1.4 Reponer inexistente
# esperado: 404
POST /libros/9999/reponer {"cantidad": 5}
-> obtenido: 404 {"detail":"Libro no encontrado"}

### 1.5 Reponer sin sesión
# esperado: 401
POST /libros/2/reponer {"cantidad": 5}
-> obtenido: 401 {"detail":"No autenticado"}

### 2.1 Baja Rayuela
# esperado: 204
DELETE /libros/1
-> obtenido: 204 

### 2.2 Catálogo sin Rayuela
# esperado: 200 total 4
GET /libros
-> obtenido: 200 {"items":[{"id":2,"isbn":"978-950-00-0002-8","titulo":"Antología de la literatura fantástica","precio":"30000.00","stock":5,"editorial_id":2,"genero_id":3,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":3,"nombre":"Antología"}},{"id":3,"isbn":"978-950-00-0003-5","titulo":"Ficciones","precio":"22000.00","stock":8,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}},{"id":4,"isbn":"978-950-00-0004-2","titulo":"Respiración artificial","precio":"27000.00","stock":3,"editorial_id":2,"genero_id":1,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}},{"id":5,"isbn":"978-950-00-0005-9","titulo":"Bestiario","precio":"18000.00","stock":1,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}}],"total":4,"page":1,"size":20,"pages":1}

### 2.3 Reponer dado de baja
# esperado: 409
POST /libros/1/reponer {"cantidad": 5}
-> obtenido: 409 {"detail":"No se puede reponer un libro dado de baja"}

### 3.1 Alta mismo ISBN
# esperado: 201 stock 4
POST /libros {"isbn": "978-950-00-0001-1", "titulo": "Rayuela", "precio": "26000.00", "stock_inicial": 4, "editorial_id": 1, "genero_id": 1, "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]}
-> obtenido: 201 {"id":6,"isbn":"978-950-00-0001-1","titulo":"Rayuela","precio":"26000.00","stock":4,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"},"autores":[{"autor_id":1,"rol":"autor","orden":1,"autor":{"id":1,"nombre":"Julio Cortázar","nacionalidad":"Argentina"}}]}

### 3.2 Movimientos del nuevo
# esperado: 200 [Stock inicial +4]
GET /libros/6/movimientos
-> obtenido: 200 [{"id":9,"libro_id":6,"venta_id":null,"usuario_id":1,"cantidad":4,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:17.882785Z"}]

### 3.3 Segundo vigente mismo ISBN
# esperado: 409 Ya existe un libro activo con ese ISBN
POST /libros {"isbn": "978-950-00-0001-1", "titulo": "Rayuela (otra edición)", "precio": "26000.00", "stock_inicial": 1, "editorial_id": 1, "genero_id": 1, "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]}
-> obtenido: 409 {"detail":"Ya existe un libro activo con ese ISBN"}

### 3.4 Venta 1 sigue mostrando Rayuela
# esperado: 200 renglón libro_id 1 titulo Rayuela
GET /ventas/1
-> obtenido: 200 {"id":1,"fecha":"2026-11-06T10:48:06.830343Z","total":"69000.00","cliente":{"id":1,"nombre":"Lucía Fernández","email":"lucia@example.com"},"renglones":[{"libro_id":3,"titulo":"Ficciones","cantidad":2,"precio_unitario":"22000.00","subtotal":"44000.00"},{"libro_id":1,"titulo":"Rayuela","cantidad":1,"precio_unitario":"25000.00","subtotal":"25000.00"}]}

### 4.1 Alta con stock
# esperado: 422 extra_forbidden
POST /libros {"isbn": "978-950-00-0007-3", "titulo": "Libro de prueba", "precio": "10000.00", "stock": 3, "editorial_id": 1, "genero_id": 1, "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]}
-> obtenido: 422 {"detail":[{"type":"extra_forbidden","loc":["body","stock"],"msg":"Extra inputs are not permitted","input":3}]}

### 4.2 Alta stock_inicial 0
# esperado: 201 stock 0
POST /libros {"isbn": "978-950-00-0008-0", "titulo": "Libro sin stock", "precio": "10000.00", "stock_inicial": 0, "editorial_id": 1, "genero_id": 1, "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]}
-> obtenido: 201 {"id":8,"isbn":"978-950-00-0008-0","titulo":"Libro sin stock","precio":"10000.00","stock":0,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"},"autores":[{"autor_id":1,"rol":"autor","orden":1,"autor":{"id":1,"nombre":"Julio Cortázar","nacionalidad":"Argentina"}}]}

### 4.3 Movimientos del alta con 0
# esperado: 200 [] (sin movimiento)
GET /libros/8/movimientos
-> obtenido: 200 []

### Invariante: stock = SUM(movimientos) en cada libro vigente
### 5.0 Catálogo completo
# esperado: 200
GET /libros?size=100
-> obtenido: 200 {"items":[{"id":2,"isbn":"978-950-00-0002-8","titulo":"Antología de la literatura fantástica","precio":"30000.00","stock":5,"editorial_id":2,"genero_id":3,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":3,"nombre":"Antología"}},{"id":3,"isbn":"978-950-00-0003-5","titulo":"Ficciones","precio":"22000.00","stock":8,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}},{"id":4,"isbn":"978-950-00-0004-2","titulo":"Respiración artificial","precio":"27000.00","stock":3,"editorial_id":2,"genero_id":1,"editorial":{"id":2,"nombre":"Ediciones del Plata Sur","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}},{"id":5,"isbn":"978-950-00-0005-9","titulo":"Bestiario","precio":"18000.00","stock":1,"editorial_id":3,"genero_id":2,"editorial":{"id":3,"nombre":"Editorial Sudamérica Austral","pais":"Argentina"},"genero":{"id":2,"nombre":"Cuento"}},{"id":6,"isbn":"978-950-00-0001-1","titulo":"Rayuela","precio":"26000.00","stock":4,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}},{"id":8,"isbn":"978-950-00-0008-0","titulo":"Libro sin stock","precio":"10000.00","stock":0,"editorial_id":1,"genero_id":1,"editorial":{"id":1,"nombre":"Letras del Río","pais":"Argentina"},"genero":{"id":1,"nombre":"Novela"}}],"total":6,"page":1,"size":100,"pages":1}

### 5.2 Movimientos libro 2
# esperado: 200
GET /libros/2/movimientos
-> obtenido: 200 [{"id":2,"libro_id":2,"venta_id":null,"usuario_id":1,"cantidad":5,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:06.845981Z"}]

libro 2 (Antología de la literatura fantástica): stock 5 | suma 5 -> OK
### 5.3 Movimientos libro 3
# esperado: 200
GET /libros/3/movimientos
-> obtenido: 200 [{"id":3,"libro_id":3,"venta_id":null,"usuario_id":1,"cantidad":10,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:06.845981Z"},{"id":7,"libro_id":3,"venta_id":1,"usuario_id":3,"cantidad":-2,"motivo":"Venta","cuando":"2026-11-06T10:48:06.845981Z"}]

libro 3 (Ficciones): stock 8 | suma 8 -> OK
### 5.4 Movimientos libro 4
# esperado: 200
GET /libros/4/movimientos
-> obtenido: 200 [{"id":4,"libro_id":4,"venta_id":null,"usuario_id":1,"cantidad":3,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:06.845981Z"}]

libro 4 (Respiración artificial): stock 3 | suma 3 -> OK
### 5.5 Movimientos libro 5
# esperado: 200
GET /libros/5/movimientos
-> obtenido: 200 [{"id":5,"libro_id":5,"venta_id":null,"usuario_id":1,"cantidad":1,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:06.845981Z"}]

libro 5 (Bestiario): stock 1 | suma 1 -> OK
### 5.6 Movimientos libro 6
# esperado: 200
GET /libros/6/movimientos
-> obtenido: 200 [{"id":9,"libro_id":6,"venta_id":null,"usuario_id":1,"cantidad":4,"motivo":"Stock inicial","cuando":"2026-11-06T10:48:17.882785Z"}]

libro 6 (Rayuela): stock 4 | suma 4 -> OK
### 5.8 Movimientos libro 8
# esperado: 200
GET /libros/8/movimientos
-> obtenido: 200 []

libro 8 (Libro sin stock): stock 0 | suma 0 -> OK
INVARIANTE: OK en todos los libros
```
