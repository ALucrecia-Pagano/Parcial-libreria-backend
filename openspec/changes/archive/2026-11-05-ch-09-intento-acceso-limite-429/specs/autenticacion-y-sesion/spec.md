# Spec Delta

## ADDED Requirements

### Requirement: Limitación de intentos fallidos de autenticación (Rate Limiting)
El sistema SHALL limitar los intentos de inicio de sesión fallidos a un máximo de 5 por combinación de email e IP en una ventana móvil de 60 segundos, contados desde el último login exitoso. Al alcanzar 5 fallos, cualquier petición posterior dentro de la ventana SHALL ser rechazada con código HTTP 429 y cabecera `Retry-After` que indique los segundos restantes hasta la liberación del intento más antiguo. La evaluación SHALL realizarse antes de ejecutar cualquier cómputo de hashing con bcrypt.

#### Scenario: Quinto intento fallido dentro de la ventana de 60 segundos
- **WHEN** un cliente realiza el quinto intento consecutivo de login fallido con un mismo correo e IP en menos de 60 segundos
- **THEN** el sistema responde con código HTTP 401 y mensaje `Credenciales inválidas`, asentando el quinto fallo en el registro

#### Scenario: Sexto intento fallido rechazado con 429
- **WHEN** un cliente realiza un nuevo intento de login tras registrar 5 fallos previos dentro de los últimos 60 segundos sin un éxito intermedio
- **THEN** el sistema responde con código HTTP 429 y cabecera `Retry-After` con los segundos de espera correspondientes, respondiendo de inmediato sin calcular hash bcrypt

#### Scenario: Intento exitoso reinicia la cuenta de fallos
- **WHEN** un cliente se autentica exitosamente tras haber tenido fallos previos
- **THEN** el sistema asienta el éxito y los fallos anteriores dejan de computar para el límite de 5 intentos

### Requirement: Registro transaccional independiente de intentos de acceso
El sistema SHALL persistir cada intento de autenticación procesado (exitoso o fallido) en la tabla `intento_acceso` asociando correo, dirección IP, fecha/hora y resultado booleano (`exito`). La escritura SHALL ejecutarse en una sesión y transacción propia e independiente, garantizando su persistencia aun cuando la petición de login finalice con código de error HTTP 401. Las peticiones rechazadas por límite de tasa (429) NUNCA SHALL registrarse.

#### Scenario: Intento exitoso o fallido registrado
- **WHEN** una petición de login es procesada y evaluada, resultando en autenticación exitosa (200) o credenciales inválidas (401)
- **THEN** se almacena un registro en la tabla `intento_acceso` con el email, IP del cliente, marca temporal y el resultado booleano correspondiente

#### Scenario: Petición rechazada por 429 no se registra
- **WHEN** una petición de login es rechazada por superar el umbral de intentos fallidos respondiendo con código HTTP 429
- **THEN** el sistema no añade ninguna fila en la tabla `intento_acceso` para dicho intento bloqueado
