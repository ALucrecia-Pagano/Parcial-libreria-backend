# Tasks — CH-03 `despliegue-docker-vps`

> **Convención de responsables**:
> - **`[AGENTE]`**: Tareas sobre archivos del repositorio local (`despliegue/Dockerfile`, `despliegue/env.example`, `despliegue/DEPLOY.md`, `despliegue/evidencia/*.txt` y la actualización final de la KB/`CHANGES.md`). En Governance ALTO, el agente muestra el contenido antes de escribirlo.
> - **`[AMANDA-VPS]`**: Tareas que ejecuta Amanda a mano por SSH en el VPS (`179.199.141.99`) o desde su consola local hacia la URL pública. Cada una incluye el comando exacto y la salida esperada.
> - **Regla de confidencialidad**: Jamás ejecutar ni guardar en evidencia `docker inspect libreria` ni `docker exec libreria env` (muestran la contraseña real de `--env-file`). En toda salida de `docker logs libreria`, reemplazar la IP pública personal de Amanda por `<IP_CLIENTE>` antes de guardarla en `despliegue/evidencia/`.
> - **Commits en dos partes (lo hace Amanda)**: `CH-03` se commitea en **dos partes**:
>   1. **Parte 1 (tras la tarea 1.4, antes del `git clone` en el VPS)**: `despliegue/Dockerfile`, `despliegue/env.example` y `despliegue/DEPLOY.md` (más los artefactos del change si desea subirlos), necesarios en GitHub para poder hacer el `git clone` desde el VPS en la tarea 2.2.
>   2. **Parte 2 (al cierre)**: la evidencia `despliegue/evidencia/D-01_*.txt`..`D-08_*.txt`, la fecha/hora definitiva en `despliegue/DEPLOY.md`, `verify.md`, la actualización de la KB/`CHANGES.md` y el archive del change.

## 1. Artefactos de contenedor y documentación en `despliegue/` (`[AGENTE]`)

- [x] 1.1 `[AGENTE]` Verificar que `despliegue/.dockerignore` excluya `.env`, `.venv/`, `.git`, `__pycache__/`, `test/`, `docs/`, `evidencia/`, `DEPLOY.md` y `*.pdf` sin requerir modificaciones, comprobando su contenido actual por lectura.
- [x] 1.2 `[AGENTE]` Crear `despliegue/Dockerfile` a partir de `python:3.12-alpine` (sin compilador), con `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1`, `WORKDIR /app`, usuario del sistema sin privilegios (`appgroup` / `appuser`), copia e instalación de `requirements.txt` con `pip install --no-cache-dir -r requirements.txt` antes del código, `COPY` explícito de `alembic.ini`, `app`, `migrations` y `scripts`, directiva `USER appuser`, `EXPOSE 8000`, `HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD wget -qO- http://127.0.0.1:8000/health/ready > /dev/null || exit 1` y `CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]`. Verificar inspeccionando el archivo creado que no contenga secretos ni `COPY . .`.
- [x] 1.3 `[AGENTE]` Crear `despliegue/env.example` (sin tocar `despliegue/.env.example`) con la forma `DATABASE_URL=postgresql+asyncpg://<usuario>:<password>@<host>:5432/<base>` y `SQL_ECHO=false` más comentarios explicativos sin credenciales reales. Verificar que `despliegue/.env.example` permanezca sin cambios en `git status`.
- [x] 1.4 `[AGENTE]` Crear `despliegue/DEPLOY.md` con placeholders `<NOMBRE>` (grupo) y `<FECHA_HORA>` (hasta completar el despliegue), documentando:
  - URL pública: `http://179.199.141.99:8000`
  - Topología en el VPS: Docker en modo Swarm (EasyPanel), red overlay attachable `easypanel-calculadora`, servicio `calculadora_db:5432` (PostgreSQL 17), rol propio `libreria` (`LOGIN`, contraseña alfanumérica) y base `libreria` (`OWNER libreria`, sin usar el usuario `calculadora`).
  - Forma del archivo `/root/libreria.env` (únicamente nombres de variables y placeholders, sin su contenido real).
  - Comandos completos de clonado por HTTPS, `docker pull python:3.12-alpine`, `docker build`, `docker run` y carga inicial (`docker exec libreria python -m scripts.seed`).
  - Cambios hechos al TP para correr en el contenedor (`Ninguno`).
  - Cómo se actualiza (`git pull`, `docker build -t libreria .`, `docker rm -f libreria`, `docker run ...`) conservando los datos en PostgreSQL.
  - Nota operativa sobre el VPS de Lucas (no reiniciar el servidor sin coordinarlo con él porque la calculadora está en producción) y cómo levantar el contenedor a mano tras un reinicio del VPS (`docker start libreria` o recreación con `docker rm -f libreria && docker run ...` si la red overlay attachable demoró al iniciar el daemon).
  - Procedimiento de fallback completo: contenedor `postgres:17-alpine` propio con `docker run` en una red bridge dedicada (`libreria-net`) y volumen `libreria-pgdata`.
  - Notas de `DEBUG` vs `SQL_ECHO` (IN-06 / DD-23) y `BackgroundTasks` en `ventas/tasks.py` (P-18 / DD-25).
  Verificar por lectura que `despliegue/DEPLOY.md` cubra los 5 puntos exigidos por el Ejercicio 10 y no contenga credenciales.

