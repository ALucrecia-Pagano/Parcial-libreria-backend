# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Numeración RN del parcial reemplaza a la del TP
**Decisión**: usar sólo RN-01..RN-16 del parcial; no citar las RN del TP.
**Contexto**: la consigna dice que las reglas "se numeran de nuevo y reemplazan a las del TP en lo que se superponen".
**Alternativas**: mantener ambas numeraciones con prefijo. **Justificación**: la corrección usa los códigos del parcial. **Trade-off**: el README/commits del TP citan otras RN; hay que tener cuidado al leerlos.

### DD-02 — `test/` sólo con `.http` y un `solo_agregado.sql`; sin pytest
**Decisión**: no se escribe ningún test `.py` ni pytest (instrucción del profesor).
**Contexto**: la consigna pide "archivos `.http` ... y un `test/solo_agregado.sql` para el caso C-14". Esto también prevalece sobre el modo Strict TDD del flujo del equipo.
**Alternativas**: pytest + httpx. **Justificación**: instrucción expresa; los casos C se demuestran con `.http`. **Trade-off**: no hay regresión automática; la verificación es manual con `python seed.py` antes de cada archivo.

### DD-03 — Todo el trabajo del parcial va en `parcial/`; `despliegue/` sin tocar lógica
**Decisión**: caps. 5 y 6 sólo en `parcial/`; en `despliegue/` sólo `Dockerfile`, `.dockerignore`, `env.example`, `DEPLOY.md`, `evidencia/`.
**Justificación**: la consigna lo exige; los D-cases se prueban sobre el TP caps. 1–4. **Excepción**: defecto propio que impida arrancar en contenedor (ej. ruta de salud que no responde como pedía la consigna del TP): se corrige y se anota en `DEPLOY.md`.

### DD-04 — Dos configuraciones distintas
**Decisión**: `parcial/` usa `POSTGRES_*` + `Settings` (pydantic-settings); `despliegue/` mantiene `DATABASE_URL` + `SQL_ECHO` (la del TP).
**Justificación**: la consigna lo define así para cada proyecto. **Riesgo**: confundir `.env` de uno con el otro.

### DD-05 — Autorización con roles de la base, no del token
**Decisión**: `requiere_rol` consulta `asignacion_rol` en cada petición (RN-04); el token lleva roles sólo informativos.
**Justificación**: revocar un rol debe surtir efecto sin esperar el vencimiento. **Trade-off**: una consulta por petición (compartiendo la sesión del UoW para no tomar dos conexiones del pool).

### DD-06 — `intento_acceso` en sesión y transacción propias
**Decisión**: el intento se escribe fuera de la transacción de la petición y siempre se confirma. Es la **única** excepción a "una transacción por petición".
**Justificación**: el fallo que se quiere contar es el mismo que revierte la transacción de la petición. **Costo**: deja filas aunque la petición falle. Debe declararse en un **comentario** con esas tres cosas (qué hace distinto, por qué no puede compartir, costo).

### DD-07 — Sólo-agregado por disparador (un solo mecanismo)
**Decisión**: disparador en migración 4 escrita a mano. **No** se implementa el segundo mecanismo (rol de base sin permiso) porque el parcial usa un solo rol de base y "cualquiera de los dos alcanza".

### DD-08 — Hash bcrypt fuera del bucle, antes de abrir la transacción, con semáforo
**Justificación**: bcrypt tarda ~300 ms; dentro de la transacción tomaría la conexión sin usar la base; en el bucle bloquearía el servidor.

### DD-09 — Dos grupos de rutas en `main.py`
**Justificación**: FastAPI suma dependencias y no las resta; el grupo protegido monta el control de cambio obligatorio una vez; el abierto no puede heredarlo (`/auth` debe funcionar con cambio pendiente).

### DD-10 — Stock con punto único de escritura y movimientos
**Decisión**: `libro.stock` = suma de movimientos; el stock sólo se toca a través de un único punto (alta, reposición, venta). `PATCH` con `stock` → 422 por `extra="forbid"`.

