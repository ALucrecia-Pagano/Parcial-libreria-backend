# despliegue-contenedor-vps Specification

## Purpose

Define los requisitos de empaquetado en contenedor Docker y despliegue en el VPS para la aplicación del Trabajo Práctico (capítulos 1 a 4 en `despliegue/`), garantizando liviandad de imagen base, ejecución sin privilegios, ausencia de secretos horneados, verificación de salud y persistencia externa de datos verificables mediante los casos D-01 a D-08.

## Requirements

### Requirement: Imagen base liviana y caché de dependencias
La imagen del contenedor SHALL partir de `python:3.12-alpine` (con un tamaño de imagen base inferior a 100 MB y sin instalar compilador) y SHALL copiar e instalar `requirements.txt` con `--no-cache-dir` en una capa previa a la copia del código de la aplicación.

#### Scenario: Verificación de tamaño de imagen base (D-01)
- **WHEN** se descarga `python:3.12-alpine`, se construye la imagen de la aplicación y se consulta `docker images`
- **THEN** `python:3.12-alpine` figura con un tamaño menor a 100 MB y la imagen del proyecto parte de ella

### Requirement: Ejecución con usuario sin privilegios
El contenedor SHALL ejecutar el proceso de la aplicación bajo un usuario del sistema sin privilegios (distinto de `root`, UID distinto de `0`) declarado mediante la directiva `USER`.

#### Scenario: Comprobación de identidad del proceso en ejecución (D-07)
- **WHEN** se ejecuta `docker exec libreria id` sobre el contenedor en marcha
- **THEN** la salida informa un UID y GID distintos de `0` (`root`)

### Requirement: Ausencia de secretos y archivos sensibles en la imagen
La imagen y el repositorio SHALL excluir archivos `.env`, entornos virtuales, historial Git y credenciales reales; el contenedor SHALL copiar únicamente los artefactos de ejecución necesarios (`alembic.ini`, `app/`, `migrations/`, `scripts/`) y SHALL recibir `DATABASE_URL` exclusivamente en tiempo de ejecución.

#### Scenario: Inspección de archivos y entorno de la imagen (D-06)
- **WHEN** se ejecuta `docker run --rm --entrypoint ls libreria -a /app` y `docker run --rm --entrypoint env libreria`
- **THEN** en `/app` no existe ningún archivo `.env` (ni `.env.example` ni `env.example`) y el listado de variables de la imagen no contiene `DATABASE_URL` ni contraseñas

#### Scenario: Falla inmediata al iniciar sin configuración de base (D-05)
- **WHEN** se intenta ejecutar la imagen sin proveer `DATABASE_URL` (`docker run --rm libreria`)
- **THEN** el contenedor no queda sirviendo y finaliza con código de error porque la aplicación carece de dirección de base por defecto

### Requirement: Migración al arranque, chequeo de salud y servicio público
Al iniciar con configuración válida, el contenedor SHALL aplicar `alembic upgrade head` antes de levantar el servidor HTTP en `0.0.0.0:8000` y SHALL declarar un `HEALTHCHECK` (`--interval=30s --timeout=5s --start-period=20s --retries=3`) contra `http://127.0.0.1:8000/health/ready`.

#### Scenario: Arranque limpio y estado saludable en el VPS (D-02)
- **WHEN** se construye y ejecuta el contenedor en el VPS conectado a la base `libreria` y se consulta `docker ps` y `docker logs libreria`
- **THEN** el contenedor alcanza el estado `healthy` y los registros muestran las migraciones del TP aplicadas al arrancar

#### Scenario: Peticiones externas y aviso en segundo plano (D-03 y D-08)
- **WHEN** desde fuera del VPS se invoca `GET /health/ready`, `GET /libros/` (con los datos iniciales cargados) y `POST /ventas/` sobre la URL pública `http://179.199.141.99:8000`
- **THEN** las respuestas devuelven `200`, `200` con la lista de libros y `201` con precios copiados y total `71000.00`, y en `docker logs libreria` aparece el aviso del comprobante después de la línea de respuesta del `POST /ventas/`

### Requirement: Persistencia externa de datos ante recreación del contenedor
Los datos de la aplicación SHALL residir en el servidor PostgreSQL externo y no en el sistema de archivos del contenedor, conservándose intactos al eliminar y recrear el contenedor.

#### Scenario: Eliminación y recreación del contenedor (D-04)
- **WHEN** se ejecuta `docker rm -f libreria` y se vuelve a lanzar el mismo comando `docker run`
- **THEN** el nuevo contenedor vuelve al estado `healthy`, las migraciones no se repiten en `docker logs libreria` y `GET /libros/` conserva los datos y el stock descontado por la venta previa

### Requirement: Documentación operativa y plantilla de variables de entorno
El directorio `despliegue/` SHALL incluir `env.example` (sin modificar `.env.example` del TP) con la forma de `DATABASE_URL` y `SQL_ECHO=false`, y `DEPLOY.md` con la URL pública, fecha y hora, comandos completos sin secretos, cambios hechos al TP, procedimiento de actualización, recuperación tras reinicio del VPS y evidencias en `despliegue/evidencia/`.

#### Scenario: Verificación de documentación y confidencialidad de evidencias
- **WHEN** se revisan `despliegue/env.example`, `despliegue/DEPLOY.md` y los archivos de `despliegue/evidencia/`
- **THEN** todos los requisitos documentales de los Ejercicios 9 y 10 están presentes y ningún archivo contiene contraseñas reales, salidas de `docker inspect`/`docker exec ... env` ni direcciones IP personales sin anonimizar

