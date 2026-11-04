# Design — CH-03 `despliegue-docker-vps`

> **Governance ALTO.** Durante `/opsx:apply`, antes de escribir `despliegue/Dockerfile`, `despliegue/env.example` y `despliegue/DEPLOY.md`, el agente presenta el contenido y aguarda confirmación de la integrante. Toda interacción con el VPS (`179.199.141.99`) la ejecuta la integrante a mano por SSH en las tareas marcadas `[AMANDA-VPS]`.

## UI Mockups

Decision: no (no UI)

## Context

Motivación: ver `proposal.md` § Why. Requisitos: ver `specs/despliegue-contenedor-vps/spec.md`.

### Estado observado en `despliegue/` (lectura del 04/11/2026)
- `despliegue/requirements.txt`: `fastapi[standard]>=0.111`, `sqlmodel>=0.0.24`, `SQLAlchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `alembic>=1.13`, `python-dotenv>=1.0`, `uvicorn`. Todas disponen de wheels precompilados (`musllinux`) para `python:3.12-alpine`, por lo que no requieren compilador (`gcc`, `musl-dev`).
- `despliegue/app/core/config.py`: lee `DATABASE_URL` con `os.getenv("DATABASE_URL", "")` y lanza `RuntimeError("Falta configurar DATABASE_URL...")` en tiempo de importación si está vacía (satisface nativamente D-05). Lee `DEBUG` y no `SQL_ECHO` (IN-06 / DD-23).
- `despliegue/migrations/env.py`: en la línea 31 ejecuta `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)`. `ConfigParser` interpreta `%` como interpolación, por lo que la contraseña de la base debe ser alfanumérica (o únicamente con `-_.~`) sin caracteres que requieran percent-encoding.
- `despliegue/app/modules/health/router.py`: expone `GET /health/live` y `GET /health/ready` (`SELECT 1`, devuelve 200 `{"estado": "lista"}` o 503).
- `despliegue/app/modules/ventas/tasks.py`: implementa `avisar_comprobante` con `BackgroundTasks` registrando en `logging.getLogger("uvicorn.error")` el mensaje `Comprobante de venta %s enviado a %s (simulado)` tras `asyncio.sleep(0.5)` (satisface nativamente D-08).
- `despliegue/scripts/seed.py`: verifica que las 6 tablas estén vacías (si hay filas lanza `RuntimeError`) y carga 1 editorial, 1 género, 3 autores, 1 cliente (`id=1`), 2 libros (`id=1` Rayuela stock 10 a `25000.00`, `id=2` Los que aman, odian stock 4 a `21000.00`) y 1 venta (`id=1`, total `71000.00`).
- `despliegue/.dockerignore`: ya existe y excluye `.env`, `.venv/`, `.git`, `__pycache__/`, `test/`, `docs/`, `evidencia/`, `DEPLOY.md` y `*.pdf`. No excluye `.env.example` ni `env.example`.

### Datos confirmados en el VPS (`179.199.141.99`, relevamiento del 04/11/2026)
- Docker corre en modo **Swarm** (administrado por EasyPanel).
- La red `easypanel-calculadora` es de tipo `overlay` con `Attachable: true`. Una prueba con un contenedor unido mediante `--network easypanel-calculadora` resolvió `calculadora_db` (`10.0.2.3`) y verificó que el puerto `5432` responde `"open"`. El motor es **PostgreSQL 17**.
- Ya fueron creados en ese PostgreSQL el rol `libreria` (`LOGIN`, con contraseña alfanumérica) y la base `libreria` con `OWNER libreria`. **No** se utiliza el usuario `calculadora`.
- Los puertos `8000` y `8001` del host están libres; se utiliza el puerto **`8000`**.
- El VPS pertenece a Lucas y el proyecto `calculadora` está en producción: **no se reinicia el VPS** sin coordinarlo previamente con él.

## Goals / Non-Goals

**Goals:**
- Construir una imagen Docker reproducible, sin secretos y no-root a partir de `python:3.12-alpine` que ejecute las migraciones del TP al iniciar y exponga la API en el puerto `8000` con `HEALTHCHECK` activo.
- Dejar desplegado el contenedor `libreria` en `http://179.199.141.99:8000`, conectado a `calculadora_db:5432/libreria` por la red `easypanel-calculadora`, con los datos iniciales cargados y toda la evidencia D-01..D-08 recolectada y saneada en `despliegue/evidencia/`.
- Documentar en `despliegue/DEPLOY.md` la operación completa y, al cierre (después de que CH-02 esté commiteado), alinear la KB y `CHANGES.md` con la topología real del VPS.

