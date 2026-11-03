# Arquitectura Propuesta

## Patrones aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| Capas por módulo | `app/modules/<módulo>/` | Cada capa sabe lo suyo y nada más (obj. 1) |
| Repository genérico | `app/core/repository.py` (`BaseRepository[T]`, `SoftDeleteRepository[T]`) | Acceso a datos reutilizable; el constructor recibe sesión **y clase del modelo** (los genéricos se borran en runtime) |
| Soft delete | `SoftDeleteRepository` (usado por `Libro`) | Baja lógica con `borrado_en`; filtra bajas; `get_by_id_including_deleted`, `soft_delete` |
| Unit of Work | `app/core/unit_of_work.py` + `unit_of_work.py` por módulo | Una transacción por operación de negocio; confirma al salir, revierte con excepción, **no cierra la sesión** |
| Inyección de dependencias | `app/core/dependencies.py` | Usuario actual, roles vigentes, control de cambio obligatorio, `requiere_rol`; comparten sesión con el UoW |
| Lifespan / `app.state` | `main.py`, `app/core/database.py` | Motor y fábrica creados en el lifespan, no al importar |
| DTO / contratos | `schemas.py` | Entrada `extra="forbid"`; separados de los modelos de tabla |
| Eager loading en repositorio | métodos de cada `repository.py` | Sin N+1 ni lazy loading |
| Trigger en BD | migración 4 | Sólo agregado de `movimiento_stock` |
| Punto único de escritura de stock | helper/servicio de `libros` (usado por alta, reposición y venta) | RN-11 |
| Sesión propia para auditoría | escritura de `intento_acceso` | Sobrevive al rollback del login fallido |

## Estructura obligatoria del proyecto (`parcial/`)

Nombres exactos de la consigna (págs. 8–9):

```
parcial/
├── main.py                         # app, lifespan y los dos grupos de rutas (abierto / protegido)   [*]
├── seed.py                         # deja la base en el estado inicial conocido (raíz de parcial/)
├── alembic.ini
├── requirements.txt
├── env.example                     # todas las variables, ningún secreto
├── README.md                       # integrantes + pasos desde cero
├── app/
│   ├── core/
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── database.py             # funciones que crean motor y fábrica de sesiones (las llama el lifespan) + get_session
│   │   ├── security.py             # bcrypt fuera del bucle (to_thread + semáforo); emisión y verificación del JWT
│   │   ├── dependencies.py         # usuario actual, roles vigentes, control del cambio obligatorio, requiere_rol
│   │   ├── repository.py           # BaseRepository[T], SoftDeleteRepository[T]
│   │   ├── paginacion.py           # envoltorio de listados y cálculo de páginas
│   │   └── unit_of_work.py         # UnitOfWork base (gestor de contexto asincrónico)
│   └── modules/
│       ├── health/                 # SÓLO router.py
│       ├── usuarios/               # + AsignacionRol, IntentoAcceso, EventoSeguridad
│       ├── editoriales/
│       ├── generos/
│       ├── autores/
│       ├── libros/                 # + LibroAutor, MovimientoStock
│       ├── clientes/               # + PerfilCliente
│       └── ventas/                 # + RenglonVenta
│           └── (cada módulo, salvo health:)
│               models.py  schemas.py  repository.py  unit_of_work.py  service.py  router.py
├── migrations/                     # configuración de Alembic y versiones (plantilla asincrónica)
├── test/                           # SOLO archivos .http y un único solo_agregado.sql
└── evidencia/                      # captura/consola de C-15 (2 y 4 renglones) y captura psql de C-14
```

`[*]` En la tabla del PDF dice `main.py`; **confirmado por el profesor (IN-03 resuelta)**: `app/main.py` (como el TP, `uvicorn app.main:app`) y `seed.py` en la raíz de `parcial/`.

**Material de cátedra:** está en `docs/catedra/` (cap1 a cap6, Markdown); las «secciones X.Y» de la consigna refieren a esos archivos. Regla: **buscar la sección puntual (Grep del encabezado), nunca leer el archivo entero**.

Responsabilidades por archivo de módulo:

| Archivo | Contenido |
|---|---|
| `models.py` | Modelos de tabla, restricciones y relaciones |
| `schemas.py` | Contratos de entrada y de salida |
| `repository.py` | Repositorios de cada entidad del módulo (métodos nombrados por lo que traen; precarga declarada adentro) |
| `unit_of_work.py` | UoW del módulo con los repositorios que sus operaciones necesitan, todos con la misma sesión |
| `service.py` | Reglas de negocio. **Recibe** el UoW y lo **abre** con `async with`; nunca lo construye; ya no recibe la sesión |
| `router.py` | Rutas HTTP: construyen el UoW (dependencia), llaman al servicio y traducen errores |

