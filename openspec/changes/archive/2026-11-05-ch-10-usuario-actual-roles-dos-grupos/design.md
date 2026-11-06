# Design: CH-10 — Usuario actual, roles y dos grupos de rutas

## Architectural Decisions

### D1: Exclusividad de la cookie `access_token`
Siguiendo las reglas duras (Regla 18 de `AGENTS.md`) y la cátedra §5.3, `get_usuario_actual` inspecciona únicamente `request.cookies.get("access_token")`. Se ignora y rechaza cualquier token que viaje en la cabecera `Authorization: Bearer ...`. Si la cookie no está presente, se responde HTTP 401 Unauthorized de forma inmediata.

### D2: Autorización en la base de datos en cada petición (RN-04)
El JWT emitido contiene roles únicamente como referencia informativa para interfaces de usuario (`roles_token`). La autorización real (`requiere_rol`) se consulta directamente contra la tabla `asignacion_rol` en la base de datos para el `usuario_id` en cada petición, filtrando por `revocada_en IS NULL` y `(vence_en IS NULL OR vence_en > ahora)`. Esto asegura que si a un usuario se le revoca un rol o vence su asignación, pierde el acceso de inmediato sin esperar a que expire su token o cookie.

### D3: Unificación de sesión por petición (Ejercicio 6, Cátedra §6.7)
Todas las dependencias del ciclo de vida de la petición (`get_usuario_actual`, `requiere_rol` y los constructores de UoW) reciben la misma `AsyncSession` inyectada mediante `Depends(get_session)`. FastAPI cachea por defecto el resultado de las dependencias (`use_cache=True`), por lo que una petición protegida consume una única conexión del pool.

### D4: Control de cambio obligatorio de contraseña montado a nivel de grupo (RN-06, Cátedra §5.10)
En lugar de repetir la verificación en cada handler, se monta la dependencia `exigir_password_al_dia` en el `APIRouter` del grupo protegido. Si `usuario.debe_cambiar_password == True`, responde HTTP 403 Forbidden ("Debe cambiar su contraseña antes de operar en el sistema"). Los endpoints del grupo abierto (incluyendo `/auth/cambiar-password`) no pasan por esta guarda, permitiendo al usuario desbloquear su cuenta.

### D5: Reestructuración de `main.py` en dos grupos
Se crean dos enrutadores principales:
1. `grupo_abierto`: monta `health`, `auth` y los endpoints públicos de lectura de catálogo.
2. `grupo_protegido`: configurado con `dependencies=[Depends(exigir_password_al_dia)]`, monta:
   - Rutas de ADMIN con `dependencies=[Depends(requiere_rol("ADMIN"))]`.
   - Rutas de personal (staff) con `dependencies=[Depends(requiere_rol("VENDEDOR", "ADMIN"))]`.
   - Rutas protegidas sin rol fijo (`GET /ventas/{id}` y `GET /mis-ventas`).
Para máxima compatibilidad con las ramas de catálogo de los compañeros (CH-04/CH-05), `main.py` detecta si los módulos exponen `router_abierto` y `router_admin`, o segrega dinámicamente las rutas por método HTTP (`GET` abierto vs escrituras admin).

## Component Structure

```
parcial/app/
├── core/
│   └── dependencies.py         <-- get_usuario_actual, requiere_rol, exigir_password_al_dia
├── modules/
│   └── usuarios/
│       ├── router.py           <-- GET /auth/yo usa get_usuario_actual
│       └── schemas.py          <-- UsuarioYoOut incluye debe_cambiar_password
└── main.py                     <-- grupo_abierto + grupo_protegido
```
