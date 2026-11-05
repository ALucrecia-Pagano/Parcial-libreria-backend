# Design

## Context

En CH-07 se implementó el flujo de autenticación, la verificación asíncrona de contraseñas mediante bcrypt y la emisión de tokens en cookies HttpOnly. En CH-01 se definió la tabla `intento_acceso` con el índice compuesto `(email, ip, cuando)`. En esta etapa se completa la protección del endpoint de login frente a ataques de fuerza bruta (RN-07), anteponiendo una consulta de tasa de intentos antes de invocar bcrypt y garantizando el registro de auditoría.

## Goals / Non-Goals

**Goals:**
- Implementar `IntentoAccesoRepository` con métodos para consultar fallos en la ventana de 60 segundos desde el último éxito y calcular el valor de `Retry-After`.
- Implementar la función `registrar_intento(session_factory, email, ip, exito)` que abre una sesión propia e independiente fuera de la transacción de la petición, con el comentario obligatorio sobre su funcionamiento, justificación y costo.
- Integrar la comprobación en `UsuariosService.login` como primer paso: si se registraron 5 fallos en los últimos 60 s, responder de inmediato con HTTP 429 y cabecera `Retry-After`, sin ejecutar bcrypt y sin registrar el intento bloqueado (P-14).
- Registrar cada intento procesado (éxito o fallo) en `intento_acceso`.
- Verificar el comportamiento mediante el archivo `parcial/test/C-05_limite_intentos.http`.

**Non-Goals:**
- Bloqueo permanente de usuarios o cuentas a nivel de base de datos.
- Implementación de almacenamiento en memoria externa o Redis (Backlog).

## Decisions

### 1. Sesión y transacción propia e independiente para `registrar_intento`
- **Decisión**: La función `registrar_intento` recibe la fábrica `session_factory: async_sessionmaker[AsyncSession]` de `app.state`, crea una sesión dedicada, añade la fila a `intento_acceso` y ejecuta `await session.commit()`.
- **Razón (Cátedra §6.8.1, §6.8.2)**: Si el intento se registrara en la misma sesión/transacción de la petición, cuando el login falla y el servicio lanza un `HTTPException(401)`, el Unit of Work o el middleware revertiría la transacción (`rollback`), eliminando la fila que justamente se necesita contar.
- **Costo**: Genera una conexión corta adicional al pool exclusivamente para el insert del intento y un commit inmediato.

### 2. Consulta de fallos en ventana móvil desde el último éxito
- **Decisión**: Para contar los intentos fallidos, se buscan las filas de `intento_acceso` con el mismo email e IP registradas en los últimos 60 segundos. Si existió un intento exitoso (`exito = True`), solo se consideran los fallos posteriores a la marca temporal de dicho éxito (un login correcto reinicia la ventana de conteo).
- **Cálculo de `Retry-After`**: Si hay 5 o más fallos en la ventana, se toma el fallo más antiguo dentro de la ventana de 60 s (`fallo_mas_antiguo.cuando`) y se calcula `segundos_restantes = int(60 - (ahora - fallo_mas_antiguo.cuando).total_seconds())`. Se retorna en la cabecera `Retry-After: <segundos_restantes>` con un mínimo de 1 segundo.

### 3. Peticiones 429 no registradas y sin consumo de CPU
- **Decisión**: Cuando una petición es rechazada por alcanzar los 5 fallos, se lanza inmediatamente `HTTPException(429)` con la cabecera `Retry-After`. No se ejecuta `verificar_password` (evitando los ~250ms de CPU de bcrypt) y **no** se inserta ninguna fila en `intento_acceso` (P-14).

## Risks / Trade-offs

- **[Crecimiento de la tabla `intento_acceso`]** → *Mitigación*: La tabla cuenta con el índice `ix_intento_acceso_email_ip_cuando` creado en la migración 3 de CH-01, permitiendo que la búsqueda por `(email, ip, cuando)` sea rápida.
- **[Agotamiento del pool por conexiones concurrentes de auditoría]** → *Mitigación*: La sesión de `registrar_intento` realiza una sola inserción y se cierra de inmediato (`async with session_factory() as session:`).
