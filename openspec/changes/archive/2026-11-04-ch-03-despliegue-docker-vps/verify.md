# Verify — CH-03 `despliegue-docker-vps`

Evidencia real corrida en el VPS (`http://179.199.141.99:8000`, Docker en modo Swarm con red overlay attachable `easypanel-calculadora`, servicio `calculadora_db:5432` con PostgreSQL 17, rol propio `libreria` y base `libreria`) y desde afuera del servidor el **04/11/2026 a las 10:37 (UTC-3)**. Sin secretos ni direcciones IP personales en este archivo ni en `despliegue/evidencia/`.

---

## 1. Tabla de casos D (D-01 a D-08): esperado vs. obtenido

| Caso | Archivo en `despliegue/evidencia/` | Esperado (consigna) | Obtenido (con línea del archivo de evidencia) | Estado |
|---|---|---|---|---|
| **D-01** | `D-01_imagenes.txt` | `python:3.12-alpine` por debajo de los 100 MB, y el `Dockerfile` parte de ella; imagen del proyecto construida. | `L1`: `FROM python:3.12-alpine`. `L3`: `python:3.12-alpine` (`e6dae589c1c0`) con `DISK USAGE 74.7MB` (`CONTENT SIZE 18.7MB`), `< 100 MB`. `L5`: `libreria:latest` (`61b3b4a5e3ae`, `255MB`). | ✅ Cumple |
| **D-02** | `D-02_build.txt` | Servidor limpio: `docker build` y `docker run`; después `docker ps` con el contenedor en estado `healthy`; en `docker logs`, las migraciones del TP aplicadas al arrancar. | `L1–270`: `docker build` completo desde `python:3.12-alpine` (`L18`), usuario `appuser` (`L25`), `pip install --no-cache-dir` antes del código (`L28–245`), `COPY` explícito (`L247–257`), etiquetado `libreria:latest` (`L267`). `L271–272`: `docker ps` muestra contenedor `46af053c1882` con `STATUS Up About a minute (healthy)` y `0.0.0.0:8000->8000/tcp`. `L276–277`: `Running upgrade -> 95dd46a75b66, esquema inicial sin genero` y `Running upgrade 95dd46a75b66 -> 0f5ab569096b, Agrega tabla genero y relacion con libro`. `L281–284`: `Uvicorn running on http://0.0.0.0:8000` y `GET /health/ready HTTP/1.1" 200 OK`. | ✅ Cumple |
| **D-03** | `D-03_desde_afuera.txt` | Desde afuera del VPS, en la URL pública: `GET /health/ready` → 200; `GET /libros/` con los datos iniciales cargados → 200 con la lista de libros; `POST /ventas/` con el cuerpo de ejemplo del TP → 201 con precios copiados y total calculado. | `L4–10`: `GET /health/ready` → `HTTP/1.1 200 OK` (`L4`) y `{"estado":"lista"}` (`L10`). `L15–21`: `GET /libros/` → `HTTP/1.1 200 OK` (`L15`) y lista JSON con los 2 libros del seed (`id:1` Rayuela `25000.00` stock 10; `id:2` Los que aman, odian `21000.00` stock 4) (`L21`). `L22–29`: `POST /ventas/` → `HTTP/1.1 201 Created` (`L23`) y venta `id:2` con `"total":"71000.00"` y renglones con `"precio_unitario":"25000.00"` (`subtotal: "50000.00"`) y `"precio_unitario":"21000.00"` (`subtotal: "21000.00"`) (`L29`). | ✅ Cumple |
| **D-04** | `D-04_recrear_contenedor.txt` | `docker rm -f libreria` y el mismo `docker run` otra vez: vuelve a estar `healthy`, los datos siguen —la base no vive en el contenedor— y las migraciones no se repiten. | `L1–2`: nuevo contenedor `c2dda28f4378` (distinto de `46af053c1882`) con `STATUS Up 40 seconds (healthy)`. `L4–9`: `docker logs` muestra `Context impl PostgresqlImpl.` (`L4`), `Will assume transactional DDL.` (`L5`) y `Started server process [1]` (`L6`) **sin** líneas `Running upgrade` (las migraciones no se repiten). `L13–14`: `GET /ventas/2` devuelve intacta la venta `id:2` (`"total":"71000.00"`) creada antes de borrar el contenedor anterior. | ✅ Cumple |
| **D-05** | `D-05_sin_database_url.txt` | Correr la imagen sin `DATABASE_URL`: el contenedor no queda sirviendo y termina con un error, porque el TP no trae ninguna dirección de base por defecto. | `L1–29`: traza en `/app/app/core/config.py`, línea 18, que termina en `RuntimeError: Falta configurar DATABASE_URL en el entorno o en .env (ver .env.example)` (`L29`). `L30`: `exit=1`. | ✅ Cumple |
| **D-06** | `D-06_contenido_imagen.txt` | Contenido de la imagen: no hay `.env` (`docker run --rm --entrypoint ls <imagen> -a /app`) y `docker run --rm --entrypoint env <imagen>` no muestra `DATABASE_URL` ni ninguna contraseña. | `L1–8`: `ls -a /app` lista únicamente `.`, `..`, `alembic.ini`, `app`, `migrations`, `requirements.txt`, `scripts` (sin `.env`, `.env.example` ni `env.example`). `L10–19`: `env` de la imagen muestra solo `PATH`, `HOSTNAME`, `LANG`, `GPG_KEY`, `PYTHON_VERSION`, `PYTHON_SHA256`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `HOME=/home/appuser` (sin `DATABASE_URL` ni secretos). | ✅ Cumple |
| **D-07** | `D-07_usuario.txt` | Usuario del proceso: `docker exec libreria id` no es `root`. | `L1`: `uid=100(appuser) gid=101(appgroup) groups=101(appgroup)` (`uid` y `gid` distintos de `0`/`root`). | ✅ Cumple |
| **D-08** | `D-08_comprobante.txt` | La venta registrada en el caso D-03: el aviso del comprobante aparece en `docker logs libreria` después de la línea de la respuesta. | `L1`: `2026-11-04T13:40:46.633895289Z INFO: <IP_CLIENTE> - "POST /ventas/ HTTP/1.1" 201 Created`. `L2`: `2026-11-04T13:40:47.134723999Z INFO: Comprobante de venta 2 enviado a mismo_email@example.com (simulado)` (~0,5 s después de la respuesta `201 Created`). | ✅ Cumple |

