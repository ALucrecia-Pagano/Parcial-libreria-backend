# Tasks

## 1. Estructura del monorepo

- [ ] 1.1 Mover `parcial/` a `backend/` con `git mv` y actualizar las referencias en `README.md`, `AGENTS.md`, `backend/README.md`, `backend/env.example`, `backend/seed.py` y `backend/test/*.http`; en `CHANGES.md` agregar una nota de que las rutas `parcial/...` de CH-01..CH-15 son históricas. Verificar que `uvicorn app.main:app --reload` arranca desde `backend/` y que `alembic upgrade head` sigue funcionando.
- [ ] 1.2 Mover el runtime del frontend a `frontend/public/` (`index.html`, `css/`, `js/`, `assets/`, `fonts/`) y la documentación histórica a `frontend/docs/` (`knowledge-base/`, `CHANGES.md`, `openspec/`); crear `frontend/README.md`. Verificar que `index.html` carga CSS/JS/imágenes/fuentes con rutas relativas y que no quedan referencias a `file://`.
- [ ] 1.3 Actualizar `.gitignore` raíz y `frontend/.gitignore` (sin ignorar `frontend/public/`, `AGENTS.md`, `CLAUDE.md`, `openspec/`) y el `README.md` raíz con el nuevo layout. Verificar con `git status` que no se ignora ningún artefacto requerido.

## 2. Backend: CORS y contratos que faltan

- [ ] 2.1 Agregar `CORS_ORIGINS` a `backend/app/core/config.py` (default local y parser de lista separada por comas) y documentarla en `backend/env.example`. Verificar que un valor vacío o inválido no rompe el arranque y que `settings.cors_origins` devuelve la lista esperada.
- [ ] 2.2 Agregar `CORSMiddleware` en `backend/app/main.py` después de `app = FastAPI(...)`, con orígenes explícitos, credenciales, métodos y `Content-Type`. Verificar con `curl -i -X OPTIONS http://localhost:8000/auth/login -H "Origin: http://localhost:8080"` que devuelve `Access-Control-Allow-Origin` y `Access-Control-Allow-Credentials`, y que un origen no listado no los devuelve.
- [ ] 2.3 Implementar `GET /clientes` paginado (VENDEDOR/ADMIN) con `listar_con_perfil` (`joinedload(Cliente.perfil)`), `service.listar` y la ruta en `router_staff`; agregar `backend/test/G-01_clientes_listado.http`. Verificar 200 con `{items,total,page,size,pages}` y `perfil`, 401 sin cookie, 403 con CLIENTE y 422 con página fuera de rango.
- [ ] 2.4 Agregar `cliente_nombre` a `VentaRead` y `joinedload(Venta.cliente)` en el listado de ventas; agregar `backend/test/G-01_ventas_listado.http`. Verificar que `GET /ventas` y `GET /mis-ventas` devuelven `cliente_nombre` y que el número de consultas no crece con las filas (revisar `SQL_ECHO=true`).
- [ ] 2.5 Actualizar `backend/README.md` con las nuevas rutas y el comando de seed; verificar que los `.http` corren después de `python seed.py`.

## 3. Backend: Docker

- [ ] 3.1 Crear `backend/Dockerfile` (`python:3.12-alpine`, `appuser` sin privilegios, `requirements.txt` con `--no-cache-dir`, `alembic.ini`, `app/`, `migrations/`, `seed.py`, `EXPOSE 8000`, `HEALTHCHECK /health/ready`, `CMD ["sh","-c","alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]`). Verificar `docker build -t libreria-backend ./backend` y `docker run --rm --entrypoint id libreria-backend` (UID y GID distintos de 0).
- [ ] 3.2 Crear `backend/.dockerignore` (`.env`, `.venv`, `.git`, `__pycache__`, `*.pyc`, `test/`, `docs/`, `evidencia/`, `*.pdf`). Verificar que `docker run --rm --entrypoint ls libreria-backend -a /app` no muestra `.env` ni `.git`.
- [ ] 3.3 Verificar el arranque con una base real: `docker run --env-file backend/.env -p 8000:8000 libreria-backend`, `curl http://localhost:8000/health/ready` y revisar `docker logs` con las migraciones; ejecutar el seed una vez con `docker exec <contenedor> python seed.py`.