### DD-11 — Despliegue: base nueva `libreria` en el PostgreSQL existente del VPS
**Decisión**: reutilizar el PostgreSQL ya corriendo en EasyPanel (proyecto "calculadora", servicio "db", host interno `calculadora_db`, puerto 5432, usuario `calculadora`) y crear en él una base nueva `libreria`. El contenedor se conecta por la red interna de EasyPanel; el 5432 **no** se expone. La contraseña **nunca** se escribe en archivos del repo: entra sólo por `--env-file` en el servidor. Ver `13`.
**Contexto**: la consigna dice que la cátedra provee la base y la dirección ("Si la cátedra entrega otra dirección, se usa esa"; `host.docker.internal` como ejemplo). **Riesgo**: ver `10` (P-04). **Resuelto parcialmente:** puerto público 8000 (8001 si está ocupado); si crear `libreria` en ese PostgreSQL falla, se crea un Postgres nuevo (DD-27).

### DD-12 — `knowledge-base/` en la raíz del repo
**Decisión**: nunca dentro de `parcial/` ni `despliegue/`; no se mezcla con `docs/` (fuentes).

## Supuestos inferidos

### SU-01 — (RESUELTO, ver DD-15) `otorgada_por` es FK a `usuario.id`
**Origen**: columna "(nulo)" en la tabla de dominio sin tipo. **Riesgo si es falso**: migración inconsistente con lo que corrige el profesor. **Validar**: preguntar o dejar FK nula con índice.

### SU-02 — (RESUELTO, ver DD-13) `movimiento_stock.usuario_id` es obligatorio (no nulo) salvo en los movimientos del seed
**Origen**: la consigna sólo marca `venta_id` como nulo. **Riesgo**: el seed y el "Stock inicial" necesitan un usuario (¿admin?). **Validar**: ver `10`.

### SU-03 — El detalle de venta carga cliente, renglones y libros con `selectinload`/`joinedload` para número fijo de consultas
**Origen**: Ej. 8 y C-15. **Riesgo**: `joinedload` con colecciones puede multiplicar filas; con `selectinload` son 3–4 consultas fijas. **Validar**: contar consultas con `SQL_ECHO=true`.

### SU-04 — La migración 3 autogenerada requerirá corrección manual
**Origen**: cambio de UNIQUE a índice parcial en `libro.isbn` y nombres de constraints. **Riesgo si es falso**: ninguno. **Validar**: `alembic check` / leer el diff antes de aplicar; comentar la corrección en la migración.

### SU-05 — `main.py` vive como `app/main.py`
**Origen**: el comando `uvicorn app.main:app` del Dockerfile (D-02 / Ej. 9) y el entry point del TP. **Riesgo**: la tabla del PDF dice `main.py` sin carpeta. **Validar**: copiar la ubicación del TP. **Confirmado por el profesor (DD-21).**

### SU-06 — El ejemplo `Authorization: Bearer` de C-03 verifica que NO se acepta
**Origen**: "sin cookie o con `Authorization: Bearer`, 401". **Validar**: caso `.http` con Bearer válido en cabecera debe dar 401.

### SU-07 — (RESUELTO, págs. 16–18) Rutas con `GET`/`POST` de `…/{id}/libros` interpretadas desde una tabla mal maquetada
**Origen**: la extracción del PDF desordena columnas (págs. 16–18). **Validar**: contrastar con el PDF original (ver IN-02).

### SU-08 — El "mismo correo desde la misma dirección" usa `request.client.host`
**Origen**: RN-07. **Riesgo**: detrás de un proxy (EasyPanel/Traefik) la IP puede ser la del proxy. Aplica al TP desplegado sólo si tuviera login (no lo tiene). **Validar**: en local es 127.0.0.1.

## Decisiones aceptadas tras las respuestas de la consigna

> Resuelven SU-01 (-> DD-15), SU-02 (-> DD-13) y SU-07 (IN-02 resuelta). SU-05 quedó confirmado por el profesor (DD-21).

### DD-13 — `movimiento_stock.usuario_id` NOT NULL (P-01)
Los movimientos "Stock inicial" del seed los hace `admin@example.com`. Venta: el usuario que la registra. Alta y reposición: el admin autenticado.

### DD-14 — `motivo` es texto libre (P-02)
Valores usados: "Stock inicial", "Reposición", "Venta". Sin CHECK.

### DD-15 — `otorgada_por` FK nullable a `usuario.id` (P-07)
En el seed es NULL (actor SISTEMA). Con índice (toda FK lleva índice).

### DD-16 — Variables de entorno (P-03)
`JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO`, `COOKIE_SECURE`, `DB_POOL_SIZE`, `SQL_ECHO` y `POSTGRES_USER/PASSWORD/DB/HOST/PORT`. La URL de la base se arma con `@computed_field` (driver `postgresql+asyncpg`). **Sin default** para `POSTGRES_PASSWORD` ni `JWT_SECRET`.

