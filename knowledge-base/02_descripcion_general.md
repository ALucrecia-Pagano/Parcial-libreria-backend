# Descripción General

## Qué cambia respecto del TP de los capítulos 1 a 4 (pág. 2 de la consigna)

El grupo parte de **su propio TP entregado**. Esto es el delta; lo ya hecho en el TP (CRUD de editoriales, géneros, autores, libros, clientes, ventas; migraciones 1 y 2; seed; casos `.http` del TP) **no se re-documenta ni se re-planifica**.

| Qué | Cambio |
|---|---|
| Usuarios, roles e intentos de acceso | **Nuevo.** Tablas `usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad`; módulo `usuarios` |
| `cliente` | Se agrega `usuario_id` (nulo permitido y UNIQUE): un cliente puede tener, o no, acceso por la web |
| `libro` | Se agrega borrado lógico (`borrado_en`). El ISBN deja de ser UNIQUE común y pasa a ser único entre los vigentes |
| Stock | Nuevo `movimiento_stock`, de sólo agregado. El stock ya no se edita por PATCH: cambia con el alta, la reposición y las ventas |
| Registro de una venta | Además de crear venta y renglones, descuenta el stock de cada libro y deja un movimiento por renglón, **todo en una sola transacción** |
| Capas | Todos los módulos pasan a repositorios + Unit of Work; los servicios dejan de recibir la sesión |
| Configuración | `Settings` con pydantic-settings, **sin secretos por defecto** |
| Listados | Devuelven `{items, total, page, size, pages}` en lugar de `limit`/`offset` |
| Despliegue | **Nuevo y aparte.** El TP de caps. 1–4, tal como se entregó, se empaqueta en una imagen (Dockerfile), se corre con `docker run` y se pone en línea en el VPS. **No lleva ninguna de las demás modificaciones** |

## Stack tecnológico (versiones mínimas de la consigna)

| Capa | Tecnología | Versión mínima | Notas |
|---|---|---|---|
| Lenguaje | Python | 3.12 | |
| Web | FastAPI | 0.111 | Todos los handlers `async def` |
| Modelos | SQLModel | 0.0.24 | Modelos de tabla |
| ORM/Motor | SQLAlchemy asincrónico | 2.0 | Motor, sesión, carga anticipada |
| Driver | asyncpg | 0.30 | |
| BD | PostgreSQL | 16 | En el despliegue, la que ya tiene el servidor |
| Migraciones | Alembic | 1.13 | Plantilla asincrónica |
| Config | pydantic-settings | 2.0 | Lee del entorno o `.env` (no versionado) |
| Hash | bcrypt | 4.0 | Costo en configuración; desde la v5 rechaza >72 bytes con excepción |
| Token | PyJWT | 2.8 | JWT firmado |
| Servidor | uvicorn | el que instala `fastapi[standard]` | ASGI |
| Contenedor | Docker | 20.10 | Sólo para el despliegue del TP caps. 1–4 |

## Arquitectura general

Capas por **módulo funcional**, mismas capas en todos los módulos (detalle en `08`):

```
HTTP -> router.py  (construye UoW con dependencia, llama al servicio, traduce errores)
     -> service.py (reglas de negocio; RECIBE el UoW y lo abre con `async with`; nunca lo construye)
     -> unit_of_work.py (compone repositorios con la MISMA sesión; confirma/revierte; no cierra la sesión)
     -> repository.py (BaseRepository[T] / SoftDeleteRepository[T]; add/update hacen flush(), nunca commit(); precarga declarada acá)
     -> models.py (SQLModel tables, restricciones, relaciones)
```

Decisiones de alto nivel impuestas por la consigna:
- Motor y fábrica de sesiones se crean **en el lifespan** y se guardan en `app.state` (no al importar).
- Dos grupos de rutas en `main.py`: **abierto** (catálogo público, `/auth`, `/health`) y **protegido** (lleva el control de cambio obligatorio de contraseña montado una sola vez).
- La autorización se decide con los roles **vigentes en la base** en cada petición; los roles del token son informativos.
- Garantías delegadas a la base: UNIQUE/índices únicos parciales, FKs, CHECKs y disparador de sólo agregado.

## Integraciones externas

| Servicio | Propósito | Tipo |
|---|---|---|
| PostgreSQL (VPS, EasyPanel) | Persistencia; en despliegue es una base nueva `libreria` en el servidor ya existente | asyncpg / `postgresql+asyncpg` |
| Aviso de comprobante al cliente | Simulado: `await asyncio.sleep(0.5)` + mensaje en el registro | `BackgroundTasks` (mismo proceso) |
| VPS / Docker | Hospedar el TP caps. 1–4 | `docker build` / `docker run` |

No hay pasarelas de pago, correo real ni colas.

## Variables de configuración (parcial/)

La URL de la base se arma con `@computed_field` desde `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` con driver `postgresql+asyncpg`. La clave de firma del token también sale del entorno. **Ni la clave ni la contraseña de la base tienen valor por defecto**: si faltan, la app no arranca. `env.example` con todas las variables y ningún secreto. Tabla completa en `08`.

> En `despliegue/` (TP caps. 1–4) la configuración es otra: `DATABASE_URL` completa + `SQL_ECHO=false`. Ver `13`.

## API REST

Resumen y tabla completa de endpoints en `11_endpoints_y_casos_de_prueba.md`.
