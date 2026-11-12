# Design: Monorepo e integración global

## Context

Ver `proposal.md` — Why. El estado actual es: dos repositorios; el backend completo vive en `parcial/` (auth, roles, catálogo, stock, clientes, ventas) y `despliegue/` es la copia reducida del TP de caps. 1–4; el frontend es estático, se abre por `file://`, usa `localStorage` para libros/clientes/ventas y no tiene CORS ni cliente HTTP. La API ya expone catálogo, auth por cookie `access_token` (`HttpOnly`, `SameSite=Lax`, `Path=/`), clientes y ventas, pero no un listado de clientes ni `cliente_nombre` en los listados de ventas. EasyPanel ya hospeda el backend del TP y PostgreSQL; no usa Docker Compose en producción.

## Goals / Non-Goals

**Goals:**
- Un solo repositorio con dos imágenes independientes (backend FastAPI y frontend Nginx) y un contrato same-origin `/api`.
- Que login, catálogo, libros, clientes, ventas e historial funcionen contra la API real, con roles y cookies.
- Mantener la UX/accesibilidad actual y las portadas CSS; conservar `despliegue/` intacto.
- Poder levantar todo localmente con `docker compose` y desplegar en EasyPanel con dos servicios.

**Non-Goals:**
- Reescribir el frontend con framework o módulos ES; sigue siendo JS clásico con `defer`.
- Migrar datos existentes de `localStorage` al servidor (el seed es la fuente de demo).
- Cambiar reglas de negocio, esquema de datos o migraciones del backend.
- Implementar los extras C-12 (Inicio, escritores, estrellas, toasts, migas) o un registro completo de clientes desde la UI.
- Añadir Redis, caché, paginación infinita o búsqueda server-side avanzada.

## Decisions

### 1. Layout del monorepo

```
backend/                 # desde parcial/ (git mv)
frontend/
  public/                # index.html, css/, js/, assets/, fonts/
  Dockerfile
  .dockerignore
  default.conf.template
  README.md
  docs/                  # knowledge-base/, CHANGES.md y openspec/ históricos del frontend
despliegue/              # intacto (TP caps. 1-4)
openspec/                # OpenSpec activo del backend
knowledge-base/          # KB activa del backend
docker-compose.yml       # solo local
```

- **Alternativas descartadas**: submódulo Git (dos repos, difícil de desplegar juntos) y fusionar `despliegue/` dentro de `backend/` (es una entrega histórica con otro alcance).
- Las herramientas del frontend (`.agents/`, `.claude/`, `.opencode/`, `.atl/`) no se copian a la raíz para no pisar las del backend; su OpenSpec y su KB quedan como referencia histórica en `frontend/docs/`. El OpenSpec activo sigue siendo el del backend.

### 2. Imagen del backend

- `python:3.12-alpine`, usuario `appuser` sin privilegios, `requirements.txt` con `--no-cache-dir`, `alembic.ini`, `app/`, `migrations/` y `seed.py` (el seed no corre al arrancar).
- `EXPOSE 8000`; `HEALTHCHECK` contra `http://127.0.0.1:8000/health/ready`; `CMD ["sh","-c","alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]`.
- **Alternativa descartada**: reutilizar `despliegue/Dockerfile` (requirements reducidos, sin auth/usuarios, app distinta).

### 3. Imagen del frontend y proxy same-origin

- `nginxinc/nginx-unprivileged:1.27-alpine` (sin privilegios, escucha 8080); `public/` a `/usr/share/nginx/html`; `default.conf.template` a `/etc/nginx/templates/`; `EXPOSE 8080`; healthcheck `/healthz`.
- **Alternativa descartada**: `nginx:1.27-alpine` en puerto 80 (más simple, pero master root). Se elige 8080 por consistencia con la postura sin privilegios; EasyPanel publica 8080.

```nginx
server {
  listen 8080;
  root /usr/share/nginx/html;
  index index.html;
  location / { try_files $uri $uri/ /index.html; }
  location /api/ {
    proxy_pass ${API_UPSTREAM}/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
  location = /healthz { return 200 "ok\n"; add_header Content-Type text/plain; }
}
```

- `API_UPSTREAM` se define como `esquema://host:puerto` sin barra final; la barra final de `proxy_pass` recorta el prefijo `/api/`. Ejemplos: `http://backend:8000` (compose) o la URL interna del servicio backend en EasyPanel.

### 4. Same-origin y cookies

- El navegador siempre llama `/api/...` en el origen del frontend; Nginx reenvía al backend. La cookie `access_token` (`Path=/`, `SameSite=Lax`, `HttpOnly`) queda almacenada para el origen del frontend y se envía en las peticiones a `/api`. Esto evita problemas de cookies cross-site y hace innecesario CORS en producción.
- Abrir por `file://` deja de ser soportado (Origin `null`, cookie no confiable). El desarrollo local usa `http://localhost:8080`.
- **Alternativa descartada**: llamadas directas cross-origin a la API (requeriría `SameSite=None; Secure`, HTTPS en todo el entorno y CORS con credenciales).

