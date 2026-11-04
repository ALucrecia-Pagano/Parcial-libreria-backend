# Proposal — CH-03 `despliegue-docker-vps`

> **Governance: ALTO** (credenciales, servidor VPS compartido con un sistema en producción, red overlay de Docker Swarm/EasyPanel; la contraseña de la base **nunca** se escribe en ningún archivo del repositorio ni entra en la imagen). Antes de escribir `despliegue/Dockerfile`, `despliegue/env.example` y `despliegue/DEPLOY.md` durante `/opsx:apply`, el agente muestra el contenido propuesto y espera confirmación de la integrante. Todos los comandos en el VPS los ejecuta la integrante (`[AMANDA-VPS]`) a mano por SSH.

## Why

Los Ejercicios 9 y 10 del parcial exigen empaquetar el Trabajo Práctico de los capítulos 1 a 4 (carpeta `despliegue/`, sin tocar su lógica) en una imagen Docker liviana y segura, desplegarla en el VPS provisto conectándola al PostgreSQL existente y dejar documentado el procedimiento en `despliegue/DEPLOY.md` junto con la evidencia verificable de los casos **D-01 a D-08** en `despliegue/evidencia/`. Este change es independiente del camino crítico de `parcial/` (`CH-01..CH-15`) y permite cerrar la parte de infraestructura y despliegue sin bloquear ni pisar el desarrollo de los capítulos 5 y 6.

## What Changes

- **`despliegue/Dockerfile`** (nuevo):
  - Parte de `python:3.12-alpine` (imagen base por debajo del límite de 100 MB; sin instalar compilador).
  - Define `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1` y `WORKDIR /app`.
  - Crea un usuario y grupo del sistema sin privilegios (`appuser`).
  - Copia e instala `requirements.txt` con `pip install --no-cache-dir -r requirements.txt` **antes** de copiar el código para aprovechar la caché de capas.
  - Realiza `COPY` explícito únicamente de lo necesario para migrar, sembrar y servir (`alembic.ini`, `app/`, `migrations/`, `scripts/`), evitando que archivos del repositorio como `.env.example`, `env.example` o `README.md` aparezcan dentro de `/app` al inspeccionar la imagen en D-06.
  - Activa `USER appuser` y declara `EXPOSE 8000`.
  - Configura `HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3` consultando `http://127.0.0.1:8000/health/ready` con `wget` (nunca `localhost`, que en Alpine intenta primero `::1` IPv6 mientras uvicorn escucha en IPv4 `0.0.0.0`).
  - Define el arranque con `CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]` (sin script `.sh` auxiliar, evitando problemas de permisos de ejecución o finales de línea CRLF).
- **`despliegue/.dockerignore`** (revisión sin cambios): ya excluye `.env`, `.venv/`, `.git`, `__pycache__/`, `test/`, `docs/`, `evidencia/`, `DEPLOY.md` y `*.pdf`. Se conserva intacto.
- **`despliegue/env.example`** (nuevo, sin tocar `despliegue/.env.example` por DD-22 / IN-05): documenta la forma de las variables que recibe `--env-file` en el servidor (`DATABASE_URL=postgresql+asyncpg://<usuario>:<password>@<host>:5432/<base>` y `SQL_ECHO=false`), sin credenciales reales.
- **`despliegue/DEPLOY.md`** (nuevo): documenta la URL pública (`http://179.199.141.99:8000`), día y hora del despliegue (`<FECHA_HORA>` hasta ejecutarlo), placeholder `<NOMBRE>` del grupo (P-05), arquitectura de conexión a `calculadora_db` (PostgreSQL 17 en la red overlay attachable `easypanel-calculadora` con rol propio `libreria` y base `libreria`), forma del archivo `/root/libreria.env` (solo nombres y placeholders, jamás su contenido real), comandos completos de clonado HTTPS, `docker build`, `docker run` y carga inicial (`docker exec libreria python -m scripts.seed`), cambios hechos al TP (ninguno, salvo que surja un defecto bloqueante durante el apply), procedimiento de actualización (`git pull` + `docker build` + `docker rm -f libreria` + `docker run`), recuperación manual tras un reinicio del VPS de Lucas (sin reiniciar el servidor sin coordinarlo porque la calculadora está en producción), fallback con un contenedor PostgreSQL propio en red bridge (`libreria-net`) y notas sobre `DEBUG` vs `SQL_ECHO` (IN-06 / DD-23) y `BackgroundTasks` en `ventas/tasks.py` (P-18 / DD-25).
- **`despliegue/evidencia/`** (nuevo directorio): archivos `.txt` individuales con las salidas reales (y saneadas, sin secretos ni IP personal de la integrante) de los casos **D-01 a D-08**, ejecutados en el orden que preserva los logs de la venta antes de recrear el contenedor (**D-08 antes que D-04**).
- **Sincronización documental post-CH-02** (última tarea, marcada para ejecutarse **después de que CH-02 esté commiteado**): actualizar `knowledge-base/09_decisiones_y_supuestos.md` (DD-11, DD-27), `knowledge-base/10_preguntas_abiertas.md` (IN-08, P-04), `knowledge-base/13_despliegue.md` y la ficha de CH-03 en `CHANGES.md` para reflejar los datos confirmados en el VPS (red `easypanel-calculadora` attachable, PostgreSQL 17, rol propio `libreria` en vez de `calculadora`, puerto `8000` y fallback de Postgres con `docker run` en red bridge propia en lugar de otro servicio de EasyPanel).

**No entra**: cambios a la lógica del TP en `despliegue/app/`, `despliegue/migrations/` ni `despliegue/scripts/`; `docker-compose.yml`; cambios en `parcial/`; pruebas con pytest o scripts `.py`.

## Capabilities

### New Capabilities
- `despliegue-contenedor-vps`: empaquetado Docker del TP (caps. 1–4) bajo restricciones de imagen base liviana, usuario sin privilegios, ausencia de secretos horneados, migración al arranque y chequeo de salud, junto con su puesta en producción en el VPS, documentación operativa en `DEPLOY.md` y evidencia verificable D-01..D-08.

### Modified Capabilities
- (ninguna: las specs actuales en `openspec/specs/` cubren únicamente `parcial/`)

## Impact

- **Archivos nuevos en `despliegue/`**: `despliegue/Dockerfile`, `despliegue/env.example`, `despliegue/DEPLOY.md`, `despliegue/evidencia/D-01_imagenes.txt` .. `despliegue/evidencia/D-08_aviso_comprobante.txt`.
- **Archivos sin cambios en `despliegue/`**: `despliegue/.dockerignore`, `despliegue/.env.example`, `despliegue/requirements.txt`, `despliegue/alembic.ini`, `despliegue/app/**`, `despliegue/migrations/**`, `despliegue/scripts/**`, `despliegue/test/**`.
- **Archivos de documentación en raíz** (solo al final del apply y **después de que CH-02 esté commiteado**): `knowledge-base/09_decisiones_y_supuestos.md`, `knowledge-base/10_preguntas_abiertas.md`, `knowledge-base/13_despliegue.md`, `CHANGES.md`.
- **Infraestructura (VPS `179.199.141.99`)**: uso de la red existente `easypanel-calculadora` (overlay attachable), conexión al servicio interno `calculadora_db:5432` (PostgreSQL 17) con rol y base `libreria` ya creados, archivo `/root/libreria.env` administrado exclusivamente por Amanda en el servidor (`chmod 600`), y publicación del puerto TCP `8000` hacia el exterior (`-p 8000:8000`).

