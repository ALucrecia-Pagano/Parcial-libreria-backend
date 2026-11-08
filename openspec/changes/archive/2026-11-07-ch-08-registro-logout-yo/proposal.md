# Proposal

## Why

El sistema de la librería requiere permitir a nuevos clientes registrarse de forma autónoma en la plataforma (`POST /auth/registro`), garantizando la creación atómica del usuario, su asignación inicial de rol CLIENTE y su ficha asociada de cliente en una única transacción de base de datos (RN-02), sin fugas de datos sensibles ni inconsistencias de unicidad. Asimismo, es necesario proveer un mecanismo explícito de cierre de sesión (`POST /auth/logout`) que invalide la cookie HttpOnly en el cliente incluso ante llamadas sin sesión previa (DD-18), y definir la consulta de identidad (`GET /auth/yo`) que expone el usuario autenticado junto a la comparativa de sus roles vigentes en la base frente a los declarados en el token.

## What Changes

- **Registro atómico de clientes (`POST /auth/registro`)**:
  - Esquema de entrada estricto con `extra="forbid"` (`RegistroClienteRequest`), validando contraseña con `PasswordBcrypt` (máximo 72 bytes UTF-8) y prohibiendo campos arbitrarios como asignación de roles.
  - Hashing de contraseña ejecutado fuera de la transacción de base de datos para no retener conexiones del pool.
  - Creación transaccional atómica en un único bloque `async with uow:` de tres entidades vinculadas: `usuario`, `asignacion_rol` (rol CLIENTE) y `cliente` (asociado a `usuario_id`). Si falla cualquiera de las tres operaciones, se produce un rollback completo.
  - Manejo de colisiones de unicidad mediante captura de `IntegrityError` (sin consulta previa, RN-01/RN-15):
    - Colisión en `uq_usuario_email` -> HTTP 409 con mensaje `"El correo ya se encuentra registrado por un usuario"`.
    - Colisión en `uq_cliente_email` -> HTTP 409 con mensaje `"El correo ya pertenece a un cliente existente"`, impidiendo la apropiación de fichas ajenas y evitando registros huérfanos.
  - Respuesta HTTP 201 Created con esquema `RegistroClienteResponse` que expone los datos creados sin filtrar `password_hash`.
- **Cierre de sesión (`POST /auth/logout`)**:
  - Endpoint accesible públicamente que responde siempre HTTP 200, incluso sin cookie o sesión activa previa (DD-18).
  - Limpieza de la cookie HttpOnly `access_token` mediante cabecera `Set-Cookie` con `Max-Age=0`.
- **Identidad del usuario autenticado (`GET /auth/yo`)**:
  - Definición del contrato y endpoint que devuelve el usuario autenticado, los roles vigentes leídos de la base de datos y los roles codificados en el token JWT. (Nota de alcance: la verificación de identidad dependerá de `get_usuario_actual` de CH-10).
- **Extensión de Unit of Work y Errores**:
  - Inclusión de repositorio genérico `BaseRepository[Cliente]` en `UsuariosUnitOfWork` para operar la tabla `cliente` sin depender de módulos comerciales.
  - Traducción de las restricciones de unicidad de email de usuario y cliente en el módulo central de errores.

## Capabilities

### New Capabilities

*(Ninguna, se extiende la capacidad existente de autenticación y sesión).*

### Modified Capabilities

- `autenticacion-y-sesion`: Incorpora los requerimientos de auto-registro atómico de clientes con rol por defecto y ficha vinculada, cierre de sesión idempotente con limpieza de cookie y consulta de identidad del usuario autenticado.

## Impact

- **Código afectado**:
  - `parcial/app/modules/usuarios/schemas.py`: Nuevos contratos `RegistroClienteRequest`, `RegistroClienteResponse`, `UsuarioYoResponse`.
  - `parcial/app/modules/usuarios/unit_of_work.py`: Soporte para gestión de clientes dentro del UoW de usuarios.
  - `parcial/app/modules/usuarios/service.py`: Métodos `registrar_cliente` y `obtener_yo`.
  - `parcial/app/modules/usuarios/router.py`: Endpoints `POST /auth/registro`, `POST /auth/logout` y `GET /auth/yo`.
  - `parcial/app/core/errores.py`: Registro de traducción para `uq_usuario_email` y `uq_cliente_email`.
- **Pruebas y verificación**:
  - Creación de suite `parcial/test/C-02_registro.http` cubriendo casos 201, colisión 409 usuario, colisión 409 cliente existente, rechazo 422 por rol en payload, rechazo 422 por clave > 72 bytes y logout sin sesión (200).