### 5. CORS

- `CORS_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"` en `Settings`; propiedad `cors_origins` que separa y limpia la lista.
- `CORSMiddleware` después de `app = FastAPI(...)`: `allow_origins=settings.cors_origins`, `allow_credentials=True`, `allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"]`, `allow_headers=["Content-Type"]`.
- Nunca `"*"` con credenciales. En producción el same-origin no necesita CORS, pero se puede sumar la URL pública del frontend para herramientas/acceso directo.
- Documentar `CORS_ORIGINS` en `backend/env.example` y en el README.

### 6. Gaps de API necesarios para el frontend

- **`GET /clientes` (VENDEDOR/ADMIN, paginado)**: sin este endpoint el frontend no puede poblar la tabla de clientes ni el selector de venta. Implementar `ClienteRepository.listar_con_perfil(offset, limit)` con `joinedload(Cliente.perfil)`; `service.listar(uow, page, size)` con `count()`, `validar_pagina` y `construir_pagina`; y la ruta en `router_staff`. No usar `get_all()` porque no precarga `perfil` (lazy load async → `MissingGreenlet`).
- **`cliente_nombre` en `VentaRead`**: `VentaRepository.listar` agrega `joinedload(Venta.cliente)` y arma el DTO; así el historial y `/mis-ventas` muestran el nombre sin N+1. **Alternativa descartada**: N llamadas a `GET /ventas/{id}` (N+1 HTTP).
- Ambos son cambios de comportamiento de la API: llevan delta specs y pruebas `.http` (regla del proyecto: sin pytest).

### 7. Capa API del frontend

- `js/api.js`: `API_BASE = '/api'`; `apiFetch(ruta, opciones)` con `credentials: 'include'`, `Content-Type: application/json`, parseo JSON y `ApiError` (`status`, `detail`, `retryAfter`); wrappers de auth, catálogo, libros, clientes, ventas e historial.
- `js/mapeo.js`: `aModeloLibro/Cliente/Venta` y `aDtoLibro/Cliente/Venta`. Se conserva el modelo interno actual: ids string con prefijo (`li-1`, `cl-1`, `ed-1`, `ge-1`, `au-1`, `V-0001`), importes `number`, `nombreCompleto`, `clienteNombre`, camelCase. Conversiones: `Decimal` string → `Number()`, ids en ambos sentidos, `Pagina.items` desenvuelto, `V-####` ↔ entero.
- `js/storage.js`: solo preferencias (`libreria.preferencias.tema`, `libreria.preferencias.sidebar`); se eliminan las claves de dominio y la validación de arrays.
- `js/data.js`: solo `PORTADAS_IDS_CONOCIDOS`, tapas/resolución de portada y helpers de formato; se eliminan los arrays de editoriales/géneros/autores/libros/clientes/ventas.
- `js/app.js`: `iniciarPersistencia()` se reemplaza por `cargarDatosIniciales()` (en paralelo `GET /libros?size=100`, `/editoriales?size=100`, `/generos?size=100`, `/autores?size=100` y, según rol, clientes/ventas). Handlers `async`, botones deshabilitados mientras se guarda, refresco de los listados afectados después de cada mutación; se conservan las funciones de render y la accesibilidad.
- **Alternativas descartadas**: mantener el seed local como fallback (dos fuentes de verdad) y usar un framework (regla del proyecto).

### 8. UI de sesión

- Bloque `#sesion` en la sidebar (sin sexta vista):
  - Sin sesión: `#form-login` (`email`, `password`), `#login-errores`, `#login-mensaje`.
  - Con sesión: `#sesion-usuario` (nombre/email), `#sesion-roles`, `#btn-logout`, `#btn-cambiar-password` y un `#form-cambiar-password` colapsable (`password_actual`, `password_nueva`).
- `js/sesion.js`: `iniciarSesion`, `cerrarSesion`, `refrescarSesion` (`GET /auth/yo`), `puede(rol)`, `actualizarUI`, `manejarErrorSesion`. Al cargar se consulta `/auth/yo`; 401 → anónimo. Si el login devuelve `debe_cambiar_password`, se muestra el formulario y un aviso; las operaciones protegidas responderán 403 hasta cambiarla.
- Visibilidad: `data-requiere-rol="ADMIN"` en el alta de libro; `data-requiere-rol="VENDEDOR ADMIN"` en clientes/ventas; se ocultan las vistas/acciones no permitidas. CLIENTE usa `/mis-ventas` en Historial; anónimo ve Catálogo y Libros en modo lectura y un aviso de login en las vistas protegidas.
- **Alternativas descartadas**: modal (focus trap y complejidad) y sexta vista (cambia más de lo necesario el contrato de 5 vistas).

### 9. Errores, carga y accesibilidad