**Non-Goals:**
- No se modifica ningún archivo de código Python ni migración de `despliegue/`.
- No se utiliza Docker Compose ni se crea otro servicio desde la interfaz de EasyPanel.
- No se toca nada de `parcial/`.

## Decisions

### D1 — Red `--network easypanel-calculadora` y fallback en red bridge propia
- **Decisión**: Conectar el contenedor `libreria` a la red overlay existente con `--network easypanel-calculadora`, resolviendo el host interno `calculadora_db` en el puerto `5432` sin publicar dicho puerto en el host. Documentar como fallback en `DEPLOY.md` el levantamiento de un contenedor `postgres:17-alpine` propio con `docker run` en una red bridge dedicada (`docker network create libreria-net`) y volumen persistente (`libreria-pgdata`).
- **Por qué**: En el VPS ya se verificó que `easypanel-calculadora` tiene `Attachable: true` y permite alcanzar `calculadora_db:5432`. El fallback anterior de DD-27 ("crear otro servicio Postgres en EasyPanel") tenía un hueco: si el problema fuera adjuntar un contenedor standalone a una red overlay de Swarm, otro servicio de EasyPanel quedaría igualmente en una red overlay. Una red `bridge` propia (`libreria-net`) con `docker run` es 100% independiente de Swarm/EasyPanel.
- **Alternativas descartadas**: `host.docker.internal` (el puerto 5432 de `calculadora_db` no está publicado en el host).

### D2 — Clonado por HTTPS y `docker build` directamente en el VPS
- **Decisión**: Clonar el repositorio en el VPS por HTTPS (`/opt/parcial-libreria` o `/root/parcial-libreria`) y construir la imagen `libreria` localmente en el servidor (`docker build -t libreria .` dentro de `despliegue/`), haciendo `docker pull python:3.12-alpine` explícito antes del build.
- **Por qué**: La consigna permite construir en el servidor o llevar la imagen; construir en el VPS tras `docker pull python:3.12-alpine` garantiza que `python:3.12-alpine` aparezca listada explícitamente en `docker images` para la evidencia **D-01** (BuildKit a veces no registra la etiqueta de la imagen base por separado si no se descargó antes) y simplifica las actualizaciones con `git pull` + `docker build`.
- **Alternativas descartadas**: Construir en la máquina local y transferir con `docker save` / `scp` (más lento en cada iteración).

### D3 — `COPY` explícito de artefactos en `despliegue/Dockerfile`
- **Decisión**: En lugar de `COPY . .`, copiar primero `COPY requirements.txt .` para instalar dependencias con `pip install --no-cache-dir -r requirements.txt` y luego ejecutar:
  ```dockerfile
  COPY alembic.ini ./
  COPY app ./app
  COPY migrations ./migrations
  COPY scripts ./scripts
  ```
- **Por qué**: `.dockerignore` no excluye `.env.example`, `env.example`, `README.md` ni `Dockerfile`. Con `COPY . .`, esos archivos aparecerían en `docker run --rm --entrypoint ls libreria -a /app` durante el caso **D-06**, pudiendo generar confusión visual con `.env`. Con `COPY` explícito, `/app` contiene únicamente `.`, `..`, `alembic.ini`, `app`, `migrations`, `requirements.txt` y `scripts`.
- **Alternativas descartadas**: Agregar `.env.example`, `env.example`, `README.md` y `Dockerfile` a `.dockerignore` (innecesario tocar `.dockerignore` cuando `COPY` explícito es más limpio y declarativo).

### D4 — Variables de entorno de Python, usuario sin privilegios, `HEALTHCHECK` con `--timeout=5s` y `CMD` sin script `.sh`
- **Decisión**:
  - Declarar `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1` para que Python no escriba `.pyc` y vuelque inmediatamente los logs (`uvicorn` y `BackgroundTasks`) a stdout/stderr sin buffer.
  - Crear usuario y grupo sin privilegios: `RUN addgroup -S appgroup && adduser -S -G appgroup -H -D appuser` y activar `USER appuser`.
  - Configurar `HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD wget -qO- http://127.0.0.1:8000/health/ready > /dev/null || exit 1` (usando `127.0.0.1` y no `localhost` para evitar que `wget` en Alpine intente IPv6 `::1`).
  - Arrancar con `CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]`.
