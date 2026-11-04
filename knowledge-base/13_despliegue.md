# Despliegue (E9 y E10) — TP de los capítulos 1 a 4 en el VPS

> Se despliega el TP **tal como se entregó** (carpeta `despliegue/`). **No lleva ninguna** de las modificaciones del parcial (usuarios, roles, UoW, movimientos, etc.). Sólo se le agregan `Dockerfile`, `.dockerignore` (ya existe), `env.example`, `DEPLOY.md` y `evidencia/`. Su lógica no se toca. Si el TP no arranca en el contenedor por un defecto propio (ej. una ruta de salud que no responde como pedía su consigna), se corrige y **se anota en `DEPLOY.md`**.
> No se usa Docker Compose: la base no forma parte del paquete porque el servidor ya tiene PostgreSQL.

## Infraestructura disponible (VPS)

| Dato | Valor |
|---|---|
| PostgreSQL | **PostgreSQL 17** ya corriendo dentro de **EasyPanel** (Docker en modo Swarm) |
| Proyecto / servicio EasyPanel | proyecto `calculadora`, servicio `db` |
| Host interno | `calculadora_db` |
| Puerto | `5432` (**NO expuesto** hacia afuera) |
| Rol propio | `libreria` (`LOGIN`, contraseña alfanumérica; **no** se usa el usuario `calculadora`) |
| Contraseña | **NUNCA en ningún archivo.** Entra sólo por `--env-file /root/libreria.env` en el servidor (archivo fuera del repo y de la imagen) |
| Base de la librería | **Nueva**, llamada `libreria` (`OWNER libreria`), en ese mismo servidor |
| Conexión | El contenedor se conecta por la red overlay attachable `--network easypanel-calculadora`; el 5432 no se publica |

La consigna dice que la cátedra provee "los datos de acceso y la base" y que, si la dirección es otra que `host.docker.internal`, "se usa esa". **Resuelto en CH-03 (P-04 / IN-08 / DD-27):** con `docker run` común el contenedor queda en `bridge` y no resuelve `calculadora_db`; se lo une a la red overlay de EasyPanel con `--network easypanel-calculadora` (`Attachable: true`). **Puerto público: 8000** (`-p 8000:8000`, URL `http://179.199.141.99:8000`). **Fallback real de la base (DD-27):** si fallara la conexión al PostgreSQL existente o a la red overlay de Swarm, se levanta un contenedor PostgreSQL propio con `docker run` en una red `bridge` dedicada (`libreria-net`, independiente de Swarm/EasyPanel), tal como queda documentado en `DEPLOY.md`.

## Ejercicio 9 — La imagen (11 pts)

Requisitos del `Dockerfile` (cada uno tiene su razón):

| Requisito | Razón |
|---|---|
| Parte de **`python:3.12-alpine`** (74,7 MB medida con Docker 29.2 el 2/11/2026; `python:3.12-slim` = 180 MB **no cumple** el límite de **100 MB**) | El VPS descarga y guarda la imagen; cada MB se paga en disco y tiempo de descarga; cada paquete del sistema es superficie de ataque. El límite es de la imagen **base**; la del proyecto es bastante más grande, y es lo esperado |
| Sin compilador | Las dependencias del TP (asyncpg, pydantic-core, etc.) se instalan en alpine **sin compilar** |
| Copia e instala `requirements.txt` **antes** de copiar el código, con `--no-cache-dir` | Mientras las dependencias no cambien esa capa sale de la caché |
| La app **no corre como root**: se crea un usuario sin privilegios y se activa con `USER` | Si vulneran la app, no son dueños del contenedor |
| **Sin secretos**: `.dockerignore` excluye `.env`, `.venv`, `.git` y `__pycache__`; ni la dirección de la base ni su contraseña aparecen en el Dockerfile (entran como variables al correr) | Lo que se hornea en una capa queda para siempre aunque otra capa lo borre |
| Al arrancar: `alembic upgrade head` y luego `uvicorn app.main:app` escuchando en **`0.0.0.0`** | Dentro de un contenedor `127.0.0.1` sólo se alcanza desde el propio contenedor. Si la base no responde, Alembic falla y el contenedor termina con error (lo que se quiere) |
| **`HEALTHCHECK`** sobre `GET /health/ready` con `--interval=30s --retries=3 --start-period=20s` (P-16; el start-period da tiempo a las migraciones) | Sin Compose, la imagen dice cuándo está sana; `docker ps` lo muestra |

