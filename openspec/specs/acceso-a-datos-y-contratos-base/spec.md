# acceso-a-datos-y-contratos-base Specification

## Purpose

Provee las abstracciones base de infraestructura en `app/core/` para el acceso a datos genérico y con baja lógica (`repository.py`), el control transaccional por operación de negocio (`unit_of_work.py`), el envoltorio y validación de colecciones paginadas (`paginacion.py`) y la traducción segura de errores de integridad de la base a respuestas HTTP 409 (`errores.py`).

## Requirements

### Requirement: Repositorio base genérico sin confirmación transaccional
El sistema SHALL proveer una clase genérica `BaseRepository[T]` cuyo constructor reciba explícitamente la sesión asincrónica y la clase del modelo (`model: type[T]`), y que ofrezca las operaciones mínimas `get_by_id`, `get_all` (con `offset` y `limit`, ordenado por `id`), `count`, `add`, `update` y `delete`; las operaciones de escritura (`add`, `update`, `delete`) SHALL emitir los cambios con `flush()` y NUNCA confirmar la transacción con `commit()`.

#### Scenario: Instanciación con clase de modelo explícita y lectura básica
- **GIVEN** una sesión asincrónica activa y datos iniciales cargados
- **WHEN** se instancia el repositorio base pasando la sesión y el modelo `Editorial` y se invocan `count()`, `get_all(offset=0, limit=2)` y `get_by_id(1)`
- **THEN** `count()` devuelve `3`, `get_all` devuelve las dos primeras editoriales ordenadas por `id` y `get_by_id(1)` devuelve `"Letras del Río"`

#### Scenario: Escritura emite flush y asigna identificador sin hacer commit
- **GIVEN** una sesión asincrónica activa
- **WHEN** se invoca `add` o `update` sobre el repositorio base y luego se revierte la sesión (`rollback()`)
- **THEN** durante la operación la entidad recibe su `id` por `flush()`, pero tras el `rollback()` el cambio no queda persistido en la base de datos

### Requirement: Repositorio con borrado lógico separado
El sistema SHALL proveer una clase `SoftDeleteRepository[T]` que herede de `BaseRepository[T]`, filtre automáticamente las filas con `borrado_en` no nulo en `get_by_id`, `get_all` y `count`, y agregue los métodos `get_by_id_including_deleted` (que no filtra bajas) y `soft_delete` (que asigna la marca de tiempo actual con zona horaria a `borrado_en` y hace `flush()` sin borrar físicamente la fila).

#### Scenario: Baja lógica oculta la entidad en lecturas normales pero la conserva en lecturas históricas
- **GIVEN** un libro vigente en la base de datos
- **WHEN** se ejecuta `soft_delete` sobre ese libro desde el repositorio con borrado lógico
- **THEN** `get_by_id` devuelve `None` y `count` disminuye en uno, mientras que `get_by_id_including_deleted` sigue devolviendo el libro con `borrado_en` poblado

### Requirement: Unit of Work base como gestor de contexto asincrónico
El sistema SHALL proveer una clase `UnitOfWork` base que actúe como gestor de contexto asincrónico (`async with`): al salir normalmente del bloque SHALL confirmar la transacción (`commit()`), si se sale con una excepción SHALL revertirla (`rollback()`) dejando propagar la excepción sin traducirla a HTTP, y en ningún caso SHALL cerrar la sesión recibida.

#### Scenario: Confirmación al salir sin errores y sesión abierta
- **GIVEN** un `UnitOfWork` inicializado con una sesión asincrónica
- **WHEN** se agrega una entidad con `flush()` dentro de `async with uow:` y el bloque termina sin excepción
- **THEN** el cambio queda confirmado en la base de datos y la sesión continúa abierta para ser cerrada por la dependencia que la creó

#### Scenario: Reversión automática ante excepción a mitad de bloque
- **GIVEN** un `UnitOfWork` inicializado con una sesión asincrónica
- **WHEN** dentro de `async with uow:` se realiza una escritura con `flush()` y luego se lanza una excepción antes de salir del bloque
- **THEN** el `UnitOfWork` ejecuta `rollback()`, ninguna escritura del bloque queda en la base y la excepción original se propaga intacta

### Requirement: Envoltorio de paginación y validación de página inexistente
El sistema SHALL proveer el contrato de salida `{items, total, page, size, pages}` con `page >= 1` y `size` entre `1` y `100` (por defecto `20`), donde `pages` vale `1` cuando `total` es `0`, y solicitar una `page` mayor que `pages` SHALL responder con código `422` y el mensaje `"La página X no existe: hay Y"` verificando el rango a partir de `total` antes de consultar los ítems de la página.

#### Scenario: Cálculo de páginas con resultados
- **GIVEN** un total de `5` registros y parámetros `page = 1`, `size = 2`
- **WHEN** se valida y construye la página con los 2 ítems correspondientes
- **THEN** el envoltorio devuelve `total = 5`, `page = 1`, `size = 2` y `pages = 3`

#### Scenario: Colección vacía tiene una única página vacía
- **GIVEN** un total de `0` registros y parámetros `page = 1`, `size = 20`
- **WHEN** se valida y construye la página
- **THEN** el envoltorio devuelve `items = []`, `total = 0`, `page = 1`, `size = 20` y `pages = 1`

