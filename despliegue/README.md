# TP Librería — FastAPI + PostgreSQL (UTN Programación III, Unid. 1–4)

Avance por ejercicio de la consigna. `[X]` = completado y verificado, `[]` = pendiente.

## Cómo levantar el proyecto desde cero

Pasos para Windows con Git Bash (Python 3.12 o superior y PostgreSQL instalados):

1. Entrá a la carpeta del proyecto:
   ```bash
   cd TP_Libreria
   ```
2. Creá el entorno virtual (Python 3.12 o superior):
   ```bash
   py -3.13 -m venv .venv
   ```
3. Activalo:
   ```bash
   source .venv/Scripts/activate
   ```
4. Instalá las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Copiá el archivo de entorno y completá `DATABASE_URL` con tu contraseña de PostgreSQL. La variable es obligatoria: si falta o está vacía, la aplicación y Alembic muestran un error de configuración. Opcional: agregá `DEBUG=true` para ver las consultas SQL en la consola.
   ```bash
   cp .env.example .env
   ```
6. Creá la base vacía:
   ```bash
   psql -U postgres -c "CREATE DATABASE libreria;"
   ```
7. Aplicá las migraciones:
   ```bash
   alembic upgrade head
   ```
8. Levantá la API (el `--reload-dir app` evita reinicios en bucle cuando el `.venv` está dentro de la carpeta):
   ```bash
   uvicorn app.main:app --reload --reload-dir app
   ```
9. Abrí http://localhost:8000/docs
10. Sobre una base recién creada y migrada, ejecutá `python -m scripts.seed` antes de probar los endpoints. El script no borra datos y rechaza una base con registros. Deja cliente 1 con perfil, libros 1 y 2, y venta 1 (total `71000.00`) para los casos `.http`.

## Ejercicio 1 — Proyecto, conexión y ciclo de vida (10 pts)

- [X] Estructura modular (`app/core`, `app/modules/<modulo>`, `migrations/`, `test/`)
- [X] Entorno virtual `.venv` (Python 3.12) y `requirements.txt` con los mínimos (fastapi[standard]>=0.111, sqlmodel>=0.0.24, SQLAlchemy[asyncio]>=2.0, asyncpg>=0.30, alembic>=1.13, python-dotenv>=1.0, uvicorn). El extra `[asyncio]` instala `greenlet`, sin el cual `alembic upgrade head` falla en una instalación limpia
- [X] `.env.example` con `DATABASE_URL` (+ `.gitignore` cubre `.env` y `.venv`, sin credenciales en el repo)
- [X] Motor asincrónico + `async_sessionmaker(expire_on_commit=False)` + `get_session` (`app/core/`)
- [X] `lifespan`: recursos en `app.state`, motor cerrado al apagar (`app/main.py`)
- [X] `GET /health/live` (sin base) y `GET /health/ready` (`SELECT 1`, 503 con mensaje propio)

## Ejercicio 2 — Modelos, restricciones y relaciones (25 pts)