Trampas documentadas por la consigna:
- **La base no está en `localhost`**: dentro de un contenedor, `localhost` es el propio contenedor ("Connection refused" aunque PostgreSQL ande). Si la base está en el servidor: `host.docker.internal` + `--add-host=host.docker.internal:host-gateway`; si la cátedra da otra dirección, usar esa (acá: `calculadora_db` por red interna).
- **El HEALTHCHECK y `localhost`**: en Alpine no hay `curl`; `wget` sí, pero resuelve `localhost` primero a `::1` (IPv6) y uvicorn con `--host 0.0.0.0` escucha sólo IPv4 → el contenedor queda `unhealthy`. **Usar `127.0.0.1`**: `docker exec libreria wget -qO- http://127.0.0.1:8000/health/live`.

### Forma del comando de ejecución

```
docker run -d --name libreria --network easypanel-calculadora -p 8000:8000 \
   --restart unless-stopped --env-file /root/libreria.env libreria
```
- `-p <puerto>:8000`: publica sólo la aplicación, en el puerto que asigna la cátedra.
- `--restart unless-stopped`: Docker vuelve a levantarlo si termina (reinicio del servidor, base todavía no lista).
- `--env-file`: archivo en el servidor, fuera del repo y la imagen, con **`DATABASE_URL`** (driver `postgresql+asyncpg`, host/usuario/contraseña/base que provee la cátedra; acá `.../libreria` en `calculadora_db`) y **`SQL_ECHO=false`**.

`env.example` de `despliegue/` (nuevo, sin valores reales; el `.env.example` del TP queda como está, IN-05): forma de `DATABASE_URL`, p. ej. `postgresql+asyncpg://<usuario>:<contraseña>@<host>:5432/<base>`, y `SQL_ECHO=false`.

> **Nota para `DEPLOY.md` (IN-06):** el TP lee `DEBUG`, no `SQL_ECHO`; por eso `SQL_ECHO=false` del `--env-file` no tiene efecto (es inofensivo). No se toca el código del TP. En el `parcial/`, `Settings` sí lee `SQL_ECHO`.
> **D-08 (P-18):** el TP ya trae `BackgroundTasks` en `ventas/tasks.py`; sólo se verifica que el aviso aparezca en `docker logs`.

## Ejercicio 10 — Despliegue en el VPS (7 pts)

- Se despliega con los datos de acceso y la base que provee la cátedra. El grupo construye la imagen **en el servidor o en otro lado y la lleva**, y la corre con `docker run`; **elige y documenta**.
- Queda accesible desde afuera en la URL declarada en `DEPLOY.md`.
- Una vez arriba, la base se carga ejecutando **dentro del contenedor** el comando de datos iniciales del README del TP: `docker exec libreria python -m scripts.seed` (según `README.md` del TP; el seed del TP rechaza una base con registros).
- Debe **seguir en línea hasta que se publiquen las notas** (la corrección lo prueba).

### `DEPLOY.md` debe incluir

1. La **URL pública**.
2. El **día y la hora** del despliegue.
3. Los comandos **`docker build` y `docker run` completos**, con el **nombre** del archivo de variables y **sin su contenido**.
4. **Cualquier cambio** que se le haya hecho al TP para que corra en el contenedor.
5. **Cómo se actualiza**: se construye la imagen de nuevo, se elimina el contenedor (`docker rm -f libreria`) y se lo vuelve a correr. Los datos no se pierden (viven en la base del servidor, no en el contenedor).

### Evidencia (`despliegue/evidencia/`)

Salida de cada caso **D-01..D-08** (ver `11`): `docker images` (base < 100 MB), `docker build`/`run`/`ps` (healthy) y `logs` (migraciones), requests desde afuera (200 / 200 / 201), `rm -f` + re-run (healthy, datos siguen, migraciones no se repiten), imagen sin `DATABASE_URL` (termina con error), contenido de la imagen sin `.env` ni secretos, `id` no root, aviso del comprobante en `docker logs` luego de la respuesta.

## Seguridad del despliegue

- Contraseña de la base: sólo en el archivo de `--env-file` del servidor; jamás en `env.example`, Dockerfile, DEPLOY.md, repo, imagen ni zip.
- 5432 no expuesto; sólo el puerto de la aplicación se publica.
- Proceso no root; sin secretos en capas; `.dockerignore` correcto.
