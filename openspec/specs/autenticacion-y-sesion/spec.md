# autenticacion-y-sesion Specification

## Purpose

Define las capacidades de autenticación del sistema, emisión de sesiones seguras mediante cookies HttpOnly, prevención de ataques de enumeración y ejecución no bloqueante de algoritmos criptográficos.

## Requirements

### Requirement: Autenticación mediante credenciales y emisión de cookie
El sistema SHALL permitir iniciar sesión vía `POST /auth/login` con correo y contraseña. Ante credenciales válidas de un usuario activo, SHALL responder HTTP 200 con `mensaje`, `debe_cambiar_password` y `expira_en_segundos`, emitiendo la cookie `access_token` (`HttpOnly`, `SameSite=Lax`, expiración según vigencia y `Secure` según configuración). La respuesta NUNCA SHALL exponer el token de acceso en el cuerpo JSON.

#### Scenario: Inicio de sesión exitoso
- **WHEN** un cliente realiza `POST /auth/login` con email y contraseña válidos de un usuario activo
- **THEN** el sistema responde con código HTTP 200, un cuerpo con `mensaje`, `debe_cambiar_password` y `expira_en_segundos` sin token expuesto, y una cabecera `Set-Cookie` con la cookie `access_token` configurada con `HttpOnly` y `SameSite=Lax`

#### Scenario: Usuario inactivo no puede iniciar sesión
- **WHEN** un cliente realiza `POST /auth/login` con credenciales válidas pero correspondientes a un usuario con `activo=false`
- **THEN** el sistema responde con código HTTP 401 y mensaje `Credenciales inválidas`, sin emitir cookie de sesión

### Requirement: Mitigación de enumeración de usuarios
El sistema SHALL responder con código HTTP 401 y el mensaje exacto `Credenciales inválidas` tanto cuando el correo electrónico no exista como cuando la contraseña no coincida. Si el correo no existe, el sistema SHALL ejecutar una verificación simulada contra un hash ficticio precalculado para igualar el tiempo de respuesta y neutralizar ataques de temporización.

#### Scenario: Contraseña incorrecta para usuario existente
- **WHEN** un cliente realiza `POST /auth/login` con el correo de un usuario existente pero una contraseña incorrecta
- **THEN** el sistema responde con código HTTP 401 y cuerpo `{"detail": "Credenciales inválidas"}`

#### Scenario: Intento de inicio de sesión con correo inexistente
- **WHEN** un cliente realiza `POST /auth/login` con un correo que no existe en el sistema
- **THEN** el sistema ejecuta la verificación criptográfica contra el hash ficticio y responde con código HTTP 401 y el mismo cuerpo `{"detail": "Credenciales inválidas"}`, en un tiempo comparable al caso de usuario existente

### Requirement: Restricción de longitud de contraseña en contratos de entrada
El sistema SHALL validar en todos los esquemas de entrada que reciban contraseñas que la representación codificada en UTF-8 del valor no exceda los 72 bytes. Si la contraseña supera los 72 bytes, el sistema SHALL rechazar la petición con código de estado HTTP 422 antes de invocar cualquier operación de hash o base de datos.

#### Scenario: Contraseña con longitud mayor a 72 bytes
- **WHEN** un cliente envía una petición `POST /auth/login` con una contraseña cuya codificación UTF-8 supera los 72 bytes
- **THEN** el sistema responde con código HTTP 422 indicando error de validación en el campo de contraseña

#### Scenario: Contraseña válida de hasta 72 bytes
- **WHEN** un cliente envía una petición `POST /auth/login` con una contraseña de hasta 72 bytes en UTF-8
- **THEN** el sistema acepta el contrato de entrada y procede con la autenticación

### Requirement: Operaciones de hash no bloqueantes con control de concurrencia
Las operaciones de cálculo y verificación de contraseñas mediante bcrypt SHALL ejecutarse en un hilo de trabajo separado (`asyncio.to_thread`) para no bloquear el bucle de eventos principal. Dichas operaciones SHALL estar reguladas por un semáforo asíncrono para limitar la concurrencia de procesamiento de hashing intensivo.

#### Scenario: Verificación de contraseña concurrente
- **WHEN** múltiples peticiones de autenticación llegan concurrentemente
- **THEN** la verificación de hashes bcrypt se delega a hilos de ejecución secundarios respetando el límite del semáforo sin degradar la capacidad de respuesta del bucle de eventos

### Requirement: Generación y verificación de tokens de acceso JWT
El sistema SHALL emitir tokens de acceso JWT firmados con el secreto configurado y algoritmo HS256. El token SHALL contener los claims `sub` con el identificador del usuario, `exp` con el tiempo de expiración y los roles vigentes del usuario al momento de la emisión.

#### Scenario: Contenido del token generado
- **WHEN** se genera un token de acceso tras una autenticación exitosa
- **THEN** el token codificado incluye en su payload el identificador del usuario en `sub`, la fecha de expiración en `exp` y la lista de roles activos y vigentes

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