## 2. Preparación del entorno en el VPS y construcción de la imagen (`[AMANDA-VPS]`)

- [x] 2.1 `[AMANDA-VPS]` Crear a mano por SSH en el VPS el archivo `/root/libreria.env` con permisos restringidos (`chmod 600`), usando exclusivamente la forma con placeholders (Amanda completa su contraseña alfanumérica real del rol `libreria`, sin pegarla en el chat ni en ningún archivo del repo):
  - **Forma del archivo `/root/libreria.env`**:
    ```dotenv
    DATABASE_URL=postgresql+asyncpg://libreria:<PASSWORD_ALFANUMERICA>@calculadora_db:5432/libreria
    SQL_ECHO=false
    ```
  - **Comando de permisos y verificación segura** (verifica permisos y nombres de claves sin mostrar valores):
    ```bash
    chmod 600 /root/libreria.env && stat -c "%a %n" /root/libreria.env && cut -d= -f1 /root/libreria.env
    ```
  - **Salida esperada**:
    ```text
    600 /root/libreria.env
    DATABASE_URL
    SQL_ECHO
    ```
- [x] 2.2 `[AMANDA-VPS]` Clonar el repositorio por HTTPS en el VPS (una vez subidos los archivos del grupo 1, o copiando `despliegue/` al servidor), posicionarse en `despliegue/`, descargar explícitamente la imagen base `python:3.12-alpine` y construir la imagen `libreria`:
  - **Comandos exactos**:
    ```bash
    git clone https://github.com/<USUARIO_O_ORG>/<REPO>.git /opt/parcial-libreria
    cd /opt/parcial-libreria/despliegue
    docker pull python:3.12-alpine
    docker build -t libreria .
    ```
  - **Salida esperada**: descarga de `python:3.12-alpine` y construcción exitosa de las capas (`COPY requirements.txt`, `pip install --no-cache-dir`, `COPY alembic.ini / app / migrations / scripts`, `USER appuser`, `HEALTHCHECK`) finalizando con `Successfully tagged libreria:latest` (o `naming to docker.io/library/libreria:latest done`).
- [x] 2.3 `[AMANDA-VPS]` **Caso D-01 (Imágenes base y del proyecto)**: Ejecutar `docker images` para demostrar que `python:3.12-alpine` pesa menos de 100 MB y que `libreria` se construyó:
  - **Comando exacto**:
    ```bash
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | grep -E "REPOSITORY|libreria|python"
    ```
  - **Salida esperada**: tabla con `python` tag `3.12-alpine` con tamaño `< 100MB` (aprox. `50MB–75MB`) y `libreria` tag `latest`. Copiar la salida para `despliegue/evidencia/D-01_imagenes.txt`.

