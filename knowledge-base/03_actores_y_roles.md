# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| Anónimo ("Cualquiera") | Visitante sin sesión | Ve el catálogo público, se registra (`/auth/registro`), inicia sesión |
| CLIENTE | Persona que se registró sola en la web | Consulta sus compras (`/mis-ventas`, y su propia venta en `/ventas/{id}`) |
| VENDEDOR | Personal de mostrador | Registra ventas, atiende clientes (alta/consulta/PATCH, perfil, ventas del cliente) |
| ADMIN | Administrador | Mantiene catálogo, repone stock, administra personal y roles, ve eventos de seguridad y todas las ventas |
| SISTEMA | **No es un usuario**: es un *texto* en `evento_seguridad.actor` | Actor de la línea "Carga de los datos iniciales" del seed |

Roles válidos (CHECK en la base): `ADMIN`, `VENDEDOR`, `CLIENTE`. `usuario` **no tiene columna `rol`**: los roles viven en `asignacion_rol` (ver `04`).

## Roles vigentes

Una asignación es **vigente** si no fue revocada (`revocada_en IS NULL`) y no venció (`vence_en` nulo o futuro). Revocar escribe `revocada_en`; la fila **nunca se borra** (historial). Reasignar un rol vencido cierra la fila anterior y abre una nueva. El vencimiento llega con zona horaria y en el futuro; sin zona o en el pasado → **422** (no 409).

## RBAC — Matriz de permisos

(Fuente: tabla "Endpoints de referencia", págs. 16–18, confirmada; ver `11`.)

| Recurso / operación | Anónimo | CLIENTE | VENDEDOR | ADMIN |
|---|---|---|---|---|
| `GET /libros`, `/libros/{id}`, `/editoriales`, `/generos` | sí | sí | sí | sí |
| `/health/live`, `/health/ready`, `/auth/registro`, `/auth/login`, `/auth/logout` | sí | sí | sí | sí |
| `/auth/yo`, `/auth/cambiar-password` | no (401) | sí | sí | sí |
| `GET /{editoriales,generos,autores}/{id}/libros` (abiertos) | sí | sí | sí | sí |
| Altas de editoriales, géneros, autores; PATCH de editoriales y autores (no hay PATCH de géneros) | no | no | no | sí |
| `POST /libros`, `PATCH /libros/{id}`, `DELETE /libros/{id}`, `POST /libros/{id}/reponer`, `GET /libros/{id}/movimientos` | no | no | no (403) | sí |
| `/usuarios` (alta de personal), `/usuarios/{id}/roles` (asignar/listar/revocar), `GET /eventos` | no | no | no | sí |
| `/clientes` (alta, GET/PATCH `{id}`, `{id}/perfil`, `{id}/ventas`) | no | no | sí | sí |
| `POST /ventas`, `GET /ventas` | no | no | sí | sí |
| `GET /ventas/{id}` | no | sólo la propia | sí | sí |
| `GET /mis-ventas` | no | sí (sólo las suyas) | sí | sí |

Notas:
- **401** = sin sesión / token inválido o vencido / usuario inexistente o inactivo. **403** = autenticado pero sin permiso, **o** con cambio de contraseña pendiente.
- `GET /ventas/{id}` **no lleva `requiere_rol`**: la decisión la toma el servicio (primero quién es y qué relación tiene con la venta → 403 si no es personal ni dueño; recién después qué se devuelve).
- "Lo propio" (RN-14) sólo pide estar autenticado.

## Rutas públicas (grupo abierto)

`GET /health/live`, `GET /health/ready`, `POST /auth/registro`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/yo`*, `POST /auth/cambiar-password`*, `GET /libros`, `GET /libros/{id}`, `GET /editoriales`, `GET /generos`, `GET /{editoriales,generos,autores}/{id}/libros`.

\* Están en el grupo abierto (no llevan el control de cambio obligatorio) pero requieren sesión (401 sin ella). Con cambio pendiente, el usuario **sólo** puede usar `/auth/*` y las rutas que no piden sesión (RN-06).

## Cambio obligatorio de contraseña

`usuario.debe_cambiar_password = true` (ej. `nuevo@example.com` del seed, o altas de personal con contraseña provisoria). Se resuelve con dos grupos de rutas en `main.py` (FastAPI suma dependencias y no las resta): el protegido lleva el control montado una sola vez. Tras `POST /auth/cambiar-password` la **misma cookie** sirve para las rutas protegidas (no se emite token nuevo).
