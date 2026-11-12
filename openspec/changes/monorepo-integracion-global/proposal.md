# Proposal: Monorepo e integración global frontend–API

## Why

La Etapa 2 Global exige que el frontend de la librería consuma la API real (FastAPI + PostgreSQL) y que todo el conjunto se despliegue como una unidad. Hoy el frontend vive en otro repositorio, se abre por `file://`, persiste libros/clientes/ventas en `localStorage` y no puede autenticarse contra la API; el backend tiene la aplicación completa en `parcial/` pero no un Dockerfile para ella, y no expone CORS ni un listado de clientes. Sin un monorepo con proxy same-origin, las cookies `HttpOnly` y los flujos de venta no funcionan de forma confiable.

## What Changes

- **Estructura monorepo**: mover `parcial/` a `backend/` y el runtime del frontend a `frontend/public/` (`index.html`, `css/`, `js/`, `assets/`, `fonts/`); conservar `despliegue/` como entrega histórica de los caps. 1–4.
- **Backend dockerizado**: crear `backend/Dockerfile` y `backend/.dockerignore` (usuario sin privilegios, `alembic upgrade head`, `uvicorn` en `0.0.0.0:8000`, healthcheck `/health/ready`).
- **Frontend dockerizado**: crear `frontend/Dockerfile`, `frontend/.dockerignore` y `frontend/default.conf.template` (Nginx sin privilegios, SPA con fallback a `index.html`, proxy `/api/` → `API_UPSTREAM`).
- **CORS configurable**: agregar `CORS_ORIGINS` a `Settings` y `CORSMiddleware` en `backend/app/main.py`, con orígenes explícitos y credenciales.
- **API para el frontend**: agregar `GET /clientes` paginado (staff, con perfil) y `cliente_nombre` en `VentaRead` (listados de ventas), sin N+1.
- **Integración del frontend**: cliente `fetch` con `credentials: 'include'`, login/logout/`/auth/yo`, mapeo DTO↔modelo, estados de carga/error/vacío, visibilidad por rol y flujo de `debe_cambiar_password`.
- **Persistencia**: eliminar el seed y la persistencia de dominio en `localStorage`; el servidor es la fuente de verdad. Solo quedan tema y sidebar como preferencias locales.
- **BREAKING**: el frontend deja de funcionar por `file://`; debe servirse por HTTP (Nginx local o EasyPanel) para que la cookie de sesión y el proxy `/api` funcionen. La ruta `parcial/` pasa a `backend/` y las referencias en documentación/scripts se actualizan.

## Capabilities

### New Capabilities
- `despliegue-monorepo`: layout del monorepo, imagen del backend, imagen Nginx del frontend, `API_UPSTREAM`, healthchecks, variables de entorno y despliegue local/EasyPanel.
- `integracion-frontend-api`: contrato del cliente API, sesión por cookie, mapeo de DTOs, pantallas conectadas, errores/carga/accesibilidad y preferencias locales.

### Modified Capabilities
- `clientes`: se agrega el listado paginado `GET /clientes` (staff) con perfil, necesario para la tabla y el selector de venta.
- `ventas`: los listados `GET /ventas`, `GET /clientes/{cliente_id}/ventas` y `GET /mis-ventas` agregan `cliente_nombre` para el historial.
- `configuracion-y-ciclo-de-vida`: se agrega `CORS_ORIGINS` y el comportamiento de `CORSMiddleware`.

## Impact

- **Backend**: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/modules/clientes/{router,service,repository,schemas}.py`, `backend/app/modules/ventas/{schemas,repository,service}.py`, `backend/env.example`, `backend/README.md`, `backend/test/*.http`.
- **Frontend**: `frontend/public/index.html`, `frontend/public/js/{app,api,mapeo,sesion,storage,data}.js`, `frontend/public/css/styles.css`, `frontend/README.md`, `frontend/docs/` (KB/OpenSpec históricos).
- **Infra**: `backend/Dockerfile`, `backend/.dockerignore`, `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/default.conf.template`, `docker-compose.yml` (local), `.gitignore`, `README.md`, `CHANGES.md`.
- **Datos**: PostgreSQL existente (`calculadora_db`/`libreria`) o una base nueva; sin migración de datos de `localStorage`. El seed del backend (`python seed.py`) pasa a ser la fuente de datos de demo.
- **Despliegue**: EasyPanel con dos servicios (backend y frontend) o `docker compose` local; `API_UPSTREAM` y `CORS_ORIGINS` por entorno.
