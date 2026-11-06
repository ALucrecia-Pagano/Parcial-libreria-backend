# Design: CH-12 — Roles con vigencia, autoprotección, alta de personal y eventos de seguridad

## Contexto y Restricciones Arquitectónicas

1. **Autoprotección (RN-05)**:
   - Un administrador no puede revocarse su propio rol `ADMIN`.
   - El sistema nunca puede quedar sin administradores vigentes (si al revocar el rol `ADMIN` a un usuario el conteo de administradores vigentes desciende a 0, debe rechazarse con 409).
   - El orden de evaluación en `revocar_rol` debe contemplar:
     a) Si `admins_vigentes <= 1` y el usuario a revocar tiene el rol `ADMIN` vigente, rechazar con 409: `"No se puede revocar el rol: no pueden quedar cero administradores vigentes en el sistema"`.
     b) Si `usuario_id == admin_actual.id` y `rol == "ADMIN"`, rechazar con 409: `"Un administrador no puede revocarse su propio rol ADMIN"`.
2. **Ciclo de vida y vigencia de roles (RN-03, RN-04, RN-16)**:
   - La tabla `asignacion_rol` mantiene el historial completo; la revocación marca `revocada_en = datetime.now(timezone.utc)` y nunca borra físicamente la fila.
   - En `POST /usuarios/{id}/roles`: si existe una asignación con `revocada_en IS NULL`:
     - Si está vigente (`vence_en IS NULL` o `vence_en > ahora`), conflicto 409 (`"El usuario ya tiene ese rol activo asignado"`).
     - Si ha vencido (`vence_en <= ahora`), se cierra dicha asignación (`revocada_en = ahora`), se ejecuta `flush()`, y se procede a crear la nueva asignación.
3. **Validación estricta de `vence_en`**:
   - `vence_en` es opcional, pero si se envía debe ser timezone-aware (`tzinfo is not None`) y estrictamente mayor a `datetime.now(timezone.utc)`. En caso de ser naive o fecha pasada, el validador de Pydantic lanza `ValueError` produciendo una respuesta HTTP 422 Unprocessable Entity.
4. **Alta de personal (`POST /usuarios`)**:
   - Contraseña provisoria de hasta 72 bytes UTF-8 (`PasswordBcrypt`). Se calcula el hash fuera de la transacción con `hashear_password` (cátedra §5.6).
   - En un solo bloque `async with uow:` se crea el `Usuario` (`debe_cambiar_password = True`), se inserta en `asignacion_rol` con `otorgada_por = admin.id`, y se inserta en `evento_seguridad` con `actor = admin.email` y `accion = "Alta de personal"`.
5. **Consulta de eventos (`GET /eventos`)**:
   - Endpoint protegido para ADMIN que utiliza `PaginacionDep` (`page`, `size` entre 1 y 100).
   - Ordena por `cuando.desc()`, `id.desc()`.
   - Utiliza `validar_pagina` y `construir_pagina`.

## Estructura de Capas

- `schemas.py`: `UsuarioCreateAdminIn`, `UsuarioAdminOut`, `AsignacionRolCreateIn`, `AsignacionRolOut`, `EventoSeguridadOut`.
- `repository.py`:
  - `AsignacionRolRepository.obtener_asignaciones(usuario_id: int) -> list[AsignacionRol]`
  - `AsignacionRolRepository.obtener_abierta(usuario_id: int, rol: str) -> AsignacionRol | None`
  - `AsignacionRolRepository.contar_admins_vigentes() -> int`
  - `EventoSeguridadRepository.contar() -> int`
  - `EventoSeguridadRepository.listar_recientes(offset: int, limit: int) -> list[EventoSeguridad]`
- `service.py`:
  - `alta_personal(uow, admin, datos)`
  - `listar_roles(uow, usuario_id)`
  - `asignar_rol(uow, admin, usuario_id, datos)`
  - `revocar_rol(uow, admin, usuario_id, rol)`
  - `listar_eventos(uow, params)`
- `router.py`:
  - `router_admin = APIRouter(tags=["usuarios"])`
  - `POST /usuarios`
  - `GET /usuarios/{id}/roles`
  - `POST /usuarios/{id}/roles`
  - `DELETE /usuarios/{id}/roles/{rol}`
  - `GET /eventos` (tag: "eventos")
