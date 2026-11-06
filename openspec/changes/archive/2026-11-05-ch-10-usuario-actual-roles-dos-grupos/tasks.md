# Tasks: CH-10 — Usuario actual, roles y dos grupos de rutas

- [x] Crear `parcial/app/core/dependencies.py` con `get_usuario_actual`, `requiere_rol`, `exigir_password_al_dia` y la clase contenedora `UsuarioActual`. <!-- id: 0 -->
- [x] Actualizar `parcial/app/modules/usuarios/schemas.py` y `service.py` para incluir `debe_cambiar_password` en `UsuarioYoOut`. <!-- id: 1 -->
- [x] Actualizar `parcial/app/modules/usuarios/router.py` en `GET /auth/yo` inyectando `get_usuario_actual` (cierre de tarea CH-08). <!-- id: 2 -->
- [x] Reestructurar `parcial/app/main.py` en dos grupos de rutas (`grupo_abierto` y `grupo_protegido` con `exigir_password_al_dia` y guardas de rol). <!-- id: 3 -->
- [x] Actualizar `parcial/test/C-03_cookie.http` con las peticiones 401 sin cookie y con Bearer. <!-- id: 4 -->
- [x] Ejecutar `python seed.py` y correr las pruebas HTTP de `C-01`, `C-03` y `C-06`. <!-- id: 5 -->
- [x] Documentar la evidencia real en `verify.md` y auditar contra `.github/prompts/audit-change.prompt.md`. <!-- id: 6 -->