- **Por qué**: `exec` hace que `uvicorn` reemplace al proceso `sh` como PID 1 y reciba señales `SIGTERM` limpiamente; prescindir de un archivo `entrypoint.sh` evita fallos por finales de línea `CRLF` en Windows o falta de `chmod +x`.

### D5 — Rol propio `libreria` y base `libreria` en `calculadora_db`
- **Decisión**: Conectar con el rol `libreria` (con permiso `LOGIN` y contraseña alfanumérica, dueño de la base `libreria`, ya creados en el PostgreSQL 17 de `calculadora_db`), nunca con el superusuario/usuario `calculadora`. El archivo `/root/libreria.env` en el VPS (`chmod 600`) lo escribe exclusivamente Amanda con:
  ```dotenv
  DATABASE_URL=postgresql+asyncpg://libreria:<PASSWORD_ALFANUMERICA>@calculadora_db:5432/libreria
  SQL_ECHO=false
  ```
- **Por qué**: Aísla los permisos de la librería respecto de la base de datos en producción de la calculadora y evita caracteres especiales que rompan `config.set_main_option` en `migrations/env.py`.

### D6 — Convivencia con `calculadora` en producción y recuperación tras reinicio del VPS
- **Decisión**: No reiniciar nunca el VPS sin coordinarlo con Lucas. Documentar en `DEPLOY.md` que, si bien el contenedor se lanza con `--restart unless-stopped`, en Docker Swarm un contenedor standalone (`docker run`) conectado a una red `overlay` (`attachable=true`) puede fallar al re-adjuntarse automáticamente durante el arranque en frío del daemon si la red overlay aún no terminó de inicializarse, e incluir el comando exacto para volver a levantarlo manualmente (`docker start libreria` o `docker rm -f libreria && docker run ...`).

### D7 — URL pública en puerto `8000`
- **Decisión**: Publicar con `-p 8000:8000` y declarar `http://179.199.141.99:8000` en `DEPLOY.md`.

### D8 — Caso D-03 desde fuera del VPS con `curl -i`
- **Decisión**: Ejecutar las tres peticiones de **D-03** (`GET /health/ready`, `GET /libros/` tras correr `docker exec libreria python -m scripts.seed`, y `POST /ventas/` con el cuerpo de ejemplo `{"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 2, "cantidad": 1}]}`) desde la máquina local de Amanda hacia `http://179.199.141.99:8000` usando `curl -i` para que la evidencia muestre tanto la línea de estado HTTP (`200 OK`, `200 OK`, `201 Created`) como los encabezados y el cuerpo JSON con precios copiados y `"total":"71000.00"`.

### D9 — Orden de recolección de evidencias (`.txt` en `despliegue/evidencia/`, D-08 antes que D-04) y saneamiento
- **Decisión**: Guardar un archivo `.txt` por caso en `despliegue/evidencia/` (`D-01_imagenes.txt` a `D-08_aviso_comprobante.txt`) ejecutándolos en el orden: **D-01 → D-02 → seed → D-03 → D-08 → D-04 → D-05 → D-06 → D-07**.
- **Por qué D-08 antes que D-04**: D-04 ejecuta `docker rm -f libreria`, lo que elimina los registros del contenedor anterior donde quedó impresa la línea `Comprobante de venta 2 enviado a mismo_email@example.com (simulado)` generada por la venta de D-03. Capturar `docker logs libreria` para D-08 inmediatamente después de D-03 preserva la evidencia sin necesidad de repetir ventas (recordando que `libro 2` arranca con `stock=4`).
- **Regla de confidencialidad**: Jamás ejecutar ni guardar `docker inspect libreria` ni `docker exec libreria env` (ambos exponen el `--env-file` con la contraseña real de `DATABASE_URL`). En los logs de acceso de `docker logs libreria` (D-02, D-04, D-08), reemplazar la IP pública personal de la integrante por `<IP_CLIENTE>` antes de guardar los archivos en el repositorio.

