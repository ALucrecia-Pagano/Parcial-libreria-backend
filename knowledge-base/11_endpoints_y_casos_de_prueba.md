# Endpoints de referencia y casos de prueba

> Tablas de endpoints confirmadas con la consigna oficial (págs. 16–18); ya no hay verbos inferidos (IN-01/IN-02 resueltas). Los ejemplos de cuerpo son los del PDF.

Toda ruta del grupo **protegido** responde además **401** sin sesión y **403** con el cambio de contraseña pendiente.

## Grupo abierto (no pide `requiere_rol` ni el control de cambio obligatorio)

| Método | Ruta | Quién | Códigos |
|---|---|---|---|
| GET | `/health/live` | Cualquiera | 200 |
| GET | `/health/ready` | Cualquiera | 200, 503 |
| POST | `/auth/registro` | Cualquiera | 201, 409, 422 |
| POST | `/auth/login` | Cualquiera | 200, 401, 422, 429 |
| POST | `/auth/logout` | Cualquiera (funciona sin sesión) | 200 |
| GET | `/auth/yo` | Autenticado | 200, 401 |
| POST | `/auth/cambiar-password` | Autenticado (401 también si la `password_actual` es incorrecta, DD-30) | 200, 401, 422 |
| GET | `/libros` (`page`, `size`, `titulo`, `genero_id`) | Cualquiera | 200, 422 |
| GET | `/libros/{id}` | Cualquiera | 200, 404, 422 |
| GET | `/editoriales`, `/generos` (`page`, `size`) | Cualquiera | 200, 422 |
| GET | `/editoriales/{id}/libros`, `/generos/{id}/libros`, `/autores/{id}/libros` | Cualquiera | 200, 404 |

## Grupo protegido (además: 401 sin sesión, 403 con cambio de contraseña pendiente)

### ADMIN

| Método | Ruta | Códigos |
|---|---|---|
| POST | `/usuarios` (alta de personal, con contraseña provisoria) | 201, 409, 422 |
| GET | `/usuarios/{id}/roles` | 200, 404 |
| POST | `/usuarios/{id}/roles` | 201, 404, 409, 422 |
| DELETE | `/usuarios/{id}/roles/{rol}` | 200, 404, 409 |
| GET | `/eventos` (`page`, `size`) | 200, 422 |
| POST | `/editoriales`, `/generos`, `/autores` | 201, 409, 422 |
| PATCH | `/editoriales/{id}`, `/autores/{id}` (**no hay** PATCH de `/generos`) | 200, 404, 409, 422 |
| POST | `/libros` (con `autores` y `stock_inicial`) | 201, 409, 422 |
| PATCH | `/libros/{id}` (título y precio; el stock no) | 200, 404, 409, 422 |
| DELETE | `/libros/{id}` | 204, 404 |
| POST | `/libros/{id}/reponer` | 200, 404, 409, 422 |
| GET | `/libros/{id}/movimientos` | 200, 404 |

### VENDEDOR o ADMIN

| Método | Ruta | Códigos |
|---|---|---|
| POST | `/clientes` | 201, 409, 422 |
| GET, PATCH | `/clientes/{id}` (con su perfil) | 200, 404, 409, 422 |
| POST | `/clientes/{id}/perfil` | 201, 404, 409 |
| GET | `/clientes/{id}/ventas` | 200, 404 |
| POST | `/ventas` (con `renglones`) | 201, 409, 422 |
| GET | `/ventas` (`page`, `size`) | 200, 422 |

### Sin `requiere_rol` (decide el servicio)

| Método | Ruta | Quién | Códigos |
|---|---|---|---|
| GET | `/ventas/{id}` | El personal, o el cliente dueño de la venta (el servicio decide) | 200, 403, 404 |
| GET | `/mis-ventas` (`page`, `size`) | Autenticado | 200, 422 |

### Cuerpos de ejemplo (del PDF)

