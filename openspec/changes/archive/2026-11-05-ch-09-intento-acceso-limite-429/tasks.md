# Tasks

## 1. Repositorio y Registro Independiente de Intentos

- [x] 1.1 Implementar `IntentoAccesoRepository` en `parcial/app/modules/usuarios/repository.py` con método `obtener_fallos_recientes(email, ip, ventana_segundos=60)` que consulte fallos en la ventana temporal posteriores al último éxito y calcule el tiempo restante para `Retry-After`.
- [x] 1.2 Implementar en `parcial/app/modules/usuarios/repository.py` la función `registrar_intento(session_factory, email, ip, exito)` en sesión y transacción propia que siempre confirma, incluyendo el comentario documental con sus tres aspectos (qué hace distinto, por qué no comparte la transacción y su costo).

## 2. Rate Limiting y Auditoría en el Servicio de Login

- [x] 2.1 Actualizar `UsuariosService.login` en `parcial/app/modules/usuarios/service.py` para evaluar el umbral de 5 fallos como primer paso y elevar inmediatamente `HTTPException(429)` con cabecera `Retry-After` sin calcular hash bcrypt ni registrar el intento bloqueado.
- [x] 2.2 Integrar en `UsuariosService.login` el llamado a `registrar_intento` con `exito=True` tras una autenticación exitosa y con `exito=False` cuando las credenciales sean inválidas (antes de propagar el 401).

## 3. Adaptación del Router y Caso de Prueba

- [x] 3.1 Actualizar `parcial/app/modules/usuarios/router.py` para obtener la IP del cliente (`request.client.host` o fallback) y la fábrica de sesiones de `request.app.state.session_factory`, delegando ambos al servicio de login.
- [x] 3.2 Crear `parcial/test/C-05_limite_intentos.http` y verificar los 5 intentos fallidos iniciales (401), el 6º intento rechazado con 429 y cabecera `Retry-After` en pocos milisegundos, la ausencia del 429 en la base de datos y la recuperación de acceso.
