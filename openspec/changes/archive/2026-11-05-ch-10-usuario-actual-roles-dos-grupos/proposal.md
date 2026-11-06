# Proposal: CH-10 — Usuario actual, roles y dos grupos de rutas

## Why

Para implementar el control de acceso y autorización del sistema de la librería, se requiere conocer quién realiza cada petición, qué roles vigentes posee en la base de datos (RN-04) y aplicar las políticas de acceso según el tipo de recurso (abierto vs protegido). Además, se debe restringir a los usuarios que tengan el cambio obligatorio de contraseña pendiente (`debe_cambiar_password = True`), bloqueando su acceso a los recursos protegidos con HTTP 403 (RN-06), y unificar la sesión de base de datos entre la capa de dependencias y el Unit of Work para optimizar el pool de conexiones consumiendo una única conexión por petición (Ejercicio 6).

## What Changes

- **Dependencias de autenticación y autorización (`parcial/app/core/dependencies.py`)**:
  - `get_usuario_actual`: extrae el token exclusivamente de la cookie `access_token` (rechazando cabeceras `Authorization`), valida su firma y expiración, obtiene el usuario de la base con la misma sesión inyectada (`Depends(get_session)`), y responde `401 Unauthorized` si falta la cookie, el token es inválido o el usuario no existe o está inactivo (`activo == False`).
  - `requiere_rol(*roles)`: consulta en cada petición los roles vigentes en `asignacion_rol` (`revocada_en IS NULL` y `(vence_en IS NULL OR vence_en > ahora)`) (RN-04) usando la misma sesión compartida. Si el usuario no posee ninguno de los roles requeridos, responde `403 Forbidden`.
  - `exigir_password_al_dia`: dependencia montada a nivel de grupo protegido que valida `usuario.debe_cambiar_password`; si es `True`, responde `403 Forbidden` (RN-06).
  - Unificación de sesión: todas las dependencias consumen `Depends(get_session)` asegurando una sola conexión del pool por petición.
- **Reestructuración de rutas en `parcial/app/main.py`**:
  - Grupo abierto: salud (`/health/*`), autenticación (`/auth/*`), y endpoints públicos de catálogo (`GET /libros...`, `GET /editoriales`, `GET /generos`, `GET /{x}/{id}/libros`).
  - Grupo protegido: todas las rutas administrativas y de personal (`/usuarios`, `/eventos`, escrituras de catálogo, `/clientes`, `/ventas`, `/mis-ventas`), con `exigir_password_al_dia` montado una sola vez a nivel del grupo protegido.
  - Guardas por rol: los routers de administrador se montan con `requiere_rol("ADMIN")`, los routers de personal con `requiere_rol("VENDEDOR", "ADMIN")`, y las rutas de ventas accesibles por dueño o personal (`GET /ventas/{id}` y `GET /mis-ventas`) se montan en el grupo protegido sin `requiere_rol` a nivel de router.
- **Cierre de la tarea `/auth/yo` de CH-08**:
  - Inyección de `get_usuario_actual` en el endpoint `GET /auth/yo`, exponiendo el usuario activo, roles vigentes en base y roles contenidos en el token.
- **Pruebas HTTP**:
  - `parcial/test/C-01_param_no_entero.http` (parámetros no enteros con sesión responden 422).
  - `parcial/test/C-06_401_vs_403.http` (diferenciación estricta de 401 vs 403 y usuario inactivo).
  - Actualización de `parcial/test/C-03_cookie.http` (casos 401 sin cookie y con Bearer).

## Capabilities

### New Capabilities
- `autorizacion`: Autenticación por cookie exclusiva, verificación de vigencia de roles en base de datos en cada petición, bloqueo por cambio obligatorio de contraseña y montaje estructurado en grupo abierto y grupo protegido.

## Impact

- `parcial/app/core/dependencies.py`: nuevo archivo con dependencias y tipos de autorización.
- `parcial/app/main.py`: reestructuración en dos grupos de rutas (`grupo_abierto` y `grupo_protegido`).
- `parcial/app/modules/usuarios/router.py`: endpoint `/auth/yo` actualizado para usar `get_usuario_actual`.
- `parcial/app/modules/usuarios/schemas.py`: `UsuarioYoOut` incluye `debe_cambiar_password`.
- `parcial/test/C-03_cookie.http`: casos complementarios 401.