`POST /ventas` (el mismo del TP; **no** viajan precio, total ni fecha):
```json
{ "cliente_id": 2, "renglones": [ { "libro_id": 1, "cantidad": 2 }, { "libro_id": 4, "cantidad": 1 } ] }
```
`POST /libros` (viaja `stock_inicial` en lugar de `stock`; el alta deja el movimiento "Stock inicial"):
```json
{ "isbn": "978-950-00-0006-6", "titulo": "Los que aman, odian", "precio": "21000.00", "stock_inicial": 4,
  "editorial_id": 1, "genero_id": 1,
  "autores": [ { "autor_id": 3, "rol": "coautor", "orden": 1 }, { "autor_id": 4, "rol": "coautor", "orden": 2 } ] }
```
Respuesta del login (el token viaja en `Set-Cookie`, no en el cuerpo):
```json
{ "mensaje": "Sesión iniciada", "debe_cambiar_password": false, "expira_en_segundos": 1800 }
```
Listado `GET /libros?size=2` (5 libros; `page=4` → 422 "La página 4 no existe: hay 3"):
```json
{ "items": [ {"id":1,"isbn":"978-950-00-0001-1","titulo":"Rayuela","precio":"25000.00","stock":10},
             {"id":2,"isbn":"978-950-00-0002-8","titulo":"Antología de la literatura fantástica","precio":"30000.00","stock":5} ],
  "total": 5, "page": 1, "size": 2, "pages": 3 }
```

## Casos de prueba C (en `parcial/test/C-xx_tema.http`; antes de cada archivo: `python seed.py`)

Nombres: `C-xx_tema.http` (p. ej. `C-05_limite_intentos.http`). Los `C-01.http`..`C-08.http` del TP se **borran** de `parcial/test/` (siguen en `despliegue/test/`; DD-29). La lista de archivos por caso está en `CHANGES.md` (matriz de casos C).

Cada caso lleva su respuesta esperada **en un comentario**. C-14 va en `test/solo_agregado.sql`. Evidencia (en `parcial/evidencia/`): captura/consola de **C-15** (2 y 4 renglones) y captura `psql` de **C-14**.

| Caso | Qué se demuestra | Resultado esperado |
|---|---|---|
| **C-01** | Un parámetro de ruta que no es entero, con la sesión iniciada | 422, sin ejecutar el handler |
| **C-02** | Registro; correo repetido de usuario y de cliente | 201; 409 con mensaje propio, y el registro rechazado no deja ninguna fila suelta |
| **C-03** | La cookie del login | `Set-Cookie` con `HttpOnly`, `SameSite=Lax` y `Max-Age`; el cuerpo sin token; sin cookie o con `Authorization: Bearer`, 401 |
| **C-04** | Correo existente con contraseña mala, y correo inexistente | 401 con el mismo cuerpo y un tiempo parecido |
| **C-05** | Seis intentos fallidos seguidos | El sexto, 429 con `Retry-After` y en pocos milisegundos; los cinco fallos están en `intento_acceso` |
| **C-06** | 401 contra 403, y lo propio | Sin sesión, 401; un vendedor que crea un libro, 403; la cliente ve su venta (200) y no la ajena (403) |
| **C-07** | Revocar un rol con la sesión abierta; vencimientos inválidos | La misma cookie, 403 en la petición siguiente; `/auth/yo` muestra la diferencia; la fila revocada sigue. Un vencimiento en el pasado o sin zona horaria, 422 |
| **C-08** | Autoprotección | El administrador no se revoca su ADMIN: 409 |
| **C-09** | Cambio obligatorio | Bloqueado (403) salvo `/auth`; después del cambio, `debe_cambiar_password` queda en falso y la misma cookie sirve para las rutas protegidas (200), sin iniciar sesión de nuevo. Con la contraseña actual incorrecta, 401 (DD-30) |
| **C-10** | Venta válida con dos renglones | 201 con los precios copiados y el total; el stock de cada libro bajó, hay un movimiento por renglón y el aviso sale en el registro después de la respuesta |
| **C-11** | Venta con Rayuela (1 ejemplar, alcanza) y Bestiario (2 ejemplares, hay 1) | 409; no hay venta nueva, ni descuentos, ni movimientos: el stock de Rayuela sigue en 10 y la suma de movimientos coincide con el stock en los cinco libros |
| **C-12** | Venta con un cliente o un libro inexistente, o con un libro dado de baja | 409 en los tres, sin dejar escrituras |
| **C-13** | Reponer un libro; darlo de baja; volver a cargar el mismo ISBN | Reposición 200 con su movimiento; baja 204; el libro deja de aparecer en el catálogo; el alta con el mismo ISBN, 201; un segundo vigente con ese ISBN, 409; la venta vieja sigue mostrando el título |
| **C-14** | `UPDATE` y `DELETE` sobre `movimiento_stock` en `psql` | Los dos, rechazados por el disparador |
| **C-15** | Detalle de una venta con 2 y con 4 renglones | La misma cantidad de consultas en la consola |
| **C-16** | Búsqueda con `' OR '1'='1`; paginación con filtro; PATCH parcial; PATCH del stock | Lista vacía con total 0; con `titulo=ficc&size=1`, total 1 y pages 1, y `page=2` da 422; `size=500`, 422; sólo cambia lo enviado; el PATCH con `stock`, 422 |

