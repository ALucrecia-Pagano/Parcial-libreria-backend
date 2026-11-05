# Tasks

## 1. Contratos y traducción de errores

- [x] 1.1 Definir esquemas `RegistroClienteRequest` (con `PasswordBcrypt` y `extra="forbid"`), `RegistroClienteResponse` (sin `password_hash`) y `UsuarioYoResponse` en `parcial/app/modules/usuarios/schemas.py` y verificar que contratos rechacen campos extra.
- [x] 1.2 Registrar las traducciones para las restricciones de unicidad `uq_usuario_email` y `uq_cliente_email` en `parcial/app/core/errores.py` para mapear colisiones de base de datos a HTTP 409 con mensajes limpios.

## 2. Capa de acceso a datos y Unit of Work

- [x] 2.1 Agregar `self.clientes = BaseRepository(session, Cliente)` en `UsuariosUnitOfWork` (`parcial/app/modules/usuarios/unit_of_work.py`) para permitir persistencia de la ficha de cliente en la misma transacción del usuario.

## 3. Lógica de servicio y endpoints

- [x] 3.1 Implementar `UsuariosService.registrar_cliente` en `parcial/app/modules/usuarios/service.py` calculando el hash bcrypt antes de abrir el UoW y persistiendo `Usuario`, `AsignacionRol` (CLIENTE) y `Cliente` en un único bloque `async with uow:`.
- [x] 3.2 Implementar handlers `POST /auth/registro` y `POST /auth/logout` (invalidando cookie `access_token` con `Max-Age=0`) en `parcial/app/modules/usuarios/router.py`.
- [x] 3.3 Estructurar `GET /auth/yo` en router y servicio para exponer datos del usuario, roles vigentes en la base y roles del token (preparado para la dependencia `get_usuario_actual` de CH-10).

## 4. Pruebas y verificación con .http

- [x] 4.1 Crear la suite `parcial/test/C-02_registro.http` con casos 201, 409 (correo usuario duplicado), 409 (correo cliente duplicado), 422 (intento de asignar rol en payload), 422 (contraseña > 72 bytes) y 200 en logout sin sesión.
- [x] 4.2 Ejecutar `C-02_registro.http` contra uvicorn y PostgreSQL real, verificar ausencia de filas huérfanas o apropiación indebida de fichas de clientes y documentar la evidencia completa en `verify.md`.

## Workflow follow-up

- Mantener `CH-08` listo para integración final de `GET /auth/yo` cuando `CH-10` esté incorporado en la rama principal.

