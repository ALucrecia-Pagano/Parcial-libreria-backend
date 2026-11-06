# Tasks

## 1. Core de Seguridad y Ciclo de Vida

- [x] 1.1 Implementar `parcial/app/core/security.py` con `hashear_password` y `verificar_password` delegando a `bcrypt` mediante `asyncio.to_thread` y semáforo de concurrencia, tipo reusable `PasswordBcrypt` (validación de máximo 72 bytes en UTF-8 con rechazo 422), y funciones `crear_token` / `decodificar_token` con PyJWT (`sub`, `exp`, `roles`).
- [x] 1.2 Actualizar el `lifespan` en `parcial/app/main.py` para calcular el `hash_ficticio` al inicio de la aplicación y guardarlo en `app.state.hash_ficticio`.

## 2. Repositorios y Unit of Work de Usuarios

- [x] 2.1 Implementar `parcial/app/modules/usuarios/repository.py` con `UsuarioRepository` (hereda de `BaseRepository[Usuario]` con búsqueda `get_by_email`).
- [x] 2.2 Agregar en `parcial/app/modules/usuarios/repository.py` los repositorios `AsignacionRolRepository` (con consulta `roles_vigentes(usuario_id)` que filtre `revocada_en IS NULL` y `vence_en IS NULL OR vence_en > ahora`) y `EventoSeguridadRepository`.
- [x] 2.3 Implementar `parcial/app/modules/usuarios/unit_of_work.py` con `UsuariosUnitOfWork` que componga dichos repositorios bajo una misma sesión transaccional.

## 3. Esquemas, Servicio y Router de Autenticación

- [x] 3.1 Definir en `parcial/app/modules/usuarios/schemas.py` los esquemas `LoginIn` (`email`, `password: PasswordBcrypt`, `extra="forbid"`) y `LoginOut` (`mensaje`, `debe_cambiar_password`, `expira_en_segundos`), garantizando la ausencia de campos de token en la respuesta.
- [x] 3.2 Implementar en `parcial/app/modules/usuarios/service.py` el método `login`: búsqueda de usuario, verificación contra `hash_ficticio` ante inexistencia, verificación de contraseña fuera de la transacción de base de datos, rechazo 401 unificado ante credenciales erróneas o usuario inactivo, consulta de roles vigentes y generación de token.
- [x] 3.3 Implementar en `parcial/app/modules/usuarios/router.py` el `router_abierto` con prefijo `/auth` y endpoint `POST /auth/login` que setee la cookie `access_token` (`HttpOnly`, `SameSite=Lax`, `Max-Age`, `Secure`), e incluirlo en `parcial/app/main.py`.

## 4. Casos de Prueba y Verificación

- [x] 4.1 Crear `parcial/test/C-03_cookie.http` y verificar que el login devuelva 200, configure la cookie `access_token` con `HttpOnly` y `SameSite=Lax`, y el cuerpo no contenga ningún token.
- [x] 4.2 Crear `parcial/test/C-04_anti_enumeracion.http` y verificar que correo existente con contraseña errónea y correo inexistente devuelvan 401 con idéntico cuerpo y tiempo comparable, y que contraseñas mayores a 72 bytes respondan con 422.