#### Scenario: Pedido de página más allá de la última rechaza con 422
- **GIVEN** un total de `5` registros y un tamaño de página `size = 2` (`pages = 3`)
- **WHEN** se solicita la página `page = 4`
- **THEN** la validación rechaza la petición con estado HTTP `422` y detalle exacto `"La página 4 no existe: hay 3"`

### Requirement: Traducción de IntegrityError a 409 con mensaje propio
El sistema SHALL proveer un traductor de `IntegrityError` basado en el diccionario `MENSAJES_CONSTRAINT` que devuelva una excepción HTTP `409 Conflict` con un mensaje propio de dominio según la restricción violada y que NUNCA exponga en la respuesta nombres de tablas, columnas, constraints ni texto interno del motor PostgreSQL (RN-15).

#### Scenario: Violación de constraint conocido devuelve su mensaje propio 409
- **GIVEN** existe la editorial `"Letras del Río"` en la base
- **WHEN** se intenta insertar otra editorial con el mismo nombre, se captura el `IntegrityError` y se pasa al traductor de errores
- **THEN** se obtiene una excepción HTTP con código `409` y el mensaje propio asociado a `uq_editorial_nombre`, sin contener texto crudo de la base ni el nombre técnico del constraint

#### Scenario: Violación de integridad no catalogada usa el mensaje por defecto sin filtrar SQL
- **GIVEN** un `IntegrityError` cuyo nombre de restricción no figura en el diccionario
- **WHEN** se pasa al traductor de errores
- **THEN** se obtiene una excepción HTTP `409` con el mensaje genérico de conflicto en español y sin ningún fragmento del error del driver

### Requirement: Jerarquía de errores del dominio sin acoplamiento a HTTP
El sistema SHALL proveer en `app/core/errores.py` una jerarquía de excepciones de dominio (`ErrorDominio` con atributo `mensaje`) cuyas clases (`NoEncontrado`, `Conflicto`, `NoAutenticado`, `Prohibido` y `DemasiadosIntentos` con atributo `retry_after`) hereden de `Exception` y no dependan de `fastapi` ni de `HTTPException`.

#### Scenario: Instanciación de errores del dominio con mensaje y atributo propio
- **GIVEN** los módulos de negocio necesitan señalar un error semántico de dominio
- **WHEN** se instancia `NoEncontrado`, `Conflicto`, `NoAutenticado`, `Prohibido` con un `mensaje`, o `DemasiadosIntentos` con `mensaje` y `retry_after`
- **THEN** la excepción conserva el atributo `mensaje` (y `retry_after` en `DemasiadosIntentos`) y es subclase de `ErrorDominio` y `Exception` sin heredar de `HTTPException`

### Requirement: Manejador global único para traducir errores del dominio a HTTP
El sistema SHALL registrar en `app/main.py` un único manejador global definido en `app/core/errores.py` para `ErrorDominio` que traduzca cada subclase a su código de estado (`404`, `409`, `401`, `403` o `429`), devuelva el cuerpo JSON `{"detail": mensaje}` e incluya la cabecera `Retry-After` cuando el error sea `DemasiadosIntentos`.

#### Scenario: Traducción de errores de dominio comunes a códigos HTTP y detail
- **GIVEN** un endpoint cuyo servicio lanza `NoEncontrado`, `Conflicto`, `NoAutenticado` o `Prohibido` con un mensaje de dominio
- **WHEN** la excepción alcanza la aplicación FastAPI sin ser capturada en el router
- **THEN** el manejador global responde con estado `404`, `409`, `401` o `403` respectivamente y cuerpo `{"detail": "<mensaje>"}`

#### Scenario: Traducción de DemasiadosIntentos con cabecera Retry-After
- **GIVEN** un intento de login bloqueado por límite de tasa donde el servicio lanza `DemasiadosIntentos` con `retry_after`
- **WHEN** el manejador global procesa la excepción
- **THEN** responde con estado `429`, cuerpo `{"detail": "<mensaje>"}` y cabecera `Retry-After` con el valor entero en segundos como texto

### Requirement: Servicios desacoplados de HTTPException y FastAPI
Ningún archivo `service.py` de `app/modules/` SHALL importar `fastapi` ni lanzar `HTTPException`; las reglas de negocio en los servicios SHALL lanzar únicamente excepciones de la jerarquía `ErrorDominio` (y delegar las validaciones de paginación o integridad según corresponda), manteniendo intactos los códigos y mensajes observables de la API.

#### Scenario: Verificación estática de ausencia de FastAPI en servicios
- **GIVEN** todos los módulos bajo `parcial/app/modules/*/service.py`
- **WHEN** se inspeccionan en busca de `HTTPException` o `from fastapi`
- **THEN** no existe ninguna coincidencia en ningún archivo `service.py`

#### Scenario: Preservación de respuestas de error en los casos de prueba E2E
- **GIVEN** la base inicializada con `python seed.py` y el servidor levantado
- **WHEN** se ejecutan los casos `C-01` a `C-16` de `parcial/test/`
- **THEN** todas las peticiones devuelven los mismos códigos HTTP, cuerpos `detail` y cabecera `Retry-After` en `C-05` que antes de la refactorización
