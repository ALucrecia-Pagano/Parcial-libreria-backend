# Design: CH-16 Errores del dominio en los servicios

## Context

Ver [proposal.md](proposal.md) para la motivación (indicador U-06). Actualmente `parcial/app/core/errores.py` solo contiene `MENSAJES_CONSTRAINT` y `traducir_integrity_error` (usado por los routers para traducir `IntegrityError` de SQLAlchemy a `HTTPException(409)`), mientras que los siete `service.py` bajo `parcial/app/modules/` importan `fastapi.HTTPException` y `fastapi.status` directamente. El `UnitOfWork` hace `rollback()` ante cualquier excepción y la deja propagar sin traducirla a HTTP.

## Goals / Non-Goals

**Goals:**
- Desacoplar los siete servicios (`autores`, `clientes`, `editoriales`, `generos`, `libros`, `usuarios`, `ventas`) de `fastapi` y `HTTPException`.
- Centralizar las excepciones de dominio y su único manejador global HTTP en `parcial/app/core/errores.py`, registrado en `parcial/app/main.py`.
- Preservar bit a bit los códigos de estado, cuerpos JSON `{"detail": ...}` y cabeceras (`Retry-After` en 429) esperados por los casos `C-01`..`C-16`.

**Non-Goals:**
- No se modifican `parcial/app/core/dependencies.py`, `parcial/app/core/paginacion.py`, `parcial/app/modules/health/router.py` ni las validaciones de configuración HTTP en `parcial/app/modules/usuarios/router.py` (son capa HTTP).
- No se modifica `traducir_integrity_error` ni los bloques `except IntegrityError` en los routers.
- No se alteran modelos, esquemas, repositorios ni migraciones de Alembic.

## Decisions

1. **Jerarquía pura en `app/core/errores.py` sin herencia de `HTTPException` ni códigos HTTP embebidos en las clases:**
   - `ErrorDominio(Exception)` guarda `self.mensaje = mensaje` y llama `super().__init__(mensaje)`.
   - Subclases sin estado extra: `NoEncontrado`, `Conflicto`, `NoAutenticado`, `Prohibido`.
   - Subclase `DemasiadosIntentos(ErrorDominio)` recibe `(mensaje: str, retry_after: int)` y guarda `self.retry_after = retry_after`.
   - *Alternativa descartada:* Guardar `status_code` dentro de cada clase de dominio (acoplaría la jerarquía de dominio a códigos HTTP). En su lugar, el mapa `_CODIGOS_ERROR_DOMINIO` vive junto al manejador global HTTP.

2. **Manejador global único en `app/core/errores.py` y registro en `app/main.py`:**
   - `manejar_error_dominio(request: Request, exc: ErrorDominio) -> JSONResponse` resuelve el código HTTP por clase (`NoEncontrado` → `404`, `Conflicto` → `409`, `NoAutenticado` → `401`, `Prohibido` → `403`, `DemasiadosIntentos` → `429`, fallback `500` para `ErrorDominio` genérico) y devuelve `JSONResponse(status_code=..., content={"detail": exc.mensaje}, headers=...)`, agregando `{"Retry-After": str(exc.retry_after)}` cuando `isinstance(exc, DemasiadosIntentos)`.
   - Se registra en `app/main.py` con `app.add_exception_handler(ErrorDominio, manejar_error_dominio)`.
   - *Alternativa descartada:* Capturar `ErrorDominio` con `try/except` en cada endpoint de cada router (duplicaría código en decenas de handlers y contradice cátedra cap1 §1.10.1).

3. **Limpieza en `libros/service.py` y mensajes idénticos:**
   - En `libros/service.py` se elimina el helper `_no_encontrado` que devolvía `HTTPException` y se reemplaza por `raise NoEncontrado(...)` directamente.
   - Todos los mensajes literales de error en los siete `service.py` se conservan idénticos para garantizar cero regresiones en `C-01`..`C-16`.

4. **Compatibilidad con `UnitOfWork`:**
   - Como `ErrorDominio` hereda de `Exception`, si se lanza dentro de `async with uow:` activa `__aexit__` con `exc_type is not None`, ejecuta `await self.session.rollback()` y se propaga hasta el manejador global de FastAPI, exactamente igual que ocurría con `HTTPException`.

## Risks / Trade-offs

- **Riesgo:** Que `app/core/errores.py` siga importando `fastapi` para `traducir_integrity_error` y `manejar_error_dominio`, mientras las clases `ErrorDominio` no usan FastAPI. → **Mitigación:** La especificación requiere la jerarquía sin imports/tipos de FastAPI y ningún `service.py` importando `fastapi` ni `HTTPException`; en `errores.py` se separa claramente la sección de excepciones puras de dominio de la sección de traducción HTTP (`manejar_error_dominio` y `traducir_integrity_error`).
- **Riesgo:** Que alguna ruta en un router envuelva llamadas al servicio en `try/except Exception` y atrape accidentalmente `ErrorDominio`. → **Mitigación:** Verificado que los routers solo capturan `except IntegrityError`; ningún router captura `Exception` ni `HTTPException`.
- **Riesgo:** Diferencia sutil de formato JSON o cabecera `Retry-After` en `C-05`. → **Mitigación:** `JSONResponse` devuelve exactamente `{"detail": exc.mensaje}` (igual que el manejador por defecto de `HTTPException` de FastAPI) y `headers={"Retry-After": str(exc.retry_after)}`; se valida corriendo `C-01`..`C-16` completos contra la base real tras `python seed.py`.