---

## 2. Tabla de tareas del change (`1.1` a `6.1`)

| Tarea | Responsable | Verificación | Resultado |
|---|---|---|---|
| `1.1` | `[AGENTE]` | Lectura de `despliegue/.dockerignore` | Excluye `.env`, `.venv/`, `.git`, `__pycache__/`, `*.pyc`, `test/`, `docs/`, `evidencia/`, `DEPLOY.md`, `*.pdf`; sin cambios. |
| `1.2` | `[AGENTE]` | Creación de `despliegue/Dockerfile` | Basado en `python:3.12-alpine`, `appuser` no-root, caché de `requirements.txt`, `COPY` explícito, `HEALTHCHECK` en `127.0.0.1:8000/health/ready`, `CMD` con `alembic upgrade head && exec uvicorn`. |
| `1.3` | `[AGENTE]` | Creación de `despliegue/env.example` | Plantilla con placeholders (`DATABASE_URL` y `SQL_ECHO=false`); `despliegue/.env.example` intacto. |
| `1.4` | `[AGENTE]` | Creación de `despliegue/DEPLOY.md` | Documentación completa de los Ejercicios 9 y 10, completada por Amanda con fecha/hora real (`04/11/2026, 10:37 UTC-3`), URL real del `git clone` y justificación de build en el VPS. |
| `2.1–4.4` | `[AMANDA-VPS]` | Ejecución en VPS (`179.199.141.99`) y desde consola local | Contenedor en línea en `http://179.199.141.99:8000` y 8 archivos `.txt` generados en `despliegue/evidencia/`. |
| `5.1–5.2` | `[AGENTE]` | Revisión de los 8 archivos de `despliegue/evidencia/`, confidencialidad y `git status` | Los 8 casos cumplen; 0 contraseñas, 0 salidas de `docker inspect`/`docker exec ... env`, IP personal anonimizada como `<IP_CLIENTE>`; lógica de `despliegue/` intacta. |
| `6.1` | `[AGENTE]` | Actualización de DD-27, IN-08 y P-04 en KB (`09`, `10`, `13`) y `CHANGES.md` (con CH-02 ya commiteado en `624f930`) | Red `easypanel-calculadora` (attachable), PostgreSQL 17, rol/base `libreria`, puerto `8000` y fallback real con Postgres en red bridge propia (`libreria-net`) documentados; `P-04` e `IN-08` marcadas como **Resuelta**. |

---

## 3. Cambios manuales de la integrante registrados

1. **`despliegue/DEPLOY.md`**: completado con la fecha y hora reales del despliegue (`04/11/2026, 10:37 (hora de Argentina, UTC-3)`), la URL real del `git clone` (`https://github.com/ALucrecia-Pagano/Parcial-libreria-backend.git`) y el motivo de construir la imagen directamente en el VPS.
2. **`README.md` (raíz del repositorio)**: creado con el enlace directo al backend desplegado en el VPS (`http://179.199.141.99:8000`, `/health/ready` y `/docs`), listado de integrantes y estructura del repositorio.

---

## 4. Nota sobre los dos commits de `CH-03`

Por el flujo de construcción en el VPS mediante `git clone` por HTTPS, **`CH-03` se commitea en dos partes**:

1. **Primer commit (previo al `git clone` en el VPS)**: incluyó `despliegue/Dockerfile`, `despliegue/env.example` y `despliegue/DEPLOY.md` (más los artefactos iniciales del change), necesarios en GitHub para que el VPS pudiera clonar el repositorio y construir la imagen en la tarea `2.2`.
2. **Segundo commit (al cierre del change)**: incluye los 8 archivos de evidencia en `despliegue/evidencia/`, la fecha/hora y URL de clonado en `despliegue/DEPLOY.md`, el `README.md` de la raíz, la actualización de DD-27 / P-04 / IN-08 en `knowledge-base/` y `CHANGES.md`, este `verify.md` y el archive del change.

