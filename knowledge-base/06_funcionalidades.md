# Funcionalidades

> **Nota de IDs.** La consigna no usa "E1..E10" ni "épicas": las llama **Ejercicio 1 ... Ejercicio 10** (con su puntaje). Acá se usan los IDs **E1..E10 = Ejercicio 1..10**, que son los que se usan en los criterios de evaluación (`12`). Cada ejercicio es una "épica" de trabajo. E1–E8 van en `parcial/`; **E9 y E10 van en `despliegue/`** (TP caps. 1–4). Puntaje total: 100.

| ID | Ejercicio | Puntos | Dónde |
|---|---|---|---|
| E1 | Proyecto, configuración y ciclo de vida | 6 | `parcial/` |
| E2 | Modelos, relaciones y migraciones | 10 | `parcial/` |
| E3 | Contratos y CRUD | 8 | `parcial/` |
| E4 | Autenticación | 14 | `parcial/` |
| E5 | Autorización | 12 | `parcial/` |
| E6 | Repositorios y Unit of Work | 16 | `parcial/` |
| E7 | Integridad: sólo agregado e intento de acceso | 10 | `parcial/` |
| E8 | Lecturas sin N+1 y asincronía | 6 | `parcial/` |
| E9 | Contenedor: la imagen | 11 | `despliegue/` |
| E10 | Despliegue en el VPS | 7 | `despliegue/` |

---

## E1 — Proyecto, configuración y ciclo de vida (6 pts)

- `Settings` (pydantic-settings) lee del entorno / `.env` no versionado; la URL de la base se arma con un **`@computed_field`**; **sin valores por defecto** para clave de firma ni contraseña de la base (si faltan, la app no arranca).
- Motor asincrónico (con el **tamaño del pool declarado en la configuración**, sec. 4.5) y fábrica de sesiones creados **en el lifespan** y guardados en `app.state`, **no al importar** un módulo (un recurso construido al importar se crea antes de que exista el bucle de eventos; el síntoma —anda al levantar y falla en pruebas, o al revés— no señala la causa).
- `get_session`: toma la fábrica de `app.state`, entrega **una sesión por petición**, creada con **`expire_on_commit=False`**, y la **cierra al terminar**.
- El lifespan calcula **una vez** el **hash ficticio** del login y al apagar hace `dispose()` del motor.
- `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`; **503** si la base no contesta).
- Módulo `health` sólo tiene `router.py`.
- Reglas: RN-04 (base), requisitos no funcionales (sin secretos).

## E2 — Modelos, relaciones y migraciones (10 pts)

- Modelos nuevos y cambios en `Cliente` y `Libro` según `04`, con todas las restricciones, **incluidos los dos índices únicos parciales** (`postgresql_where`): `asignacion_rol` (`usuario_id, rol` WHERE `revocada_en IS NULL`) y `libro` (`isbn` WHERE `borrado_en IS NULL`).
- `Cliente.usuario` devuelve un **objeto**, no una lista. Navegación en los dos extremos. FKs nuevas con índice.
- Esquema **sólo con Alembic** (sin `create_all`). Migración 3 con `--autogenerate`, migración 4 **a mano** (disparador RN-12). Cada una **leída antes de aplicarla** y con comentario que lo diga; si se corrige, el comentario lo explica.
- `upgrade head` sobre base vacía, `downgrade base`, `upgrade head` otra vez.
- Reglas: RN-01, RN-03, RN-12.

## E3 — Contratos y CRUD (8 pts)

- Endpoints de referencia (ver `11`) con **contratos separados de los modelos de tabla**.
- Contratos de entrada con **`extra="forbid"`** (nadie se registra con un rol ni edita el stock por PATCH → RN-11).
- Ninguna respuesta incluye `password_hash`. PATCH con **`exclude_unset`**.
- Códigos: 201 crear, 204 baja de libro, 404 recurso de la ruta inexistente, 409 choque, 422 contrato.
- Listados con `{items, total, page, size, pages}`: `page` ≥ 1, `size` 1..100 (def. 20), página inexistente → 422, `total` con los mismos filtros, cero resultados → una página vacía.
- Búsqueda de libros por título con **parámetros ligados** y sin distinguir mayúsculas.
- Reglas: RN-01, RN-09, RN-11, RN-15.