**Varias sesiones a la vez (REST Client)**: cada login se nombra con `# @name` y los pedidos de esa sesión llevan `# @no-cookie-jar` y el encabezado `Cookie: {{loginAdmin.response.headers.Set-Cookie}}`. Así un mismo archivo puede tener la sesión del administrador y la del vendedor al mismo tiempo (necesario para C-07).

## Casos D (sobre el TP caps. 1–4 desplegado en el VPS; evidencia en `despliegue/evidencia/`)

| Caso | Qué se demuestra | Resultado esperado |
|---|---|---|
| **D-01** | `docker images` con la imagen base y con la del proyecto | `python:3.12-alpine` por debajo de los 100 MB, y el Dockerfile parte de ella |
| **D-02** | Servidor limpio: `docker build` y `docker run`; después `docker ps` | El contenedor en estado `healthy`; en `docker logs`, las migraciones del TP aplicadas al arrancar |
| **D-03** | Desde afuera del VPS, en la URL pública: `GET /health/ready`, `GET /libros/` con los datos iniciales cargados y `POST /ventas/` con el cuerpo de ejemplo del TP | 200; 200 con la lista de libros; 201 con los precios copiados de cada libro y el total calculado |
| **D-04** | `docker rm -f libreria` y el mismo `docker run` otra vez | Vuelve a estar `healthy`, los datos siguen —la base no vive en el contenedor— y las migraciones no se repiten |
| **D-05** | Correr la imagen sin `DATABASE_URL` | El contenedor no queda sirviendo: termina con un error, porque el TP no trae ninguna dirección de base por defecto |
| **D-06** | Contenido de la imagen | No hay `.env` (`docker run --rm --entrypoint ls <imagen> -a /app`) y `docker run --rm --entrypoint env <imagen>` no muestra `DATABASE_URL` ni ninguna contraseña |
| **D-07** | Usuario del proceso | `docker exec libreria id` no es root |
| **D-08** | La venta registrada en el caso D-03 | El aviso del comprobante aparece en `docker logs libreria` después de la línea de la respuesta |

> Nota D-08: el aviso con `BackgroundTasks` existe en el TP caps. 1–4. El texto de E8 lo pide para el parcial; D-08 lo verifica en el TP desplegado. El TP ya trae `BackgroundTasks` en `ventas/tasks.py` (P-18 resuelta): sólo hay que verificar que el aviso se vea en `docker logs`.
