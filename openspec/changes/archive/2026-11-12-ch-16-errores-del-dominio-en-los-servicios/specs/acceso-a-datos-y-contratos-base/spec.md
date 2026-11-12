# Spec Delta — acceso-a-datos-y-contratos-base

## ADDED Requirements

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
