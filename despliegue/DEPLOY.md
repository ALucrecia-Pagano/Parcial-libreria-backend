# Despliegue en VPS — TP Librería (Capítulos 1 a 4)

- **Grupo**: `EDITORIAL CODEX` (Pagano Amanda, Liendo Mateo, Avila Lucas, Valentini Tiziano, García Juan)
- **URL pública**: `http://179.199.141.99:8000`
- **Día y hora del despliegue**: 04/11/2026, 10:37 (hora de Argentina, UTC-3)

---

## 1. Infraestructura y arquitectura de conexión en el VPS

El servidor VPS (`179.199.141.99`) corre Docker en modo **Swarm** (administrado con EasyPanel). El motor **PostgreSQL 17** ya se encuentra en ejecución dentro del servicio `db` del proyecto `calculadora` (nombre de host interno `calculadora_db`, puerto `5432` **sin publicar** hacia el exterior).

- **Red Docker**: `easypanel-calculadora` (red `overlay` con `Attachable: true`). Al lanzar el contenedor `libreria` con `--network easypanel-calculadora`, Docker resuelve internamente `calculadora_db` y alcanza el puerto `5432` sin exponer la base de datos en Internet.
- **Rol y base de datos propios**: En ese servidor PostgreSQL 17 se crearon el rol `libreria` (con atributo `LOGIN` y contraseña alfanumérica) y la base de datos `libreria` con `OWNER libreria`. **No** se utiliza el usuario `calculadora`.
- **Puerto público**: `8000` (`-p 8000:8000`).

---

## 2. Archivo de variables de entorno en el servidor

Las credenciales nunca se incluyen en el repositorio, en `Dockerfile` ni en la imagen. En el VPS se administra manualmente el archivo `/root/libreria.env` (fuera del repositorio, con permisos `chmod 600`), cuya **forma** (sin valores reales) es:

```dotenv
DATABASE_URL=postgresql+asyncpg://libreria:<contraseña>@calculadora_db:5432/libreria
SQL_ECHO=false
```

> **Nota sobre la contraseña y Alembic**: `migrations/env.py` pasa `settings.DATABASE_URL` a `config.set_main_option("sqlalchemy.url", ...)`, donde `ConfigParser` interpreta el carácter `%` como interpolación. Por eso la contraseña del rol `libreria` es alfanumérica.

---

## 3. Comandos completos de construcción, ejecución y carga inicial

### 3.1. Clonado del repositorio y construcción de la imagen (`docker build`)

La imagen se construye directamente en el VPS: el repositorio es público, así que se clona por HTTPS sin credenciales, y se evita tener que trasladar la imagen desde otra máquina.

Se clona el repositorio por HTTPS en el VPS, se descarga explícitamente la imagen base `python:3.12-alpine` y se construye la imagen desde la carpeta `despliegue/`:

```bash
git clone https://github.com/ALucrecia-Pagano/Parcial-libreria-backend.git /opt/parcial-libreria
cd /opt/parcial-libreria/despliegue
docker pull python:3.12-alpine
docker build -t libreria .
```

### 3.2. Ejecución del contenedor (`docker run`)

Se ejecuta el contenedor pasándole la red `easypanel-calculadora` y la ruta del archivo `/root/libreria.env`:

```bash
docker run -d --name libreria \
  --network easypanel-calculadora \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file /root/libreria.env \
  libreria
```

Al arrancar, el contenedor ejecuta `alembic upgrade head` y luego inicia `uvicorn app.main:app --host 0.0.0.0 --port 8000`. El `HEALTHCHECK` consulta `http://127.0.0.1:8000/health/ready` cada 30 segundos (`--timeout=5s --start-period=20s --retries=3`).

### 3.3. Carga de datos iniciales (seed del TP)

Una vez que el contenedor está en estado `healthy`, se cargan los datos iniciales del TP ejecutando dentro del contenedor:

```bash
docker exec libreria python -m scripts.seed
```

---

## 4. Cambios realizados al TP para correr en el contenedor