## 3. Arranque del contenedor, carga inicial y pruebas externas D-02, D-03 y D-08 (`[AMANDA-VPS]`)

- [x] 3.1 `[AMANDA-VPS]` **Caso D-02 (Arranque en servidor limpio, migraciones y estado `healthy`)**: Correr el contenedor `libreria` unido a la red `easypanel-calculadora`, esperar ~25 segundos a que pase el `HEALTHCHECK` y consultar `docker ps` y `docker logs libreria`:
  - **Comandos exactos**:
    ```bash
    docker run -d --name libreria \
      --network easypanel-calculadora \
      -p 8000:8000 \
      --restart unless-stopped \
      --env-file /root/libreria.env \
      libreria
    sleep 25
    docker ps --filter "name=^libreria$"
    docker logs libreria
    ```
  - **Salida esperada**:
    - En `docker ps`: contenedor `libreria` con `STATUS` `Up ... (healthy)` y `PORTS` `0.0.0.0:8000->8000/tcp`.
    - En `docker logs libreria`: líneas de Alembic aplicando las migraciones 1 y 2 del TP (`Running upgrade  -> ..., crea tablas iniciales...`, `Running upgrade ... -> 0f5ab569096b, agrega tabla genero y relacion con libro`) seguidas de `Uvicorn running on http://0.0.0.0:8000`.
    - Copiar la salida (reemplazando cualquier IP personal por `<IP_CLIENTE>` si apareciera) para `despliegue/evidencia/D-02_build_run_ps_logs.txt` y anotar fecha y hora del despliegue para `DEPLOY.md`.
- [x] 3.2 `[AMANDA-VPS]` Cargar los datos iniciales del TP dentro del contenedor en marcha:
  - **Comando exacto**:
    ```bash
    docker exec libreria python -m scripts.seed
    ```
  - **Salida esperada**:
    ```text
    Datos iniciales: cliente=1, libros=1,2, venta=1
    ```
- [x] 3.3 `[AMANDA-VPS]` **Caso D-03 (Peticiones desde fuera del VPS con `curl -i`)**: Desde la máquina local de Amanda (fuera del VPS), ejecutar los tres pedidos contra `http://179.199.141.99:8000`:
  - **Comandos exactos**:
    ```bash
    curl -i http://179.199.141.99:8000/health/ready
    curl -i http://179.199.141.99:8000/libros/
    curl -i -X POST http://179.199.141.99:8000/ventas/ \
      -H "Content-Type: application/json" \
      -d '{"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 2, "cantidad": 1}]}'
    ```
  - **Salida esperada**:
    1. `GET /health/ready` → `HTTP/1.1 200 OK` y cuerpo `{"estado":"lista"}`.
    2. `GET /libros/` → `HTTP/1.1 200 OK` y lista JSON con los 2 libros iniciales (`Rayuela` con `stock: 10` y `Los que aman, odian` con `stock: 4`).
    3. `POST /ventas/` → `HTTP/1.1 201 Created` y cuerpo JSON de la venta `id: 2` con `precio_unitario: "25000.00"` (x2) y `"21000.00"` (x1) copiados y `"total": "71000.00"`.
    - Copiar las tres salidas completas para `despliegue/evidencia/D-03_requests_externos.txt`.
- [x] 3.4 `[AMANDA-VPS]` **Caso D-08 (Aviso del comprobante en `docker logs` — ejecutar ANTES de D-04)**: En el VPS, consultar los últimos registros de `libreria` para verificar que el aviso en segundo plano salió después de la línea de respuesta `201 Created`:
  - **Comando exacto**:
    ```bash
    docker logs --tail 25 libreria
    ```
  - **Salida esperada**:
    ```text
    INFO:     <IP_CLIENTE>:<PUERTO> - "POST /ventas/ HTTP/1.1" 201 Created
    Comprobante de venta 2 enviado a mismo_email@example.com (simulado)
    ```
    - Reemplazar la IP pública de Amanda por `<IP_CLIENTE>` y guardar para `despliegue/evidencia/D-08_aviso_comprobante.txt`.