## 4. Frontend: Docker y Nginx

- [ ] 4.1 Crear `frontend/Dockerfile` con `nginxinc/nginx-unprivileged:1.27-alpine`, copiar `public/` a `/usr/share/nginx/html` y `default.conf.template` a `/etc/nginx/templates/`, `EXPOSE 8080` y healthcheck `/healthz`. Verificar `docker build -t libreria-frontend ./frontend` y que el proceso corre con UID distinto de 0.
- [ ] 4.2 Crear `frontend/default.conf.template` con `listen 8080`, `try_files $uri $uri/ /index.html`, `location /api/ { proxy_pass ${API_UPSTREAM}/; ... }` y `location = /healthz`. Verificar `GET /`, `GET /catalogo` (fallback) y `GET /api/health/ready` con `API_UPSTREAM=http://backend:8000`.
- [ ] 4.3 Crear `frontend/.dockerignore` (`node_modules/`, `.git/`, `docs/`, `README.md`, `.env`) y verificar que la imagen no contiene secretos ni documentación innecesaria.
- [ ] 4.4 Verificar el login a través de Nginx con `curl -i -c cookies.txt -X POST http://localhost:8080/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"Secreto1234!"}'` y una petición posterior con `-b cookies.txt` a `/api/auth/yo`.

## 5. Compose local y despliegue

- [ ] 5.1 Crear `docker-compose.yml` con `db` (PostgreSQL 16/17), `backend` (build `backend/`, `POSTGRES_*`, `JWT_SECRET`, `COOKIE_SECURE=false`, `CORS_ORIGINS=http://localhost:8080`), `frontend` (build `frontend/`, `API_UPSTREAM=http://backend:8000`, `8080:8080`), healthchecks y `depends_on`. Verificar `docker compose up --build` y `docker compose exec backend python seed.py`.
- [ ] 5.2 Documentar en `README.md` el despliegue EasyPanel (dos servicios, `API_UPSTREAM` interno, `CORS_ORIGINS` con la URL pública, puerto 8080, `COOKIE_SECURE=true` con HTTPS, seed manual) y el rollback. Verificar que los comandos documentados se ejecutan tal cual y no incluyen credenciales reales.

## 6. Frontend: capa API y mapeo

- [ ] 6.1 Crear `frontend/public/js/api.js` con `API_BASE='/api'`, `apiFetch` (`credentials:'include'`, JSON, `ApiError` con `status/detail/retryAfter`) y los wrappers de auth, catálogo, libros, clientes, ventas e historial. Verificar en consola que `/api/health/ready` devuelve 200 y que un 409/422 produce un `ApiError` con el `detail` del backend.
- [ ] 6.2 Crear `frontend/public/js/mapeo.js` con `idConPrefijo`/`idSinPrefijo`, `aModeloLibro/Cliente/Venta` y `aDtoLibro/Cliente/Venta` (`Decimal`→`Number`, `V-####`, `nombreCompleto`, `clienteNombre`, snake↔camel, `Pagina.items`). Verificar con el seed: precio `"25000.00"` → `25000`, venta `1` → `V-0001`, cliente `nombre` → `nombreCompleto`.
- [ ] 6.3 Reducir `frontend/public/js/storage.js` a preferencias (tema/sidebar) y eliminar las claves de dominio; reducir `frontend/public/js/data.js` a portadas/tapas y helpers de formato. Verificar que recargar no crea `libreria.libros`/`clientes`/`ventas` y que el tema/sidebar persisten.

## 7. Frontend: sesión y roles