**Ninguno.** No se modificó ningún archivo de código de la aplicación (`app/`), migraciones (`migrations/`), scripts (`scripts/`), `requirements.txt`, `alembic.ini` ni `.env.example`. Únicamente se agregaron los archivos de empaquetado y documentación (`Dockerfile`, `env.example`, `DEPLOY.md` y `evidencia/`).

### Notas técnicas sobre el comportamiento del TP tal como se entregó
- **`SQL_ECHO` vs `DEBUG` (IN-06 / DD-23)**: `app/core/config.py` del TP lee la variable `DEBUG` (y no `SQL_ECHO`) para activar `echo` en el motor de SQLAlchemy. El archivo `/root/libreria.env` y `env.example` incluyen `SQL_ECHO=false` tal como pide la consigna del parcial; el TP ignora esa variable de forma inofensiva y mantiene `DEBUG=false` por defecto.
- **`BackgroundTasks` para el caso D-08 (P-18 / DD-25)**: El TP ya implementa `BackgroundTasks` en `app/modules/ventas/tasks.py` (`avisar_comprobante`), registrando en el logger `uvicorn.error` la línea `Comprobante de venta <id> enviado a <email> (simulado)` medio segundo después de devolver la respuesta `201 Created` de `POST /ventas/`.

---

## 5. Cómo se actualiza la aplicación

Como los datos residen en el servicio PostgreSQL externo (`calculadora_db`) y no dentro del contenedor, actualizar la aplicación no produce pérdida de datos:

```bash
cd /opt/parcial-libreria/despliegue
git pull
docker build -t libreria .
docker rm -f libreria
docker run -d --name libreria \
  --network easypanel-calculadora \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file /root/libreria.env \
  libreria
```

Al volver a arrancar, `alembic upgrade head` detecta que las migraciones ya están aplicadas en la base `libreria` y no las repite.

---

## 6. Convivencia en el VPS de producción y recuperación tras un reinicio

El VPS pertenece a Lucas y aloja en producción el proyecto `calculadora`: **no se debe reiniciar el VPS sin coordinarlo previamente con él**.

Si el VPS llegara a reiniciarse por mantenimiento del proveedor, aunque el contenedor tiene `--restart unless-stopped`, en Docker Swarm un contenedor standalone unido a una red `overlay` (`attachable=true`) puede no volver a levantarse solo si el daemon de Docker intenta iniciarlo antes de que Swarm termine de inicializar la red `easypanel-calculadora`. Para verificarlo y levantarlo a mano tras un reinicio:

```bash
# 1. Verificar el estado del contenedor
docker ps -a --filter "name=^libreria$"

# 2. Si figura Exited, iniciarlo nuevamente una vez activa la red overlay
docker start libreria

# 3. Si necesitara re-adjuntarse a la red, recrearlo (los datos siguen en calculadora_db)
docker rm -f libreria
docker run -d --name libreria \
  --network easypanel-calculadora \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file /root/libreria.env \
  libreria
```

---

## 7. Procedimiento de contingencia (Fallback: PostgreSQL en red bridge propia)

En caso de que la red overlay `easypanel-calculadora` o el servicio `calculadora_db` no estuvieran disponibles, el fallback independiente de Swarm/EasyPanel consiste en crear una red `bridge` propia (`libreria-net`) y levantar un contenedor PostgreSQL dedicado con volumen persistente:

```bash
# 1. Crear red bridge dedicada y volumen persistente
docker network create libreria-net
docker volume create libreria-pgdata

# 2. Levantar PostgreSQL 17 interno en la red bridge (sin publicar el 5432 al exterior)
docker run -d --name libreria_db \
  --network libreria-net \
  --restart unless-stopped \
  -v libreria-pgdata:/var/lib/postgresql/data \
  --env-file /root/libreria_pg.env \
  postgres:17-alpine

# 3. En /root/libreria.env apuntar el host a libreria_db:
# DATABASE_URL=postgresql+asyncpg://libreria:<contraseña>@libreria_db:5432/libreria
# SQL_ECHO=false

# 4. Correr la aplicación en la red bridge propia
docker rm -f libreria
docker run -d --name libreria \
  --network libreria-net \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file /root/libreria.env \
  libreria
```