## 4. Pruebas de persistencia, fallo sin entorno, limpieza de imagen y usuario no-root: D-04 a D-07 (`[AMANDA-VPS]`)

- [x] 4.1 `[AMANDA-VPS]` **Caso D-04 (Recreación del contenedor sin pérdida de datos ni repetición de migraciones)**: Eliminar el contenedor en el VPS, volver a correr el mismo `docker run`, esperar a que esté `healthy`, revisar `docker logs` y consultar `GET /libros/`:
  - **Comandos exactos**:
    ```bash
    docker rm -f libreria
    docker run -d --name libreria \
      --network easypanel-calculadora \
      -p 8000:8000 \
      --restart unless-stopped \
      --env-file /root/libreria.env \
      libreria
    sleep 25
    docker ps --filter "name=^libreria$"
    docker logs libreria
    curl -i http://179.199.141.99:8000/libros/
    ```
  - **Salida esperada**:
    - `docker ps` muestra el nuevo contenedor en `Up ... (healthy)`.
    - `docker logs libreria` muestra `Context impl AsyncPGImpl.` y `Will assume transactional DDL.` **sin** líneas `Running upgrade ...` (las migraciones no se repiten porque ya están aplicadas en `calculadora_db`).
    - `curl -i http://179.199.141.99:8000/libros/` responde `HTTP/1.1 200 OK` conservando los libros con el stock descontado por la venta de D-03 (`Rayuela` con `stock: 8` y `Los que aman, odian` con `stock: 3`).
    - Anonimizar `<IP_CLIENTE>` en los logs y guardar para `despliegue/evidencia/D-04_recreacion_persistencia.txt`.
- [x] 4.2 `[AMANDA-VPS]` **Caso D-05 (Ejecución sin `DATABASE_URL`)**: Ejecutar un contenedor efímero a partir de la imagen `libreria` sin `--env-file` ni `-e DATABASE_URL`, verificando que termina con error:
  - **Comando exacto**:
    ```bash
    docker run --rm libreria ; echo "EXIT_CODE=$?"
    ```
  - **Salida esperada**: traza que termina en `RuntimeError: Falta configurar DATABASE_URL en el entorno o en .env (ver .env.example)` y `EXIT_CODE=1` (el contenedor no queda sirviendo). Guardar para `despliegue/evidencia/D-05_sin_database_url.txt`.
- [x] 4.3 `[AMANDA-VPS]` **Caso D-06 (Contenido y entorno de la imagen sin `.env` ni secretos)**: Inspeccionar los archivos de `/app` y las variables horneadas en la imagen `libreria` (usando `docker run --rm --entrypoint ... libreria`, **nunca** `docker exec libreria env` ni `docker inspect libreria`):
  - **Comandos exactos**:
    ```bash
    docker run --rm --entrypoint ls libreria -a /app
    docker run --rm --entrypoint env libreria
    ```
  - **Salida esperada**:
    - En `ls -a /app`: únicamente `.`, `..`, `alembic.ini`, `app`, `migrations`, `requirements.txt`, `scripts` (sin `.env`, `.env.example`, `env.example`, `.venv` ni `.git`).
    - En `env`: únicamente `PATH`, `LANG`, `GPG_KEY`, `PYTHON_VERSION`, `PYTHON_SHA256`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `HOME=/home/appuser` (o `/`), `HOSTNAME` — sin `DATABASE_URL` ni contraseñas.
    - Guardar para `despliegue/evidencia/D-06_imagen_sin_secretos.txt`.