- [ ] 7.1 Agregar al `index.html` el bloque `#sesion` en la sidebar (`#form-login` con `email`/`password`, `#login-errores`, `#login-mensaje`; estado autenticado con `#sesion-usuario`, `#sesion-roles`, `#btn-logout`, `#btn-cambiar-password`, `#form-cambiar-password`), los `data-requiere-rol` en formularios/botones protegidos, `#error-conexion` con botón "Reintentar" y `aria-live` en `#venta-total`. Verificar que los IDs/names existentes no cambian y que el HTML valida.
- [ ] 7.2 Crear `frontend/public/js/sesion.js` con `iniciarSesion`, `cerrarSesion`, `refrescarSesion` (`/auth/yo`), `puede(rol)`, `actualizarUI` y manejo de `debe_cambiar_password`. Verificar login admin/vendedor/cliente, logout, recarga con sesión y el flujo de `nuevo@example.com`.
- [ ] 7.3 Agregar estilos BEM en `frontend/public/css/styles.css` para sesión, estados de carga/error y botones deshabilitados; verificar 320 px, 1280 px, foco visible y navegación por teclado.

## 8. Frontend: pantallas conectadas

- [ ] 8.1 Catálogo: cargar libros/editoriales/géneros/autores desde la API (`size=100`), renderizar con `textContent`/`createElement`, mantener el filtro por título con `normalizarTexto` y los estados carga/vacío/error. Verificar con el seed que se ven los 5 libros y que el filtro por título funciona.
- [ ] 8.2 Libros: cargar la tabla y los selects desde la API; alta con `POST /libros` (solo ADMIN), mostrar stock, mapear errores 409/422 y refrescar la tabla. Verificar alta de un libro nuevo, ISBN duplicado (409), precio inválido (422) y que un VENDEDOR/CLIENTE no ve el formulario.
- [ ] 8.3 Clientes: cargar la tabla desde `GET /clientes?size=100` (staff), alta con `POST /clientes`, mapear 409/422 y refrescar. Verificar alta, email duplicado (409) y que CLIENTE/anónimo no ven la vista.
- [ ] 8.4 Ventas: cargar clientes/libros desde la API, armar renglones, `POST /ventas`, mostrar el total del servidor, errores 409/422 y refrescar stock/historial. Verificar venta válida, venta sin stock (409), libro repetido (422) y que el selector de clientes se puebla.
- [ ] 8.5 Historial: staff `GET /ventas`, CLIENTE `GET /mis-ventas`, mostrar `cliente_nombre`, ordenar descendente en el cliente, detalle con `GET /ventas/{id}`, estados carga/vacío/error. Verificar que el detalle muestra renglones y que el CLIENTE solo ve sus ventas.
- [ ] 8.6 Visibilidad por rol y errores globales: ocultar/mostrar vistas y acciones según `puede(rol)`, mapear 401/403/404/409/422/429/red a mensajes en español y preservar `aria-live`/foco. Verificar 401 (sin sesión), 403 (CLIENTE en staff), 429 (5 logins fallidos) y caída del backend con "Reintentar".

## 9. Documentación y verificación final

- [ ] 9.1 Actualizar `README.md` raíz, `backend/README.md`, `frontend/README.md`, `backend/env.example` y `CHANGES.md` (sección G-01) con layout, comandos, variables, seed, EasyPanel y casos manuales. Verificar que no hay credenciales reales y que las rutas documentadas existen.
- [ ] 9.2 Correr `openspec validate --all --strict` y `git status`; verificar que el change valida sin warnings y que solo aparecen los archivos esperados (sin `.env` ni artefactos de build).
- [ ] 9.3 Ejecutar la verificación manual E2E: `docker compose up --build`, seed, login admin, alta de libro/cliente, venta, stock, historial, login vendedor, login cliente (`ana@example.com`), `nuevo@example.com` (cambio obligatorio), 320 px/1280 px/teclado. Registrar el resultado real en `README.md`.

## Workflow follow-up

- Archivar el change después de la revisión y actualizar los specs principales (`openspec archive`).
- Desplegar en EasyPanel los dos servicios y verificar login/venta contra PostgreSQL; completar la URL pública en `CORS_ORIGINS` y en el README.
- Evaluar como follow-up: "cargar más" para listados mayores a 100, migración opcional de datos de `localStorage` y CSP/headers de seguridad en Nginx.
