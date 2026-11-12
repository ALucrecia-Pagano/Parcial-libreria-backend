# Tasks: CH-16 Errores del dominio en los servicios

## 1. Jerarquía de errores del dominio y manejador global

- [x] 1.1 Agregar en `parcial/app/core/errores.py` la jerarquía `ErrorDominio(Exception)` (con atributo `mensaje`) y sus subclases `NoEncontrado`, `Conflicto`, `NoAutenticado`, `Prohibido` y `DemasiadosIntentos` (con atributo `retry_after`), manteniendo intacto `traducir_integrity_error`, y verificar importación desde Python sin errores.
- [x] 1.2 Agregar el manejador global `manejar_error_dominio` en `parcial/app/core/errores.py` (mapeando 404/409/401/403/429, `{"detail": exc.mensaje}` y cabecera `Retry-After` en `DemasiadosIntentos`) y registrarlo en `parcial/app/main.py` mediante `app.add_exception_handler(ErrorDominio, manejar_error_dominio)`, verificando que la app arranca limpia.

## 2. Migración de los servicios a errores del dominio

- [x] 2.1 Reemplazar `HTTPException` y eliminar imports de `fastapi` en los servicios de catálogo (`parcial/app/modules/autores/service.py`, `editoriales/service.py`, `generos/service.py`, `libros/service.py`) usando `NoEncontrado` y `Conflicto` con los mismos mensajes, y verificar con `C-13_baja_reposicion_isbn.http`, `C-16_busqueda_paginacion_patch.http` y `CH-04_editoriales_generos_autores.http`.
- [x] 2.2 Reemplazar `HTTPException` y eliminar imports de `fastapi` en `parcial/app/modules/clientes/service.py` y `parcial/app/modules/ventas/service.py` usando `NoEncontrado`, `Conflicto` y `Prohibido` con los mismos mensajes, y verificar con `C-10_venta_valida.http`, `C-11_venta_sin_stock.http`, `C-12_venta_referencias_invalidas.http` y `CH-13_clientes.http`.
- [x] 2.3 Reemplazar `HTTPException` y eliminar imports de `fastapi` en `parcial/app/modules/usuarios/service.py` usando `NoAutenticado`, `NoEncontrado`, `Conflicto` y `DemasiadosIntentos(..., retry_after=retry_after)` con los mismos mensajes, y verificar con `C-02`..`C-09` incluyendo la cabecera `Retry-After` en `C-05`.

## 3. Verificación final de integración y regresión

- [x] 3.1 Confirmar que `HTTPException` y `from fastapi` no aparecen en ningún `parcial/app/modules/*/service.py` y que `parcial/app/core/dependencies.py` y `parcial/app/core/paginacion.py` permanecen sin cambios.
- [x] 3.2 Ejecutar `alembic check` y confirmar salida limpia sin migraciones pendientes.
- [x] 3.3 Ejecutar `python seed.py` y correr toda la batería `.http` (`C-01` a `C-16`, más `CH-01`, `CH-04`, `CH-13`) contra la aplicación levantada y la base real, registrando códigos, cuerpos `detail` y cabecera `Retry-After` en `C-05`.

## Workflow follow-up

- Archivar el change con `/opsx:archive ch-16-errores-del-dominio-en-los-servicios` cuando la usuaria lo indique.
- Realizar el commit correspondiente manualmente (los agentes no commitean).