- [x] 4.4 `[AMANDA-VPS]` **Caso D-07 (Identidad no-root del proceso en el contenedor)**: Consultar `id` dentro del contenedor `libreria` en ejecución:
  - **Comando exacto**:
    ```bash
    docker exec libreria id
    ```
  - **Salida esperada**:
    ```text
    uid=100(appuser) gid=101(appgroup) groups=101(appgroup)
    ```
    (con `uid` y `gid` distintos de `0`/`root`). Guardar para `despliegue/evidencia/D-07_usuario_no_root.txt`.

## 5. Incorporación de evidencias D-01 a D-08 y verificación final (`[AGENTE]`)

- [x] 5.1 `[AGENTE]` Crear en `despliegue/evidencia/` los ocho archivos de evidencia (`D-01_imagenes.txt`, `D-02_build_run_ps_logs.txt`, `D-03_requests_externos.txt`, `D-04_recreacion_persistencia.txt`, `D-05_sin_database_url.txt`, `D-06_imagen_sin_secretos.txt`, `D-07_usuario_no_root.txt`, `D-08_aviso_comprobante.txt`) a partir de las salidas reales entregadas por Amanda y actualizar `<FECHA_HORA>` en `despliegue/DEPLOY.md` (conservando `<NOMBRE>` como placeholder).
- [x] 5.2 `[AGENTE]` **Verify final con la evidencia de D-01 a D-08 (`verify.md`)**: Verificar uno por uno los 8 archivos de `despliegue/evidencia/` y `despliegue/DEPLOY.md`, y dejar asentado en `openspec/changes/ch-03-despliegue-docker-vps/verify.md`:
  - Que todos los casos D-01..D-08 tienen su salida real completa y cumplen los resultados esperados de la consigna.
  - Que ningún archivo de `despliegue/` contiene contraseñas reales, salidas de `docker inspect`, salidas de `docker exec ... env` ni la IP pública sin anonimizar de la integrante.
  - Que la lógica del TP en `despliegue/app/`, `despliegue/migrations/`, `despliegue/scripts/` y `despliegue/.env.example` no fue modificada (`git status`).
  - Que `CH-03` se commiteó en dos partes: primero `Dockerfile`, `env.example` y `DEPLOY.md` (necesarios en GitHub para el `git clone` del VPS), y al cierre la evidencia y el archive.

## 6. Corrección de DD-27 en la KB y `CHANGES.md` (**DESPUÉS de que CH-02 esté commiteado**) (`[AGENTE]`)

- [x] 6.1 `[AGENTE]` (**EJECUTAR SOLO DESPUÉS DE QUE CH-02 ESTÉ COMMITEADO** — verificar antes con `git status` que no haya archivos pendientes de CH-02): Actualizar `knowledge-base/09_decisiones_y_supuestos.md` (DD-11 y DD-27), `knowledge-base/10_preguntas_abiertas.md` (IN-08 y P-04 pasan a **Resuelta**), `knowledge-base/13_despliegue.md` (§Infraestructura disponible y §Forma del comando de ejecución) y la ficha de `[CH-03]` en `CHANGES.md` para reflejar los datos confirmados en el VPS:
  - Red de EasyPanel confirmada: `--network easypanel-calculadora` (overlay con `Attachable: true`).
  - Motor: PostgreSQL 17 en `calculadora_db:5432` con rol propio `libreria` (`LOGIN`, contraseña alfanumérica) y base `libreria` (`OWNER libreria`); no se usa el usuario `calculadora`.
  - Puerto público: `8000` (`http://179.199.141.99:8000`).
  - Corrección del fallback de DD-27: si fallara la conexión al PostgreSQL existente o la red overlay, el fallback real es levantar un contenedor PostgreSQL propio con `docker run` en una red `bridge` dedicada (`libreria-net`), y no crear otro servicio de EasyPanel (que quedaría igualmente en una red overlay de Swarm).
  Verificar con `git diff knowledge-base/ CHANGES.md` que solo se hayan actualizado esas secciones.

## Workflow follow-up

- Archivar el change con `/opsx:archive ch-03-despliegue-docker-vps`, marcar `[x]` el estado de CH-03 en `CHANGES.md` y cerrar con el resumen en criollo de no más de 10 líneas.

