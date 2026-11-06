# Tasks: CH-11 — Cambiar contraseña y cambio obligatorio

- [x] Agregar esquemas `CambiarPasswordIn` y `CambiarPasswordOut` en `parcial/app/modules/usuarios/schemas.py`. <!-- id: 0 -->
- [x] Implementar método `cambiar_password` en `parcial/app/modules/usuarios/service.py` con bcrypt previo y UoW atómico (RN-16). <!-- id: 1 -->
- [x] Implementar endpoint `POST /auth/cambiar-password` en `parcial/app/modules/usuarios/router.py`. <!-- id: 2 -->
- [x] Ejecutar `python seed.py` y verificar caso `C-09_cambio_obligatorio.http`. <!-- id: 3 -->
- [x] Documentar evidencia en `verify.md` y auditar contra `.github/prompts/audit-change.prompt.md`. <!-- id: 4 -->