- [X] 9 tablas en singular con columnas obligatorias (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`)
- [X] `Decimal` para dinero (`precio` 10,2 / `total` 12,2 / `precio_unitario` 10,2), `fecha` con zona horaria
- [X] UNIQUE: `isbn`, `email`, `nombre` (editorial y género), `perfil_cliente.cliente_id`
- [X] Los 7 CHECK (`precio > 0`, `stock >= 0`, `cantidad > 0`, `precio_unitario > 0`, `orden >= 1`, `total >= 0`, `rol` en la lista cerrada)
- [X] Índice en cada FK y `Relationship(back_populates=...)` en los dos extremos
- [X] `LibroAutor` como entidad (PK compuesta + `rol` + `orden`); `Cliente.perfil` escalar
- [X] Imports de módulo al pie de cada `models.py` (cualquier módulo importa aislado sin `InvalidRequestError`)

## Ejercicio 3 — Migraciones (10 pts)

- [X] Alembic con plantilla asincrónica (URL desde `DATABASE_URL`, sin secretos en `alembic.ini`)
- [X] Migración 1 autogenerada **sin** `genero` ni `libro.genero_id` (correcciones comentadas en el archivo); `upgrade head` / `downgrade -1` / `upgrade head` verificados
- [X] Migración 2 autogenerada: tabla `genero` + `libro.genero_id` (nullable, índice y FK), con `import sqlmodel` agregado a mano y comentado; `downgrade -1` corregido (nombre explícito `libro_genero_id_fkey`) — ciclo `downgrade`/`upgrade` y `alembic check` ("No new upgrade operations") verificados contra PostgreSQL real

## Ejercicio 4 — Contratos y CRUD (15 pts)

- [X] DTOs por módulo (`Create` sin `id`, `Update` parcial con `exclude_unset`, `Read`)
  - [X] `editoriales` y `generos`: `Create` / `Update` de entrada y `Read` de salida, con `min_length` / `max_length`; se agregó `pais` a los DTOs de editorial
  - [X] `autores`, `libros`, `clientes`, `ventas`: contratos de entrada y salida completos
- [X] Códigos 201/404/409/422, `IntegrityError` → 409 con mensaje propio (RN-12)
  - [X] `editoriales` y `generos`: 404 desde el service ("Editorial no encontrada" / "Género no encontrado") y 409 desde `_guardar()`, que atrapa el `IntegrityError` del commit, hace rollback y responde con mensaje propio, sin consulta previa de unicidad
  - [X] El resto de los módulos: errores de integridad traducidos a mensajes propios
- [X] Paginación `limit`/`offset` (RN-10) y filtro de título con parámetro ligado (RN-11)
  - [X] `GET /editoriales/` y `GET /generos/` con `limit` (1 a 100, por defecto 20) y `offset` (desde 0) usando `Query`; fuera de rango da 422; la consulta usa `order_by(id)` para que las páginas sean estables
  - [X] Paginación en los otros módulos y filtros por título y género en libros (RN-11)
- [X] Rutas de colección con barra final en todos los módulos, como en la consigna
- [X] `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros` y `GET /autores/{id}/libros` (con rol y orden)

## Ejercicio 5 — Altas con relaciones: ids y datos (20 pts)

- [X] Alta de libro con `editorial_id`, `genero_id` y `autores` (`autor_id` + `rol` + `orden`); FK inexistente → 409 sin `if` previo
- [X] Alta de venta con `cliente_id` + `renglones` anidados; precio copiado del libro y total calculado por el servidor (RN-04 a RN-07); sin `PATCH` de ventas (RN-08)

## Ejercicio 6 — Lecturas sin N+1 (10 pts)

- [X] Carga anticipada (`joinedload` a uno, `selectinload` a colecciones); detalle de libro y de venta en N° fijo de consultas; cero carga perezosa

## Ejercicio 7 — Asincronía sin bloqueos (10 pts)

- [X] Handlers `async def` sin llamadas bloqueantes; aviso de comprobante con `BackgroundTasks` (`asyncio.sleep(0.5)` + log)

## Entrega

- [X] Archivos `TP_Libreria/test/` (en la raíz del proyecto, al nivel de `app/` y `migrations/`) C-01 a C-08 registrados, cada uno con su resultado esperado en comentarios
- [X] Script de datos iniciales `scripts/seed.py` y pruebas de C-01 a C-08 contra los endpoints
- [X] Evidencia C-07 en `docs/evidencia-C-07.txt`: 2 SELECT por detalle de libro y venta, con una o varias relaciones
- [X] Verificación final: `alembic upgrade head` sobre base vacía, app que levanta, `README` con pasos desde cero


## Verificación y notas de integración

- Los archivos originales `test/C-01.http` a `test/C-08.http` se conservan sin cambios.
- Verificado el 14/10/2026: casos C-01 a C-08 originales aprobados en PostgreSQL 16.15, upgrade desde cero, downgrade/upgrade, `alembic check`, seed y arranque/cierre de la API.
- Para observar C-07: activar `DEBUG=true`, iniciar la API y ejecutar `test/C-07.http`; las consultas se muestran en la consola. La evidencia guardada corresponde a la verificación realizada el 14/10/2026.
- Autor recibe `nombre` y `nacionalidad`. Libro recibe `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` opcional y `autores` con `autor_id`, `rol`, `orden`. PATCH conserva lo omitido; si se envía `autores`, reemplaza esa lista atómicamente. Sólo `genero_id` admite null.
- Se mantienen los modelos, migraciones y servicios de los demás módulos. En Editoriales y Géneros sólo se agregaron los listados de libros; en Ventas se agregó el aviso posterior a la respuesta, sin cambiar el cálculo de Lucas.
