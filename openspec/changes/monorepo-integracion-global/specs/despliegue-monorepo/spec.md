# Spec Delta

## Purpose

Define el empaquetado y despliegue del monorepo de la librería: una imagen del backend FastAPI y una imagen Nginx del frontend que sirve la SPA y proxya `/api` al backend, con configuración por entorno, healthchecks y sin secretos horneados.

## ADDED Requirements

### Requirement: Estructura del monorepo
El repositorio SHALL organizar la aplicación en `backend/` (API FastAPI completa) y `frontend/public/` (HTML, CSS, JS, imágenes y fuentes), y SHALL conservar `despliegue/` como entrega histórica de los capítulos 1 a 4 sin modificarla.

#### Scenario: Layout verificable
- **WHEN** se lista la raíz del repositorio
- **THEN** existen `backend/`, `frontend/public/index.html`, `frontend/public/css/`, `frontend/public/js/`, `frontend/public/assets/`, `frontend/public/fonts/` y `despliegue/`, y `parcial/` ya no existe

### Requirement: Imagen del backend con migración y salud
La imagen del backend SHALL partir de `python:3.12-alpine`, ejecutarse con un usuario sin privilegios y, al iniciar con configuración válida, SHALL aplicar `alembic upgrade head` antes de levantar `uvicorn app.main:app` en `0.0.0.0:8000`; SHALL declarar un `HEALTHCHECK` contra `http://127.0.0.1:8000/health/ready`.

#### Scenario: Arranque saludable del backend
- **WHEN** se construye `backend/Dockerfile` y se ejecuta el contenedor con `POSTGRES_*` y `JWT_SECRET` válidos
- **THEN** el contenedor aplica las migraciones, queda `healthy` y `GET /health/ready` responde 200

#### Scenario: Usuario sin privilegios
- **WHEN** se ejecuta `docker exec <contenedor-backend> id`
- **THEN** el UID y el GID informados son distintos de 0

### Requirement: Imagen del frontend con proxy same-origin
La imagen del frontend SHALL servir `frontend/public/` con Nginx sin privilegios, SHALL resolver rutas de la SPA con fallback a `index.html` y SHALL proxear las peticiones `/api/` al backend indicado por `API_UPSTREAM`, preservando método, cuerpo, cabeceras y cookies.

#### Scenario: SPA y proxy funcionando
- **WHEN** se ejecuta el contenedor del frontend con `API_UPSTREAM=http://backend:8000` y se solicita `GET /` y `GET /api/health/ready`
- **THEN** `GET /` devuelve el `index.html` y `GET /api/health/ready` devuelve 200 con el cuerpo del backend

#### Scenario: Ruta desconocida de la SPA
- **WHEN** se solicita `GET /catalogo` (ruta del cliente) al contenedor del frontend
- **THEN** Nginx devuelve `index.html` con código 200 en lugar de 404

#### Scenario: Cookie de sesión a través del proxy
- **WHEN** el navegador hace `POST /api/auth/login` con credenciales válidas a través del frontend
- **THEN** la respuesta incluye `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax; Path=/` y las peticiones posteriores a `/api/` envían la cookie al backend

### Requirement: Configuración por entorno sin secretos
Las imágenes SHALL recibir `API_UPSTREAM`, `CORS_ORIGINS`, `POSTGRES_*` y `JWT_SECRET` en tiempo de ejecución y MUST NOT incluir archivos `.env`, credenciales reales ni secretos horneados; `frontend/.dockerignore` y `backend/.dockerignore` SHALL excluir `.env`, `.git`, entornos virtuales y artefactos de desarrollo.

#### Scenario: Imagen sin secretos
- **WHEN** se inspecciona la imagen del backend o del frontend
- **THEN** no existe ningún archivo `.env` ni variable con contraseñas o `JWT_SECRET` en la imagen

### Requirement: Despliegue local y en EasyPanel
El repositorio SHALL incluir un `docker-compose.yml` para desarrollo local con PostgreSQL, backend y frontend, y la documentación SHALL describir el despliegue en EasyPanel como dos servicios separados (backend y frontend) con `API_UPSTREAM` interno y `CORS_ORIGINS` con la URL pública del frontend.

#### Scenario: Levantar el conjunto local
- **WHEN** se ejecuta `docker compose up --build` con las variables de ejemplo
- **THEN** el backend queda saludable, el frontend responde en `http://localhost:8080` y el login funciona a través de `/api`

#### Scenario: Documentación de EasyPanel
- **WHEN** se revisa `README.md`
- **THEN** describe los dos servicios, las variables `API_UPSTREAM`/`CORS_ORIGINS`, el puerto 8080 del frontend, la ejecución de `alembic upgrade head` y `python seed.py`, y no contiene credenciales reales
