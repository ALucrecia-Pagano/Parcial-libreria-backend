# Proposal: CH-12 — Roles con vigencia, autoprotección, alta de personal y eventos de seguridad

## Why

Para completar el ciclo de autorización y auditoría del parcial (RN-03, RN-04, RN-05, RN-16), se requiere que los administradores gestionen el ciclo de vida del personal y de los roles con vigencia temporal, autoprotección estricta y registro auditable en `evento_seguridad`.

Específicamente:
1. **Alta de personal (`POST /usuarios`)**: un ADMIN crea un nuevo usuario con rol inicial y contraseña provisoria de hasta 72 bytes UTF-8 (`PasswordBcrypt`), marcando `debe_cambiar_password = True` (RN-06), asignando el rol con `otorgada_por = admin.id` y registrando el evento de auditoría en la misma transacción (RN-16).
2. **Historial de roles (`GET /usuarios/{id}/roles`)**: lista completa de asignaciones históricas, incluyendo las revocadas y vencidas (cátedra §4.9).
3. **Asignación de roles con vigencia (`POST /usuarios/{id}/roles`)**: asigna un rol con `vence_en` opcional (con zona horaria obligatoria y fecha futura; de lo contrario 422). Si ya existe una asignación abierta vigente del mismo rol, responde 409 (RN-03). Si existía una asignación abierta pero vencida, en el mismo UoW se cierra la anterior (`revocada_en = ahora`) y se abre la nueva con `otorgada_por = admin.id` y auditoría en `evento_seguridad` (RN-16).
4. **Revocación con autoprotección (`DELETE /usuarios/{id}/roles/{rol}`)**: revoca un rol estableciendo `revocada_en = ahora` sin borrar la fila. Aplica las dos reglas de autoprotección (RN-05): un administrador no puede revocarse su propio rol ADMIN (409), y no se puede revocar un rol ADMIN si con ello el sistema quedaría sin ningún administrador vigente (409). Registra auditoría en `evento_seguridad` (RN-16).
5. **Consulta de auditoría (`GET /eventos`)**: listado paginado (`page`, `size` entre 1 y 100; 422 si size > 100) de los eventos de seguridad ordenados cronológicamente de más reciente a más antiguo, reservado exclusivamente para ADMIN.

## What Changes

- **DTOs (`parcial/app/modules/usuarios/schemas.py`)**:
  - `UsuarioCreateAdminIn`: `email: EmailStr`, `nombre: str`, `password: PasswordBcrypt`, `rol: Literal["ADMIN", "VENDEDOR", "CLIENTE"]` (`extra="forbid"`).
  - `UsuarioAdminOut`: `id: int`, `email: str`, `nombre: str`, `activo: bool`, `debe_cambiar_password: bool` (`extra="forbid"`).
  - `AsignacionRolCreateIn`: `rol: Literal["ADMIN", "VENDEDOR", "CLIENTE"]`, `vence_en: datetime | None` con validación estricta de tzinfo y fecha futura (422 ante violaciones).
  - `AsignacionRolOut`: `id: int`, `usuario_id: int`, `rol: str`, `desde: datetime`, `vence_en: datetime | None`, `revocada_en: datetime | None`, `otorgada_por: int | None`.
  - `EventoSeguridadOut`: `id: int`, `cuando: datetime`, `actor: str`, `accion: str`.
- **Repositorios (`parcial/app/modules/usuarios/repository.py`)**:
  - En `AsignacionRolRepository`: métodos `obtener_asignaciones`, `obtener_abierta`, `contar_admins_vigentes`.
  - En `EventoSeguridadRepository`: métodos `contar`, `listar_recientes`.
- **Lógica de negocio (`parcial/app/modules/usuarios/service.py`)**:
  - `alta_personal`: hashea la contraseña provisoria fuera de la transacción; dentro de `async with uow:` crea el usuario con `debe_cambiar_password=True`, la asignación y el evento `Alta de personal`.
  - `listar_roles`: consulta todas las asignaciones del usuario (404 si el usuario no existe).
  - `asignar_rol`: valida existencia (404), verifica asignación abierta (409 si activa; si vencida, la cierra), crea la asignación y registra evento.
  - `revocar_rol`: valida existencia (404), existencia de rol activo (404), autoprotección de ADMIN propio (409), autoprotección de último ADMIN vigente (409), cierra con `revocada_en` y registra evento.
  - `listar_eventos`: paginación con `validar_pagina` y `construir_pagina`.
- **Rutas HTTP (`parcial/app/modules/usuarios/router.py`)**:
  - `router_admin`: endpoints `/usuarios`, `/usuarios/{id}/roles`, `/usuarios/{id}/roles/{rol}`, `/eventos`.
- **Verificación**:
  - `parcial/test/C-07_revocar_rol.http` y `parcial/test/C-08_autoproteccion.http` ejecutados contra PostgreSQL real y Uvicorn.

## Capabilities

### Modified Capabilities
- `autorizacion`: Alta de personal con contraseña provisoria, gestión de roles con vencimiento y revocación, autoprotección del administrador (RN-05) y consulta paginada de eventos de seguridad (RN-16).