### D10 — Sincronización de KB y `CHANGES.md` como última tarea post-CH-02
- **Decisión**: Incluir como última tarea de `tasks.md` (`[AGENTE]`, explícitamente condicionada a que **CH-02 ya esté commiteado** en el árbol de trabajo) la actualización de `knowledge-base/09_decisiones_y_supuestos.md` (DD-11, DD-27), `knowledge-base/10_preguntas_abiertas.md` (IN-08, P-04), `knowledge-base/13_despliegue.md` y la ficha de CH-03 en `CHANGES.md`.
- **Por qué**: Otro agente está aplicando CH-02 en paralelo en esta misma copia de trabajo; tocar archivos compartidos de la raíz antes de que CH-02 se commitee mezclaría cambios en el `git status` de la integrante.

### D11 — Placeholders `<NOMBRE>` y `<FECHA_HORA>`
- **Decisión**: Mantener `<NOMBRE>` en `DEPLOY.md` para el nombre del grupo (P-05 sigue abierta) y completar la fecha y hora exactas del despliegue cuando Amanda ejecute el `docker run` en el VPS.

## Risks / Trade-offs

- **[Exposición accidental de la contraseña de la base en un repo público]** → El archivo `/root/libreria.env` solo existe en el VPS; `D-06` inspecciona la imagen con `docker run --rm --entrypoint env libreria` (sin `--env-file`), y queda prohibido correr o guardar `docker inspect libreria` o `docker exec libreria env`.
- **[Agotamiento de stock en `D-03` si se repite muchas veces]** → `scripts/seed.py` del TP carga `libro 2` con `stock=4` y rechaza correr sobre una base no vacía. Si durante las pruebas se agotara el stock antes de sacar la evidencia limpia, Amanda puede vaciar las tablas en la base `libreria` (`TRUNCATE venta_renglon, venta, libro_autor, libro, perfil_cliente, cliente, autor, genero, editorial RESTART IDENTITY CASCADE;`) y volver a correr `docker exec libreria python -m scripts.seed`.
- **[Reinicio imprevisto del VPS deja el contenedor detenido por demora de la red overlay]** → Documentado en `DEPLOY.md` el procedimiento de verificación (`docker ps -a`) y arranque manual (`docker start libreria`).

## Migration Plan

1. **Preparación en el repo (`[AGENTE]`)**: Crear `despliegue/Dockerfile`, `despliegue/env.example` y `despliegue/DEPLOY.md` (con placeholders donde corresponda). La integrante revisa y hace commit/push si desea clonar desde GitHub en el VPS (o copia los archivos de `despliegue/` al VPS).
2. **Despliegue y evidencias en el VPS (`[AMANDA-VPS]`)**:
   - Crear `/root/libreria.env` con `chmod 600`.
   - Ejecutar `docker pull python:3.12-alpine`, `docker build -t libreria .` y capturar **D-01**.
   - Ejecutar `docker run -d --name libreria --network easypanel-calculadora -p 8000:8000 --restart unless-stopped --env-file /root/libreria.env libreria`, esperar a `healthy` y capturar **D-02**.
   - Ejecutar `docker exec libreria python -m scripts.seed`.
   - Desde fuera del VPS, correr los tres `curl -i` contra `http://179.199.141.99:8000` y capturar **D-03**.
   - En el VPS, capturar los logs del comprobante para **D-08**.
   - Ejecutar `docker rm -f libreria`, repetir el `docker run`, esperar a `healthy`, verificar logs y `GET /libros/` y capturar **D-04**.
   - Ejecutar `docker run --rm libreria` (sin `--env-file`) y capturar **D-05**.
   - Ejecutar `docker run --rm --entrypoint ls libreria -a /app` y `docker run --rm --entrypoint env libreria` y capturar **D-06**.
   - Ejecutar `docker exec libreria id` y capturar **D-07**.
3. **Incorporación de evidencias y cierre (`[AGENTE]`)**: Guardar las salidas saneadas en `despliegue/evidencia/D-01_*.txt` .. `D-08_*.txt`, completar la fecha y hora reales en `despliegue/DEPLOY.md` y, una vez que CH-02 esté commiteado, actualizar la KB y `CHANGES.md`.
4. **Rollback**: `docker rm -f libreria` y `docker rmi libreria` en el VPS (no afecta al servicio `calculadora_db` ni a la aplicación de la calculadora).