Módulos mínimos: `health`, `usuarios`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`.

## Restricción sobre las pruebas (instrucción del profesor)

`test/` contiene **ÚNICAMENTE archivos `.http` y un solo `solo_agregado.sql`**. **No se escribe pytest ni tests `.py`.** Los `.http` del TP (`test/C-01.http`..`C-08.http`) **se borran** de `parcial/test/` (siguen intactos en `despliegue/test/`); los del parcial se llaman `C-xx_tema.http` (p. ej. `C-05_limite_intentos.http`). Las pruebas son los casos C-01..C-16 en `.http` (cada uno con la respuesta esperada en un comentario; con REST Client, `# @name` y `# @no-cookie-jar` + `Cookie: {{loginAdmin.response.headers.Set-Cookie}}` para varias sesiones a la vez) y `solo_agregado.sql` para C-14. Antes de cada archivo se corre `python seed.py`. (Ver DD-02 en `09`.)

> Por el modo Strict TDD del orquestador: esta restricción del profesor tiene prioridad; la verificación se hace por los `.http` y consultas SQL, no por tests automatizados `.py`.

## Seguridad

- **Autenticación**: bcrypt (costo en config), JWT firmado (PyJWT), cookie `access_token` HttpOnly + SameSite=Lax + Max-Age + Secure configurable. Nunca por cabecera `Authorization` ni en el cuerpo.
- **Autorización**: roles vigentes leídos de la base en cada petición; roles del token informativos; 401 vs 403.
- **Anti-enumeración**: mismo mensaje y tiempo en el login (hash ficticio); límite de 5 intentos/60 s por (correo, IP).
- **Validación de entrada**: `extra="forbid"`, límite de 72 bytes en campos bcrypt, ninguna entrada inválida a 500.
- **SQL**: nunca armado por concatenación con datos del usuario (parámetros ligados).
- **Errores**: mensajes propios; nunca texto de la base ni traza (RN-15). Traducción de `IntegrityError`.
- **Secrets management**: sin valores por defecto en código; ni clave ni contraseña en código, `alembic.ini`, repo ni imagen; `env.example` sin secretos; `.env` no versionado ni en el zip.
- **Esquema**: sólo Alembic; sin `create_all`.
- **Transacciones**: ningún repositorio confirma; ningún servicio construye su UoW; el UoW no cierra la sesión.

## Variables de entorno (`parcial/`)

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `POSTGRES_USER` | Usuario de la base | `postgres` | N |
| `POSTGRES_PASSWORD` | Contraseña de la base (**sin default**) | `<definir>` | **Y** |
| `POSTGRES_DB` | Nombre de la base | `libreria` | N |
| `POSTGRES_HOST` | Servidor | `localhost` | N |
| `POSTGRES_PORT` | Puerto | `5432` | N |
| `JWT_SECRET` | Secreto de firma (**sin default**) | generar con `python -c "import secrets;print(secrets.token_hex(32))"` | **Y** |
| `JWT_MINUTOS` | Minutos de vida del token (y `Max-Age` de la cookie) | `30` | N |
| `BCRYPT_COSTO` | Rondas de bcrypt | `12` | N |
| `COOKIE_SECURE` | `Secure` de la cookie | `false` en local | N |
| `DB_POOL_SIZE` | Tamaño del pool del motor | `5` | N |
| `SQL_ECHO` | Ver consultas en consola (C-15) | `true` | N |

La URL de la base se arma en `Settings` con un `@computed_field` a partir de `POSTGRES_*` (driver `postgresql+asyncpg`). **Sin defaults** para `POSTGRES_PASSWORD` ni `JWT_SECRET` (P-03 resuelta). El semáforo de bcrypt (máx. hashes simultáneos) es una constante del módulo `security.py`, no variable de entorno.

## Dependencias (`requirements.txt` de `parcial/`)

El del TP más: `pydantic-settings>=2.0`, `bcrypt>=4.0`, `PyJWT>=2.8`. (El del TP ya trae fastapi[standard]>=0.111, sqlmodel>=0.0.24, SQLAlchemy[asyncio]>=2.0, asyncpg>=0.30, alembic>=1.13, python-dotenv>=1.0, uvicorn; **no** hay pytest: ver restricción.)

## Pasos del README de `parcial/` (lo exige la consigna)

Nombres y apellidos de los integrantes + desde cero: entorno virtual, dependencias, `.env` (con **cómo generar la clave de firma**), `alembic upgrade head`, `python seed.py`, arranque del servidor.