## E4 — Autenticación (14 pts)

- bcrypt con **costo en configuración** (no fijo en código); toda llamada a bcrypt **fuera del bucle** (`to_thread`) y **bajo un semáforo** que limita cuántas corren a la vez. El **hash se calcula antes de abrir la transacción** (adentro la conexión quedaría tomada ~300 ms sin usar la base).
- Todo campo que termina en bcrypt (también la contraseña del login y la actual del cambio): **máx. 72 bytes** (bytes, no caracteres) → 422, nunca 500.
- **Orden del login**: (1) límite de intentos (RN-07; una consulta; 429 + `Retry-After` sin calcular ningún hash); (2) verificación contra el hash del usuario o contra el **hash ficticio** si el correo no existe (RN-08).
- Token JWT firmado con `sub`, `exp` y los **roles vigentes al emitirlo**. Viaja **sólo** en cookie `access_token` (`HttpOnly`, `SameSite=Lax`, `Max-Age` = duración del token, `Secure` configurable). El cuerpo del login **no** trae el token. La dependencia lo lee de `request.cookies`.
- Login tradicional: la sesión dura hasta que el token vence o se cierra sesión; cambiar la contraseña no invalida sesiones ni emite token nuevo.
- Existen: registro (RN-02), cierre de sesión (borra la cookie), `GET /auth/yo` (usuario, roles vigentes y los que dice el token), cambio de contraseña.
- Reglas: RN-02, RN-07, RN-08.

## E5 — Autorización (12 pts)

- `get_usuario_actual`: **401** si no hay cookie, token inválido o vencido, o usuario inexistente/inactivo.
- `requiere_rol`: **403**; consulta los **roles vigentes en la base en cada petición** (RN-04): revocar un rol le quita el permiso a una sesión ya abierta sin esperar al vencimiento del token.
- El ADMIN asigna roles con vencimiento opcional (con zona y en el futuro; si no, 422) y los revoca sin borrar la fila; reasignar un rol vencido cierra la anterior y abre una nueva.
- Autoprotección (RN-05).
- Cambio obligatorio de contraseña con **dos grupos de rutas en `main.py`** (abierto y protegido; el protegido monta el control **una sola vez**) (RN-06).
- "Lo propio" sólo pide autenticación (RN-14): `/mis-ventas`; `GET /ventas/{id}` decide en el servicio (personal o dueño, si no 403).
- Historial de seguridad (RN-16): el seed registra los datos iniciales con actor `SISTEMA` (texto, no usuario).
- Reglas: RN-03, RN-04, RN-05, RN-06, RN-14, RN-16.

## E6 — Repositorios y Unit of Work (16 pts)

- `BaseRepository[T]`: el constructor recibe **la sesión y la clase del modelo** (los genéricos se borran en runtime); ofrece al menos `get_by_id`, `get_all`, `count`, `add`, `update`, `delete`.
- `SoftDeleteRepository[T]` hereda de él; lo usa `Libro`; **filtra los dados de baja** y agrega `get_by_id_including_deleted` y `soft_delete`.
- `add`/`update` hacen **`flush()`, nunca `commit()`**: ningún repositorio confirma.
- Cada entidad tiene su repositorio, con métodos nombrados **por lo que traen**; la **precarga se declara dentro del método** que la necesita.
- `UnitOfWork` base: gestor de contexto asincrónico; **confirma al salir** del bloque, **revierte** si sale con excepción, **no cierra la sesión** (no la creó).
- UoW por módulo, que compone los repositorios necesarios con **la misma sesión**. El router construye el UoW con una dependencia y se lo pasa al servicio **sin abrirlo**; el servicio lo abre con `async with` y **nunca lo construye**.
- RN-02, RN-10 y RN-16 se escriben **cada una en un solo bloque**.
- `get_usuario_actual` y `requiere_rol` reciben **la misma sesión** que el UoW (si no, cada petición autenticada tomaría dos conexiones del pool).
- El **stock se escribe en un único punto** (RN-11) usado por alta de libro, reposición y registro de ventas.