- `ApiError` → mensajes: 401 → anónimo + aviso de login; 403 → "No tenés permiso" o cambio de contraseña; 404 → "No encontrado"; 409 → `detail` del backend (ISBN/stock/duplicado); 422 → errores de campo formateados; 429 → usar `Retry-After`; red → "No se pudo conectar con el servidor. Reintentá.".
- `#error-conexion` (`role="alert"`) con botón "Reintentar"; regiones de carga con `aria-busy="true"`; se conserva `#catalogo-resultados` (`aria-live="polite"`); se agrega `aria-live="polite"` a `#venta-total`; se mantienen los contenedores `role="alert"`/`role="status"`, el foco al primer campo inválido y el uso de `textContent`/`createElement`.
- Botones deshabilitados y texto "Guardando…" mientras la petición está en curso; se evita el doble envío.

### 10. Local vs. producción

- **Local**: `docker-compose.yml` con `db` (PostgreSQL 16/17), `backend` (build `backend/`, `POSTGRES_*`, `JWT_SECRET`, `COOKIE_SECURE=false`, `CORS_ORIGINS=http://localhost:8080`) y `frontend` (build `frontend/`, `API_UPSTREAM=http://backend:8000`, `8080:8080`), healthchecks y `depends_on`. El seed se ejecuta a mano.
- **EasyPanel**: dos servicios del monorepo: backend (Dockerfile `backend/`, `POSTGRES_*`, `JWT_SECRET`, `COOKIE_SECURE=true` si hay HTTPS, `CORS_ORIGINS` con la URL del frontend) y frontend (Dockerfile `frontend/`, `API_UPSTREAM` interno, exponer 8080). Sin compose en producción. Se usa la base existente o una nueva; `alembic upgrade head` corre al arrancar y `python seed.py` se ejecuta una vez.
- **Alternativa descartada**: un solo contenedor con Nginx + uvicorn (más difícil de escalar/observar; dos imágenes encajan mejor con EasyPanel).

## Risks / Trade-offs

- **`file://` deja de funcionar** → documentar `http://localhost:8080` y el compose; si se abre mal, mostrar el aviso de servidor requerido.
- **Cookies cross-origin** → same-origin `/api` en producción y local; CORS solo con orígenes explícitos; nunca `"*"` con credenciales.
- **`precio`/`total` como string** → `Number()` en el mapeo; pruebas manuales con los importes del seed.
- **IDs con prefijo vs. enteros** → helpers `idConPrefijo`/`idSinPrefijo` y mapeo centralizado; probar alta de libro/cliente/venta.
- **Listados paginados (máx. 100)** → `size=100` para los catálogos del TP; si `total > items.length`, mostrar un aviso y dejar "cargar más" como follow-up.
- **`GET /clientes` y `cliente_nombre` tocan la API** → governance MEDIO/ALTO; pruebas `.http`, revisión de repositorios y `joinedload` para evitar `MissingGreenlet`/N+1.
- **Nginx sin privilegios en 8080** → documentar el puerto en EasyPanel; healthcheck `/healthz`; si se necesita 80, cambiar a `nginx:alpine` (trade-off de seguridad).
- **Datos de `localStorage` se descartan** → aviso en el README; el seed del backend es la fuente de demo; no hay migración automática.
- **`nuevo@example.com` con `debe_cambiar_password`** → flujo de cambio de contraseña en la UI y mensaje 403 claro.

## Migration Plan

1. Crear una rama; mover `parcial/` → `backend/` y el runtime del frontend → `frontend/public/` con `git mv`; conservar `despliegue/`.
2. Implementar los cambios de API (CORS, `GET /clientes`, `cliente_nombre`) y los `.http`; correr `alembic upgrade head` + `python seed.py`.
3. Crear Dockerfiles/Nginx/compose; levantar `docker compose up --build`; verificar login, catálogo, alta de libro/cliente, venta, stock e historial.
4. Integrar el frontend (api/mapeo/sesión/app); verificar 401/403/409/422/429, roles y `debe_cambiar_password`; probar 320 px, 1280 px y teclado.
5. Actualizar README/CHANGES/env.example; validar `openspec validate --all --strict`.
6. Desplegar en EasyPanel: backend y frontend como servicios separados; `API_UPSTREAM` interno; `CORS_ORIGINS` con la URL pública del frontend; `COOKIE_SECURE=true` con HTTPS; ejecutar el seed una vez.
7. Rollback: el servicio anterior de `despliegue/` sigue disponible; la base es externa (sin pérdida de datos); revertir el commit del monorepo y volver a la imagen/URL anterior del frontend. El frontend estático anterior puede seguir sirviéndose mientras se valida el nuevo.

## Open Questions

- URL pública exacta del frontend en EasyPanel: se completa al desplegar; solo afecta `CORS_ORIGINS` y la documentación, no el diseño ni las tareas.
- ¿Conservar la KB/OpenSpec históricos del frontend en `frontend/docs/` o dejarlos en el repo original? El diseño propone `frontend/docs/`; se puede ajustar sin cambiar el código.
