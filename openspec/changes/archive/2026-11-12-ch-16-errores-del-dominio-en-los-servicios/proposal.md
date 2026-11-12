# Proposal: CH-16 Errores del dominio en los servicios

## Why

La devolución de la cátedra marcó como único indicador pendiente **U-06** (*"Los servicios no lanzan `HTTPException`: lanzan errores del dominio y se traducen a códigos HTTP"*). Hoy los siete archivos `service.py` de `parcial/app/modules/` importan `fastapi` y lanzan `HTTPException` directamente, acoplando la capa de reglas de negocio al protocolo HTTP.

## What Changes

- Se agrega en `parcial/app/core/errores.py` una jerarquía de excepciones de dominio sin dependencia de FastAPI: `ErrorDominio(Exception)` (con atributo `mensaje`) y las subclases `NoEncontrado`, `Conflicto`, `NoAutenticado`, `Prohibido` y `DemasiadosIntentos` (con atributo `retry_after`).
- Se agrega un único manejador global (`manejar_error_dominio`) en `parcial/app/core/errores.py` y se registra en `parcial/app/main.py` mediante `app.add_exception_handler(ErrorDominio, manejar_error_dominio)` para traducir cada error del dominio a su código HTTP (`404`, `409`, `401`, `403`, `429`), cuerpo `{"detail": mensaje}` y cabecera `Retry-After` en `DemasiadosIntentos`.
- Se reemplazan todos los `raise HTTPException` y se eliminan los imports de `fastapi` en `parcial/app/modules/{autores,clientes,editoriales,generos,libros,usuarios,ventas}/service.py`, conservando exactamente los mismos mensajes y comportamientos observables.
- Se mantienen sin cambios `parcial/app/core/dependencies.py`, `parcial/app/core/paginacion.py` (capa HTTP) y la traducción de `IntegrityError` (`traducir_integrity_error`) en los routers.

## Capabilities

### New Capabilities

_(Ninguna)_

### Modified Capabilities

- `acceso-a-datos-y-contratos-base`: Incorpora la jerarquía de errores del dominio (`ErrorDominio` y subclases), el manejador global HTTP en `app/core/errores.py` y la separación estricta entre servicios de negocio y `HTTPException`.

## Impact

- `parcial/app/core/errores.py`
- `parcial/app/main.py`
- `parcial/app/modules/autores/service.py`
- `parcial/app/modules/clientes/service.py`
- `parcial/app/modules/editoriales/service.py`
- `parcial/app/modules/generos/service.py`
- `parcial/app/modules/libros/service.py`
- `parcial/app/modules/usuarios/service.py`
- `parcial/app/modules/ventas/service.py`
- Sin cambios de esquema ni migraciones de base de datos; contratos externos de la API (códigos HTTP, JSON `{"detail": ...}` y `Retry-After`) 100% preservados.
