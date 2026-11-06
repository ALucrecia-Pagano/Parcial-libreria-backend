# Proposal: CH-11 — Cambiar contraseña y cambio obligatorio

## Why

Para cumplir con la política de seguridad y cambio obligatorio de contraseñas (RN-06), el sistema debe permitir a cualquier usuario autenticado —incluyendo aquellos con la marca `debe_cambiar_password = True`— actualizar su contraseña mediante `POST /auth/cambiar-password`. Se debe verificar la contraseña actual antes de abrir la transacción, validar que ninguna de las contraseñas exceda 72 bytes en UTF-8 (cátedra §5.4), actualizar el hash y levantar la marca de cambio obligatorio junto con el registro auditable en `evento_seguridad` en una única transacción atómica (RN-16). La sesión activa debe permanecer válida inmediatamente después del cambio sin requerir reautenticación (DD-30).

## What Changes

- **DTOs de entrada y salida (`parcial/app/modules/usuarios/schemas.py`)**:
  - `CambiarPasswordIn`: con `extra="forbid"`, recibe `password_actual` y `password_nueva`, ambas validadas mediante `PasswordBcrypt` (máximo 72 bytes UTF-8; rechazo 422 ante desbordes).
  - `CambiarPasswordOut`: respuesta confirmando la actualización exitosa.
- **Lógica de servicio (`parcial/app/modules/usuarios/service.py`)**:
  - `cambiar_password`: verifica `password_actual` contra el hash almacenado fuera de la transacción mediante bcrypt en worker thread. Si la contraseña actual no coincide, responde HTTP 401 Unauthorized (DD-30).
  - Calcula el nuevo hash bcrypt fuera de la transacción.
  - En un único bloque `async with uow:` (RN-16): actualiza `password_hash`, establece `debe_cambiar_password = False` e inserta la fila de auditoría en `evento_seguridad` con `actor = usuario.email` y `accion = "Cambio de contraseña"`.
- **Ruta HTTP (`parcial/app/modules/usuarios/router.py`)**:
  - `POST /auth/cambiar-password` en `router_abierto`, inyectando `UsuarioActualDep` (401 si no hay sesión). Al pertenecer al grupo abierto, no está bloqueada por `exigir_password_al_dia`, permitiendo desbloquear la cuenta.
- **Verificación**:
  - Caso `parcial/test/C-09_cambio_obligatorio.http` ejecutado contra PostgreSQL real.

## Capabilities

### Modified Capabilities
- `autorizacion`: Incorpora la operación de cambio de contraseña, desbloqueo de cuentas restringidas por cambio obligatorio y auditoría transaccional de eventos de seguridad.

## Impact

- `parcial/app/modules/usuarios/schemas.py`: incorporación de `CambiarPasswordIn` y `CambiarPasswordOut`.
- `parcial/app/modules/usuarios/service.py`: método `cambiar_password`.
- `parcial/app/modules/usuarios/router.py`: endpoint `POST /auth/cambiar-password`.
- `parcial/test/C-09_cambio_obligatorio.http`: suite de pruebas ejecutada.
