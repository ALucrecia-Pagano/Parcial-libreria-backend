# Design: CH-11 — Cambiar contraseña y cambio obligatorio

## Architectural Decisions

### D1: Hashing y verificación fuera de la transacción (Cátedra §5.6, §6.7)
Las llamadas a bcrypt (`verificar_password` de la actual y `hashear_password` de la nueva) son intensivas en CPU y asíncronas vía worker threads. Se ejecutan estrictamente ANTES de abrir el bloque `async with uow:`, para no retener conexiones del pool de la base de datos mientras se calculan los algoritmos criptográficos.

### D2: Contraseña actual errónea responde 401 Unauthorized (DD-30)
Siguiendo la decisión de diseño DD-30 confirmada en `CHANGES.md`, si la `password_actual` no coincide con el hash del usuario, se responde HTTP 401 Unauthorized (mismo criterio que el login) y no 422.

### D3: Atomicidad de la actualización y auditoría (RN-16)
La actualización de `usuario.password_hash`, la desactivación de `usuario.debe_cambiar_password = False` y la inserción del registro en `evento_seguridad` se efectúan dentro de un único bloque `async with uow:`. Si ocurre cualquier fallo, la transacción realiza rollback completo, garantizando que no se modifique la clave sin dejar registro auditable.

### D4: Continuidad de sesión sin reautenticación (RN-06, C-09)
La cookie `access_token` vigente en el cliente no se invalida ni se emite un nuevo token. Dado que `exigir_password_al_dia` consulta el estado del usuario en cada petición, al quedar `debe_cambiar_password = False` en la base de datos, el usuario accede de inmediato a las rutas protegidas con su misma cookie.

## Component Structure

```
POST /auth/cambiar-password
      │
      ▼
1. UsuarioActualDep (valida cookie access_token, 401 si falta)
      │
      ▼
2. UsuariosService.cambiar_password:
   ├── verificar_password(actual, hash_anterior) --> 401 si falla (DD-30)
   ├── hashear_password(nueva)
   └── async with uow:
         ├── uow.usuarios.add(usuario_actualizado)
         └── uow.eventos.add(EventoSeguridad("Cambio de contraseña"))
```