## E7 — Integridad: sólo agregado e intento de acceso (10 pts)

- El **disparador** de la 4ª migración rechaza cualquier `UPDATE` o `DELETE` sobre `movimiento_stock`, venga de donde venga (RN-12).
- Cada intento de login, correcto o fallido, se anota en `intento_acceso` desde una **sesión y transacción propias**, que se confirman siempre: es la **única escritura del sistema que no comparte la transacción de su petición**, porque el fallo que se quiere contar es el mismo que la revierte. El código lo declara en **un comentario que dice tres cosas**: (1) qué hace distinto, (2) por qué no puede compartir la transacción, (3) cuál es su costo (deja filas aunque la petición falle).
- El segundo mecanismo (rol de base sin permiso de UPDATE/DELETE) **no se pide**; sería defensa en profundidad.

## E8 — Lecturas sin N+1 y asincronía (6 pts)

- Toda respuesta con datos de una relación los obtiene con **carga anticipada declarada en el repositorio**. Ninguna lectura depende de carga perezosa.
- El detalle de una venta (con su cliente, los renglones y el libro de cada renglón, **incluso si el libro está dado de baja**) se resuelve con **número fijo de consultas** que no crece con la cantidad de renglones (C-15).
- Todos los handlers `async def`; ninguna llamada bloqueante.
- Al registrar una venta se agenda con `BackgroundTasks` el aviso del comprobante (simulado: `await asyncio.sleep(0.5)` + mensaje en el registro), que corre **después de enviar la respuesta y sólo si la operación se confirmó**. El mensaje debe verse con el arranque normal de uvicorn (el logger propio sin configurar no aparece).

## E9 — Contenedor: la imagen (11 pts) — `despliegue/`

Ver `13_despliegue.md`. Dockerfile desde `python:3.12-alpine` (< 100 MB la base), capas en orden, usuario sin privilegios, sin secretos, migraciones al arrancar, `HEALTHCHECK` en `/health/ready`, ejecución con `docker run` y `--env-file`.

## E10 — Despliegue en el VPS (7 pts) — `despliegue/`

Ver `13_despliegue.md`. TP caps. 1–4 en línea en la URL declarada, `DEPLOY.md` completo, casos D-01..D-08 con evidencia en `evidencia/`.

---

## Historias de usuario derivadas (por actor)

| ID | Historia | Ejercicio | Reglas |
|---|---|---|---|
| US-01 | Como visitante quiero ver el catálogo paginado y buscar por título sin iniciar sesión | E3 | RN-15 |
| US-02 | Como visitante quiero registrarme y quedar con rol CLIENTE y ficha de cliente | E4 | RN-01, RN-02 |
| US-03 | Como usuario quiero iniciar sesión sin que se revele qué cuentas existen | E4 | RN-07, RN-08 |
| US-04 | Como ADMIN quiero dar de alta personal con contraseña provisoria | E5 | RN-16 |
| US-05 | Como ADMIN quiero asignar/revocar roles con vigencia y que se aplique al instante | E5 | RN-03, RN-04, RN-05, RN-16 |
| US-06 | Como VENDEDOR quiero registrar una venta que descuente stock de forma atómica | E6/E8 | RN-09, RN-10, RN-11 |
| US-07 | Como ADMIN quiero reponer stock y ver los movimientos de un libro | E6 | RN-11, RN-12 |
| US-08 | Como ADMIN quiero dar de baja un libro y poder recargar el ISBN | E2 | RN-01, RN-13 |
| US-09 | Como CLIENTE quiero ver mis compras y sólo las mías | E5 | RN-14 |
| US-10 | Como usuario con contraseña provisoria quiero cambiarla y seguir con la misma sesión | E4/E5 | RN-06, RN-16 |