### DD-17 — Reponer un libro dado de baja es 409 (P-08, RN-13)

### DD-18 — Sesión en `/auth` (P-09)
`POST /auth/logout` sin sesión responde 200; `GET /auth/yo` y `POST /auth/cambiar-password` requieren sesión.

### DD-19 — El intento rechazado por 429 no se registra (P-14)
Sólo los intentos que llegan a verificarse (éxito o fallo) escriben en `intento_acceso`.

### DD-20 — `HEALTHCHECK` (P-16)
`--interval=30s --retries=3 --start-period=20s`, sobre `http://127.0.0.1:8000/health/ready`.

### DD-21 — Ubicación de `main.py` (IN-03, resuelta)
`app/main.py` (`uvicorn app.main:app`); `seed.py` en la raíz de `parcial/`. **Confirmado por el profesor.**

### DD-22 — `env.example` en `despliegue/` (IN-05)
Se agrega `env.example`; el `.env.example` del TP no se toca.

### DD-23 — `SQL_ECHO` vs `DEBUG` (IN-06)
El TP lee `DEBUG`. En `despliegue/` no se cambia código: se anota en `DEPLOY.md`. En `parcial/`, `Settings` lee `SQL_ECHO`.

### DD-24 — No existe `PATCH /generos` (P-10); mensaje de paginación «La página 4 no existe: hay 3» (P-15)

### DD-25 — El TP ya tiene `BackgroundTasks` en `ventas/tasks.py` (P-18)
Alcanza para D-08; en el parcial se conserva y se hace visible en consola (logger configurado).

### DD-26 — Dataset del seed: precios y datos ficticios (P-06)
Rayuela 25000.00, Antología 30000.00, Ficciones 22000.00, Respiración artificial 27000.00 (del TP); **Bestiario 18000.00, valor ficticio** (la consigna no lo da y ningún caso lo usa; se quitó la marca `PROVISORIO (P-06)`). Venta 1 = 1 Rayuela + 2 Ficciones = 69000.00. Todo lo que el seed necesita y la consigna no fija es **ficticio**: 3 editoriales (Letras del Río, Ediciones del Plata Sur, Editorial Sudamérica Austral), 3 géneros (Novela, Cuento, Antología), 6 autores (Cortázar, Borges, Ocampo, Bioy Casares, Piglia, Saer) e ISBN `978-950-00-0001-1`..`0005-9`. Dataset completo en `04`.

### DD-27 — Despliegue: puerto 8000 y fallback de la base (P-04)
Puerto público **8000**; si está en uso, **8001**. Base: PostgreSQL de la calculadora con la base nueva `libreria`; **si falla, se crea un Postgres nuevo** y se documenta en `13`, `DEPLOY.md` y CH-03. El nombre de la red de EasyPanel sigue pendiente (se resuelve en CH-03).

### DD-28 — Material de cátedra en `docs/catedra/` (P-13)
Cap1 a cap6 en Markdown; las «secciones X.Y» de la consigna refieren a esos archivos. Regla: Grep del encabezado y leer la sección puntual, **nunca el archivo entero**.

### DD-29 — `.http`: los del TP se borran de `parcial/test/` y los nuevos se llaman `C-xx_tema.http`
`parcial/test/C-01.http`..`C-08.http` (del TP) se **borran** (siguen intactos en `despliegue/test/`); lo hace CH-02. Los del parcial: `C-xx_tema.http` (p. ej. `C-05_limite_intentos.http`); verificaciones auxiliares de un change: `CH-NN_tema.http`. Si hay `.http` de los casos D, `D-xx_tema.http` (la evidencia D vive en `despliegue/evidencia/`).

### DD-30 — `cambiar-password` con contraseña actual incorrecta: 401
Mismo criterio que el login (credencial incorrecta = 401). 422 queda para cuerpos que rompen el contrato (campo faltante o de más, más de 72 bytes).

### DD-31 — El seed vacía con `TRUNCATE ... RESTART IDENTITY CASCADE`
Los casos C usan ids fijos (libro 1, venta 1, cliente 3): sin `RESTART IDENTITY` los ids seguirían subiendo entre corridas. `CASCADE` según las FK. Un `DELETE` lo frenaría el disparador de `movimiento_stock`.

### DD-32 — CH-06 depende de CH-10 (confirmado)
`movimiento_stock.usuario_id` es NOT NULL (DD-13): alta y reposición necesitan el usuario autenticado.
