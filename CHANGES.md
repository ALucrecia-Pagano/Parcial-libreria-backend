# CHANGES — Secuencia de Implementación (Parcial Librería, caps. 5 y 6)

> Índice canónico de los **15 changes** del parcial (CH-01..CH-15). Solo cubre el **delta** respecto del TP de los caps. 1–4 (ya implementado en `parcial/` y en `despliegue/`): no hay changes para CRUD de editoriales/géneros/autores/libros/clientes/ventas, migraciones 1–2, seed viejo ni los `.http` del TP.
> Cada change es **chico y autocontenido**: pensado para que una persona con una IA de contexto chico lo implemente leyendo solo este archivo + las secciones de la KB que se indican en "Leer antes".
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**
> **Material de cátedra**: está en `docs/catedra/` (cap1 a cap6, Markdown) y las «secciones X.Y» de la consigna refieren a esos archivos. Regla: **buscar la sección puntual (Grep del encabezado, p. ej. `^#+\s*6\.4\.3`), nunca leer el archivo entero**. Cada change lista abajo, en **Leer antes (cátedra)**, qué buscar. Los números de sección exactos (§X.Y) se completan con el Grep del encabezado la primera vez que alguien abre el archivo; los que ya cita la consigna figuran con su número (§2.9, §4.5). Al 03/11/2026 `docs/catedra/` no está todavía en el árbol de trabajo: copiarla antes de empezar.
> El prefijo **CH-xx** es de los changes. El prefijo **C-xx / D-xx** es de los casos de prueba de la consigna. **No mezclar.**

---

## Cómo usar este documento

1. Identificá tu change (la tabla "Mapa de personas" dice cuál es el tuyo) y mirá sus **Dependencias**: no arranques hasta que estén en `main` (salvo lo marcado como "arranque anticipado").
2. Leé solo lo de **Leer antes** (archivos de `knowledge-base/` con su sección) y abrí **como máximo** el archivo de **Imitar**.
3. Corré `/opsx:propose CH-NN-<nombre>`; el `tasks.md` sale de los campos "Archivos", "Entra" y ".http a correr" de este archivo.
4. Implementá, corré `python seed.py` y después los `.http` indicados (REST Client), comparando con los códigos esperados. **No se escribe pytest ni `.py` de test** (instrucción del profesor, DD-02): la prueba son los `.http` y `solo_agregado.sql`.
5. `/opsx:archive`, marcá el checkbox de **Estado** y avisá al grupo.

**Commits**: conventional commits **en español**, con el change entre paréntesis: `feat(CH-03): agrega Dockerfile con usuario sin privilegios`, `fix(CH-09): no registra el intento rechazado por 429`, `docs(CH-03): completa DEPLOY.md`, `chore(CH-01): agrega pydantic-settings`. Un commit por tarea lógica. (Los commits los hace cada persona; los agentes no commitean.)

**Reglas duras para todos los changes** (no se repiten abajo):
- Nada de credenciales reales en ningún archivo (solo datos ficticios tipo `admin@example.com`). Sin defaults para `POSTGRES_PASSWORD` ni `JWT_SECRET`.
- Esquema **solo con Alembic** (nada de `create_all`). Cada migración se **lee antes de aplicar** y lleva un comentario que lo diga.
- Ningún repositorio hace `commit` (solo `flush`); el servicio **recibe** el UoW y lo **abre** con `async with`; nunca lo construye.
- Unicidad **garantizada por la base**: no se verifica con una consulta previa; se atrapa el `IntegrityError` y se traduce a 409 con mensaje propio (RN-01, RN-15).
- Contratos de entrada con `extra="forbid"`; PATCH con `exclude_unset`; nunca se devuelve `password_hash`.
- El trabajo del parcial va **solo en `parcial/`**; `despliegue/` solo recibe lo de CH-03.

### Leyenda de governance (del CLAUDE.md global)
- **CRÍTICO**: auth, seguridad, auditoría → solo análisis y propuesta; esperar aprobación humana antes de escribir.
- **ALTO**: configuración/archivos que afectan datos, backup/restore, despliegue → proponer y esperar revisión antes de escribir.
- **MEDIO**: lógica de negocio, pipelines → implementar con checkpoints y mostrar las decisiones no obvias.
- **BAJO**: CRUD simple, tipos, utilitarios de lectura → autonomía total si los `.http` dan lo esperado.

### Convenciones compartidas (evitan conflictos entre personas)

| Convención | Regla |
|---|---|
| **Routers por módulo** | Cada módulo expone hasta tres `APIRouter`: `router_abierto` (sin rol), `router_admin` (solo ADMIN), `router_staff` (VENDEDOR o ADMIN). **Sin guardas adentro**: los guardas los pone `main.py` al montarlos (lo hace CH-10). Hasta que CH-10 esté en `main`, los cambios los montan todos en una lista plana en `app/main.py`; después de CH-10, quien integre monta cada router en el grupo que corresponde. |
| **`app/main.py`** | Zona de conflicto. Regla: cada change **agrega solo sus líneas `include_router`**; CH-10 es el único que reestructura en dos grupos (abierto / protegido). |
| **`app/core/errores.py`** (lo crea CH-02) | `traducir_integrity_error(exc)` busca el **nombre del constraint** en un diccionario `MENSAJES_CONSTRAINT` y devuelve 409 con mensaje propio; nunca texto de la base. Cada change **agrega sus entradas** al diccionario. Por eso CH-01 nombra explícitamente todos los constraints (ver CH-01). |
| **Nombres de `.http`** | En `parcial/test/`: `C-xx_tema.http` (un caso de la consigna; p. ej. `C-05_limite_intentos.http`) o `CH-NN_tema.http` (verificación auxiliar de un change que no es un caso C). Los casos D, si llevan `.http`, serían `D-xx_tema.http` (la evidencia D vive en `despliegue/evidencia/`). Cada pedido lleva la respuesta esperada **en un comentario**. Antes de cada archivo: `python seed.py`. **Decidido (DD-29)**: los `C-01.http`..`C-08.http` del TP se **borran** de `parcial/test/` (los hace CH-02; siguen intactos en `despliegue/test/`). |
| **Varias sesiones en un `.http`** | `# @name loginAdmin` en cada login y, en los pedidos de esa sesión, `# @no-cookie-jar` + `Cookie: {{loginAdmin.response.headers.Set-Cookie}}`. |
| **Usuarios del seed** | `admin@example.com`, `admin2@example.com` (ADMIN), `vendedor@example.com` (VENDEDOR), `ana@example.com` (CLIENTE, ficha "Ana Paz"), `nuevo@example.com` (VENDEDOR con `debe_cambiar_password=true`). Las contraseñas de mentira viven **solo** en `seed.py`. |

---

## Mapa de personas (5 partes, 3 changes cada una)

| Parte | Persona | Changes |
|---|---|---|
| 1. Base y despliegue | Amanda | CH-01, CH-02, CH-03 |
| 2. Catálogo y stock | Persona 2 | CH-04, CH-05, CH-06 |
| 3. Autenticación | Persona 3 | CH-07, CH-08, CH-09 |
| 4. Autorización | Persona 4 | CH-10, CH-11, CH-12 |
| 5. Clientes y ventas | Persona 5 | CH-13, CH-14, CH-15 |

(Los nombres de los integrantes están en `knowledge-base/README.md`; el reparto de partes a personas lo define el grupo. Quien quede libre en un gate puede tomar un change de otra parte: lo único que importa son las dependencias.)

---

## Tabla resumen

| Change | Nombre | Parte | Governance | Depende de | Tamaño |
|---|---|---|---|---|---|
| CH-01 | `base-config-modelos-migracion-3` | 1 | ALTO | — | M |
| CH-02 | `migracion-4-seed-y-clases-base` | 1 | ALTO | CH-01 | M |
| CH-03 | `despliegue-docker-vps` | 1 | ALTO | — (independiente) | M |
| CH-04 | `catalogo-auxiliar-repo-uow` | 2 | MEDIO | CH-01, CH-02 | M |
| CH-05 | `libros-baja-logica-patch-sin-stock` | 2 | MEDIO | CH-01, CH-02 | M |
| CH-06 | `stock-punto-unico-reponer-movimientos` | 2 | ALTO | CH-02, CH-05, **CH-10** (agregada) | M |
| CH-07 | `security-login-cookie` | 3 | CRÍTICO | CH-01, CH-02 | G |
| CH-08 | `registro-logout-yo` | 3 | CRÍTICO | CH-07 (y CH-10 solo para `/auth/yo`) | M |
| CH-09 | `intento-acceso-limite-429` | 3 | CRÍTICO | CH-07 | M |
| CH-10 | `usuario-actual-roles-dos-grupos` | 4 | CRÍTICO | CH-01, CH-02, CH-07 | M |
| CH-11 | `cambiar-password-cambio-obligatorio` | 4 | CRÍTICO | CH-10 | P |
| CH-12 | `roles-vigencia-alta-personal-eventos` | 4 | CRÍTICO | CH-10 | G |
| CH-13 | `clientes-repo-uow-usuario-id` | 5 | MEDIO | CH-01, CH-02, CH-10 | M |
| CH-14 | `venta-rn10-mis-ventas-dueno` | 5 | ALTO | CH-06, CH-10 | G |
| CH-15 | `sin-n-mas-1-background-solo-agregado` | 5 | BAJO | CH-14, CH-06, CH-02 | M |

Tamaño: P = pocas horas, M = media jornada, G = jornada completa.

---

## Árbol de dependencias

```
CH-03 (independiente: despliegue/, puede arrancar ya)

CH-01 base-config-modelos-migracion-3
 └── CH-02 migracion-4-seed-y-clases-base
      ├── CH-04 catalogo-auxiliar-repo-uow
      ├── CH-05 libros-baja-logica-patch-sin-stock
      │    └── CH-06 stock-punto-unico-reponer-movimientos  (también espera a CH-10)
      │         └── CH-14 venta-rn10-mis-ventas-dueno       (también espera a CH-10)
      │              └── CH-15 sin-n-mas-1-background-solo-agregado
      └── CH-07 security-login-cookie
           ├── CH-08 registro-logout-yo     (tarea /auth/yo espera a CH-10)
           ├── CH-09 intento-acceso-limite-429
           └── CH-10 usuario-actual-roles-dos-grupos
                ├── CH-06 (ver arriba)
                ├── CH-11 cambiar-password-cambio-obligatorio
                ├── CH-12 roles-vigencia-alta-personal-eventos
                ├── CH-13 clientes-repo-uow-usuario-id
                └── CH-14 (ver arriba)
```

### Paralelismo por gate

```
GATE 0: (arranque) ✓
  → CH-01 base-config-modelos-migracion-3        [Amanda]
  → CH-03 despliegue-docker-vps                   [Amanda, o quien tenga acceso a EasyPanel — independiente]

GATE 1: CH-01 ✓
  → CH-02 migracion-4-seed-y-clases-base          [Amanda]   ← cuello de botella: todos esperan a CH-02
     (arranque anticipado permitido: borrador de security.py de CH-07, que solo necesita Settings de CH-01)

GATE 2: CH-02 ✓                                   ← FORK
  → CH-04 catalogo-auxiliar-repo-uow              [Persona 2]
  → CH-05 libros-baja-logica-patch-sin-stock      [Persona 4, libre hasta que CH-07 termine]
  → CH-07 security-login-cookie                   [Persona 3]

GATE 3: CH-07 ✓                                   ← FORK
  → CH-08 registro-logout-yo (sin /auth/yo)       [Persona 3]
  → CH-09 intento-acceso-limite-429               [Persona 5, libre hasta CH-10]
  → CH-10 usuario-actual-roles-dos-grupos         [Persona 4]

GATE 4: CH-10 ✓ (y CH-05 ✓)                       ← FORK (4 ramas)
  → CH-06 stock-punto-unico-reponer-movimientos   [Persona 2 — si CH-05 ✓]
  → CH-11 cambiar-password-cambio-obligatorio     [Persona 4]
  → CH-12 roles-vigencia-alta-personal-eventos    [Persona 3 — tras CH-08]
  → CH-13 clientes-repo-uow-usuario-id            [Persona 5]
  → cierre de CH-08: /auth/yo                     [Persona 3]

GATE 5: CH-06 ✓ y CH-10 ✓
  → CH-14 venta-rn10-mis-ventas-dueno             [Persona 5 — tras CH-13]

GATE 6: CH-14 ✓ y CH-06 ✓
  → CH-15 sin-n-mas-1-background-solo-agregado    [Persona 5]
```

### Camino crítico (7 changes — mínimo irreducible)

`CH-01 → CH-02 → CH-07 → CH-10 → CH-06 → CH-14 → CH-15`

CH-03 queda fuera del camino crítico (independiente). CH-04, CH-05, CH-08, CH-09, CH-11, CH-12 y CH-13 cuelgan del camino sin alargarlo.

### Plan con 5 personas

| Paso | Amanda | Persona 2 | Persona 3 | Persona 4 | Persona 5 |
|---|---|---|---|---|---|
| 1 | CH-01 | leer KB | leer KB (borrador de `security.py`) | leer KB | leer KB |
| 2 | CH-02 | leer KB | — | — | — |
| 3 | CH-03 | CH-04 | CH-07 | CH-05 | apoyo/revisión de CH-02 |
| 4 | CH-03 (cierre) / revisión | — | CH-08 (sin `/auth/yo`) | CH-10 | CH-09 |
| 5 | apoyo / evidencia D | CH-06 | CH-12 (y `/auth/yo` de CH-08) | CH-11 | CH-13 |
| 6 | apoyo | revisión | revisión | revisión | CH-14 |
| 7 | README / entrega | — | — | — | CH-15 |

### Dependencias agregadas respecto de lo pedido (y por qué)

| Dependencia | Justificación |
|---|---|
| **CH-02 → CH-01** | La migración 4 necesita la tabla `movimiento_stock` (migración 3) y el seed necesita todos los modelos. |
| **CH-06 → CH-05** | Mismo módulo `libros` (repositorio con baja lógica, `SoftDeleteRepository`); reponer sobre un libro dado de baja da 409 (RN-13). |
| **CH-06 → CH-10** (confirmada, DD-32) | `movimiento_stock.usuario_id` es NOT NULL (P-01): alta y reposición necesitan el usuario autenticado (`get_usuario_actual`), y el `.http` de C-13 necesita sesión de ADMIN. Esto alarga el camino crítico en un change, pero evita inventar un "actor provisorio". |
| **CH-08 → CH-10 (solo la tarea `/auth/yo`)** | `/auth/yo` necesita `get_usuario_actual`. Registro y logout no esperan; el change se **archiva** recién cuando CH-10 está en `main`. |
| **CH-15 → CH-06 y CH-02** | Mide consultas de movimientos y usa el disparador de la migración 4 (C-14). |
| Dependencias que se evitaron a propósito | CH-02 **no** depende de CH-07: `seed.py` hashea con `bcrypt` directo (script de un solo uso). CH-10 **no** depende de CH-04/05/06: por la convención de routers, `main.py` pone los guardas al montar. CH-05 **no** depende de CH-04: usa `BaseRepository(session, Editorial)` genérico para validar ids. CH-14 **no** depende de CH-13: usa `BaseRepository(session, Cliente)` genérico y define `GET /clientes/{id}/ventas` en el módulo ventas. CH-08 **no** depende de CH-13: crea la ficha de cliente con el repositorio genérico. |

---

# PARTE 1 — Base y despliegue (Amanda)

### [CH-01] `base-config-modelos-migracion-3`
- **Estado**: `[x]` hecho (archivado 04/11/2026 en `openspec/changes/archive/2026-11-04-ch-01-base-config-modelos-migracion-3/`)
- **Objetivo**: dejar el proyecto con configuración sin secretos por defecto, ciclo de vida correcto, salud, todos los modelos nuevos y la migración 3 autogenerada y corregida.
- **Entra**:
  - `Settings` (pydantic-settings) con `POSTGRES_USER/PASSWORD/DB/HOST/PORT`, `JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO`, `COOKIE_SECURE`, `DB_POOL_SIZE`, `SQL_ECHO`; URL de la base con `@computed_field` (driver `postgresql+asyncpg`); **sin default** para `POSTGRES_PASSWORD` ni `JWT_SECRET` (si faltan, la app no arranca). Lee de entorno/`.env` no versionado.
  - `database.py`: funciones que crean motor (con `pool_size=DB_POOL_SIZE`, `echo=SQL_ECHO`) y fábrica de sesiones (`expire_on_commit=False`), que las llama el **lifespan** y guarda en `app.state`; `get_session` (una sesión por petición, la cierra al terminar); `dispose()` al apagar.
  - `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`, **503** si la base no contesta). Módulo `health` solo con `router.py`.
  - Modelos nuevos en `modules/usuarios/models.py`: `Usuario`, `AsignacionRol` (CHECK de rol, índice único parcial `(usuario_id, rol) WHERE revocada_en IS NULL`, `otorgada_por` FK nullable con índice), `IntentoAcceso` (índice `(email, ip, cuando)`), `EventoSeguridad`. `MovimientoStock` en `modules/libros/models.py` (CHECK `cantidad <> 0`, `usuario_id` NOT NULL, `venta_id` nullable, índice en cada FK).
  - Cambios: `Cliente.usuario_id` (nullable, UNIQUE, `Cliente.usuario` devuelve un objeto, relación en los dos extremos); `Libro.borrado_en` y el UNIQUE de `isbn` reemplazado por índice único parcial `(isbn) WHERE borrado_en IS NULL`.
  - **Nombrar los constraints explícitamente** (los usa `errores.py` de CH-02): `uq_usuario_email`, `uq_cliente_email`, `uq_cliente_usuario_id`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn_vigente`, `uq_asignacion_rol_abierta`.
  - Migración 3 con `alembic revision --autogenerate`, **leída y corregida a mano** (el UNIQUE viejo de `isbn` y el índice parcial no los resuelve bien el autogenerate), con comentario que lo diga. Probar `upgrade head` → `downgrade base` → `upgrade head`.
  - `alembic` toma la URL de `Settings` (ninguna URL ni contraseña en `alembic.ini`).
  - `requirements.txt` + `pydantic-settings>=2.0`, `bcrypt>=4.0`, `PyJWT>=2.8`. `parcial/env.example` con todas las variables y ningún secreto (comentario de cómo generar `JWT_SECRET`).
- **No entra**: `security.py`, hash ficticio (CH-07), `dependencies.py` (CH-10), repositorios/UoW (CH-02), seed, disparador.
- **Governance**: ALTO (configuración y secretos; migración que cambia datos).
- **Dependencias**: ninguna.
- **Archivos**:
  - Crear: `parcial/app/modules/usuarios/__init__.py`, `parcial/app/modules/usuarios/models.py`, `parcial/env.example`, `parcial/migrations/versions/<rev>_acceso_y_movimiento_stock.py`.
  - Modificar: `parcial/app/core/config.py`, `parcial/app/core/database.py`, `parcial/app/main.py` (lifespan), `parcial/app/modules/health/router.py`, `parcial/app/modules/libros/models.py`, `parcial/app/modules/clientes/models.py`, `parcial/app/modules/editoriales/models.py` (nombra `uq_editorial_nombre`), `parcial/app/modules/generos/models.py` (nombra `uq_genero_nombre`), `parcial/app/modules/ventas/models.py` (`Venta.movimientos`, navegación en los dos extremos), `parcial/migrations/env.py`, `parcial/alembic.ini`, `parcial/requirements.txt`, `parcial/README.md` (pasos que nombraban `.env.example` / `DATABASE_URL`), `parcial/.gitignore` (comentario que nombraba `.env.example`).
  - Borrar: `parcial/.env.example` (tenía `DATABASE_URL`, que deja de existir; lo reemplaza `parcial/env.example`).
  - _Ampliado al proponer (03/11/2026)_: los modelos de editoriales, géneros y ventas, el README, el `.gitignore` y el borrado de `.env.example` se sumaron para que modelo y base queden sincronizados (sin diferencias falsas en `alembic check`) y para declarar toda relación nueva en los dos extremos (lo exige la consigna).
- **Imitar**: `parcial/app/core/database.py` (`init_resources` / `dispose_resources` ya existen en el TP; se adaptan) y `parcial/app/modules/ventas/models.py` (estilo de relaciones en los dos extremos).
- **RN**: RN-01 (UNIQUE e índice parcial de ISBN), RN-03 (índice parcial de roles; el 409 lo da CH-12), base de RN-12.
- **Casos C/D**: ninguno directo (es la base de todos). Verificación propia del Ej. 1 y 2.
- **.http a correr**: `parcial/test/CH-01_salud.http` (crear): `GET /health/live` → 200; `GET /health/ready` → 200; con la base apagada → 503. Más consola: `alembic upgrade head`, `downgrade base`, `upgrade head` sin errores; sin `POSTGRES_PASSWORD` la app **no arranca**.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap4-persistencia.md` §4.5 — El motor y la sesión (pool declarado en la configuración; la consigna cita «sec. 4.5»; `expire_on_commit=False`)
  - `docs/catedra/cap1-fastapi.md` §1.9 — Recursos y ciclo de vida (lifespan, `app.state`)
  - `docs/catedra/cap3-asincronia.md` §3.10 — Recursos y ciclo de vida (motor y fábrica creados y liberados en el lifespan)
  - `docs/catedra/cap1-fastapi.md` §1.12 — Los ocho servicios (subsección «PostgreSQL y Redis fallan distinto», para `/health`)
  - `docs/catedra/cap4-persistencia.md` §4.4 — SQLModel: qué une, y qué no conviene unir
  - `docs/catedra/cap4-persistencia.md` §4.6 — Relaciones y carga anticipada (la consigna cita «sec. 4.6»)
  - `docs/catedra/cap4-persistencia.md` §4.10 — Índices y restricciones
  - `docs/catedra/cap4-persistencia.md` §4.11 — Migraciones: el esquema como código versionado
  - `docs/catedra/cap4-persistencia.md` §4.13 — Seguridad y evolución (la consigna lo cita)
  - `docs/catedra/cap1-fastapi.md` §1.15 — Seguridad y evolución (secretos fuera del código)
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` (§Tablas nuevas, §Tablas que cambian, §Los dos índices únicos parciales, §Migraciones)
  - `knowledge-base/06_funcionalidades.md` (§E1, §E2)
  - `knowledge-base/08_arquitectura_propuesta.md` (§Variables de entorno, §Estructura obligatoria)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-04, DD-16, SU-04)

### [CH-02] `migracion-4-seed-y-clases-base`
- **Estado**: `[x]` hecho (archivado 04/11/2026 en `openspec/changes/archive/2026-11-04-ch-02-migracion-4-seed-y-clases-base/`)
- **Objetivo**: disparador de sólo agregado, `seed.py` del parcial y las clases base que usan todos los demás changes.
- **Entra**:
  - Migración 4 **escrita a mano**: función PL/pgSQL + `CREATE TRIGGER ... BEFORE UPDATE OR DELETE ON movimiento_stock FOR EACH ROW` que levanta excepción (RN-12). `downgrade` quita disparador y función. Comentario de que se escribió a mano porque la comparación automática no ve funciones ni disparadores.
  - `seed.py` en la **raíz de `parcial/`**: **vacía las tablas con `TRUNCATE ... RESTART IDENTITY CASCADE`** (un `DELETE` lo frenaría el disparador) y carga (la secuencia de ids vuelve a 1 por `RESTART IDENTITY`: los `.http` usan ids fijos como libro 1 o venta 1): 5 usuarios (hash con `bcrypt` directo, sin `security.py`), 3 editoriales, 3 géneros, 6 autores, 5 libros (dataset completo y **ficticio** en el siguiente punto), clientes Lucía (con perfil), Tomás y Ana (con `usuario_id` de `ana@example.com`), venta 1 de Lucía por `vendedor@example.com` (1 Rayuela + 2 Ficciones = 69000.00), movimientos ("Stock inicial" por libro hecho por `admin@example.com`, con Rayuela 11 y Ficciones 10; motivo "Venta" -1 y -2 para la venta 1) y un `evento_seguridad` con actor `SISTEMA` ("Carga de los datos iniciales"). `asignacion_rol.otorgada_por` = NULL. Invariante: `libro.stock = SUM(movimiento_stock.cantidad)` en los 5 libros.
  - **Dataset del seed (todo ficticio salvo los precios del TP; DD-26)**:
    - Editoriales: 1 Letras del Río, 2 Ediciones del Plata Sur, 3 Editorial Sudamérica Austral.
    - Géneros: 1 Novela, 2 Cuento, 3 Antología.
    - Autores: 1 Julio Cortázar, 2 Jorge Luis Borges, 3 Silvina Ocampo, 4 Adolfo Bioy Casares, 5 Ricardo Piglia, 6 Juan José Saer (sin libro).
    - Libros (id, título, ISBN, precio, stock, autores, editorial, género): 1 Rayuela `978-950-00-0001-1` 25000.00 stock 10, Cortázar, ed. 1, Novela. 2 Antología de la literatura fantástica `978-950-00-0002-8` 30000.00 stock 5, Borges + Ocampo + Bioy Casares, ed. 2, Antología. 3 Ficciones `978-950-00-0003-5` 22000.00 stock 8, Borges, ed. 3, Cuento. 4 Respiración artificial `978-950-00-0004-2` 27000.00 stock 3, Piglia, ed. 2, Novela. 5 Bestiario `978-950-00-0005-9` **18000.00** (ficticio) stock 1, Cortázar, ed. 3, Cuento.
    - Sin marca `PROVISORIO`: P-06 está resuelta.
  - **Borrar** `parcial/test/C-01.http`..`C-08.http` (los del TP; siguen intactos en `despliegue/test/`). Después, en `parcial/test/` solo quedan `C-xx_tema.http`, `CH-NN_tema.http` y `solo_agregado.sql` (DD-29).
  - `app/core/repository.py`: `BaseRepository[T]` (constructor recibe **sesión y clase del modelo**; `get_by_id`, `get_all`, `count`, `add`, `update`, `delete`; `add`/`update` hacen `flush()`, nunca `commit()`) y `SoftDeleteRepository[T]` (filtra bajas; `get_by_id_including_deleted`, `soft_delete`).
  - `app/core/unit_of_work.py`: `UnitOfWork` base, gestor de contexto asincrónico: confirma al salir, revierte si sale con excepción, **no cierra la sesión**.
  - `app/core/paginacion.py`: dependencia `page>=1`, `size` 1..100 (default 20); envoltorio `{items, total, page, size, pages}`; cero resultados → `pages=1` y una página vacía; `page > pages` → **422** «La página 4 no existe: hay 3» (con los números que correspondan); `total` cuenta con los mismos filtros que la página.
  - `app/core/errores.py`: `traducir_integrity_error` con diccionario `MENSAJES_CONSTRAINT` (nombre de constraint → mensaje propio 409; nunca texto de la base) — RN-15.
- **No entra**: repositorios/UoW de módulos (los hacen CH-04, 05, 06, 07, 13, 14), `security.py`.
- **Governance**: ALTO (migración, seed destructivo, disparador).
- **Dependencias**: CH-01.
- **Archivos**:
  - Eliminar: `parcial/test/C-01.http`, `C-02.http`, `C-03.http`, `C-04.http`, `C-05.http`, `C-06.http`, `C-07.http`, `C-08.http` (del TP).
  - Crear: `parcial/migrations/versions/<rev>_movimiento_stock_solo_agregado.py`, `parcial/seed.py`, `parcial/app/core/repository.py`, `parcial/app/core/unit_of_work.py`, `parcial/app/core/paginacion.py`, `parcial/app/core/errores.py`.
  - Modificar: nada del TP (salvo el borrado de los `.http` viejos).
- **Imitar**: `parcial/scripts/seed.py` (solo para ver cómo abre sesión y crea entidades del TP; **no copiar** su lógica de "rechazar si hay datos") y `parcial/migrations/versions/0f5ab569096b_agrega_tabla_genero_y_relacion_con_libro.py` (formato de migración).
- **RN**: RN-12, RN-15 (base), RN-16 (línea `SISTEMA`), base de RN-11.
- **Casos C/D**: deja listo el estado inicial de todos los C; C-14 se demuestra en CH-15 (el disparador nace acá).
- **.http a correr**: no hay endpoints nuevos. Verificación: `alembic upgrade head`/`downgrade base`/`upgrade head`; `python seed.py` dos veces seguidas sin error y con los mismos ids (libro 1 = Rayuela, venta 1 = la de Lucía; confirma `RESTART IDENTITY`); `ls parcial/test/` sin los `C-0x.http` del TP; consulta SQL: suma de movimientos = `libro.stock` en los 5 libros; en `psql`, `UPDATE`/`DELETE` sobre `movimiento_stock` → error del disparador.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap4-persistencia.md` §4.11 — Migraciones: el esquema como código versionado (migración escrita a mano)
  - `docs/catedra/cap4-persistencia.md` §4.10 — Índices y restricciones (los CHECK no cruzan tablas: de ahí el disparador)
  - `docs/catedra/cap4-persistencia.md` §4.9 — Borrado lógico: una enumeración taxativa (por qué no se borran movimientos de stock)
  - `docs/catedra/cap6-uow-transacciones.md` §6.4 — El repositorio (incl. 6.4.3 «Los genéricos que se borran» y 6.4.4 «El catálogo de métodos…»)
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap2-contratos.md` §2.9 — Colecciones: envoltorio, paginación y ordenamiento (la consigna cita «sec. 2.9»)
  - `docs/catedra/cap2-contratos.md` §2.10 — Errores: un formato normado (traducción de `IntegrityError` a 409)
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` (§Seed data inicial, §Migraciones, §`movimiento_stock`)
  - `knowledge-base/06_funcionalidades.md` (§E6, §E7, §E3 paginación)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-12, RN-15, §Reglas derivadas: paginación)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-07, DD-13, DD-14, DD-26, DD-29, DD-31)
  - `knowledge-base/10_preguntas_abiertas.md` (P-06, resuelta)

### [CH-03] `despliegue-docker-vps`
- **Estado**: `[x]` hecho (archivado 04/11/2026 en `openspec/changes/archive/2026-11-04-ch-03-despliegue-docker-vps/`)
- **Objetivo**: poner el TP caps. 1–4 (carpeta `despliegue/`, **sin tocar su lógica**) en un contenedor y en el VPS, con la evidencia D-01..D-08.
- **Entra**:
  - `despliegue/Dockerfile` desde `python:3.12-alpine` (sin compilador; copia e instala `requirements.txt` con `--no-cache-dir` **antes** de copiar el código; usuario sin privilegios con `USER`; sin secretos; arranque `alembic upgrade head` y luego `uvicorn app.main:app --host 0.0.0.0 --port 8000`; `HEALTHCHECK --interval=30s --retries=3 --start-period=20s` sobre `http://127.0.0.1:8000/health/ready` con `wget`, **no** `localhost`).
  - Revisar que `despliegue/.dockerignore` excluya `.env`, `.venv`, `.git`, `__pycache__` (ya existe; solo ajustar si falta algo).
  - `despliegue/env.example` (nuevo; forma de `DATABASE_URL` con `<usuario>:<contraseña>@<host>:5432/<base>` y `SQL_ECHO=false`; el `.env.example` del TP **no se toca**).
  - `despliegue/DEPLOY.md`: URL pública, día y hora, comandos `docker build` y `docker run` completos (nombre del archivo de variables, **sin su contenido**), cambios hechos al TP (ninguno si no hubo), cómo se actualiza (`docker rm -f libreria` + build + run), nota de que el TP lee `DEBUG` y no `SQL_ECHO` (IN-06), y que el TP ya trae `BackgroundTasks` en `ventas/tasks.py` (P-18).
  - Rol propio `libreria` (`LOGIN`, contraseña alfanumérica) y base `libreria` (`OWNER libreria`; no se usa el usuario `calculadora`) creados **a mano por Amanda** en el PostgreSQL 17 existente de EasyPanel (servicio `db`, proyecto `calculadora`; host interno `calculadora_db`, 5432 sin exponer; red overlay attachable `--network easypanel-calculadora`). **Fallback corregido (DD-27)**: si fallara la conexión al PostgreSQL existente o a la red overlay, se levanta un contenedor Postgres propio con `docker run` en una red `bridge` dedicada (`libreria-net`) y se documenta en `DEPLOY.md`. Archivo de variables **solo en el servidor** (`--env-file /root/libreria.env`), fuera del repo y la imagen.
  - `despliegue/evidencia/` con la salida de **D-01..D-08**. Datos iniciales: `docker exec libreria python -m scripts.seed`.
  - Si el TP no arranca en el contenedor por un defecto propio, se corrige y se anota en `DEPLOY.md` (regla de Ej. 9).
- **No entra**: cambios de lógica del TP, docker compose, nada de `parcial/`.
- **Governance**: ALTO (credenciales, servidor; la contraseña de la base **nunca** en un archivo).
- **Dependencias**: ninguna (independiente; puede arrancar ya).
- **Archivos**:
  - Crear: `despliegue/Dockerfile`, `despliegue/env.example`, `despliegue/DEPLOY.md`, `despliegue/evidencia/` (un archivo de texto/captura por caso D), `README.md` (raíz, con el link al VPS).
  - Modificar: `despliegue/.dockerignore` (solo si falta una entrada).
- **Imitar**: `despliegue/.dockerignore` y `despliegue/.env.example` (formato de variables del TP).
- **RN**: ninguna (requisitos no funcionales: sin secretos, no root).
- **Casos C/D**: **D-01..D-08**.
- **.http a correr**: no hay en `test/`; las pruebas D se corren desde afuera del VPS contra la URL pública: `GET /health/ready` → 200; `GET /libros/` → 200 con la lista; `POST /ventas/` (cuerpo de ejemplo del TP) → 201 con precios copiados y total. D-08: el aviso del comprobante aparece en `docker logs libreria` después de la línea de la respuesta.
- **Resuelto (P-04 / IN-08 / DD-27)**: URL pública `http://179.199.141.99:8000` (`-p 8000:8000`), red `--network easypanel-calculadora` (`Attachable: true`), rol y base `libreria` en `calculadora_db:5432` (PostgreSQL 17), y fallback con contenedor Postgres propio en red `bridge` (`libreria-net`).
- **Pendiente (P-05)**: nombre del grupo y fecha: `<NOMBRE>` / `<FECHA>`.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - Docker **no tiene capítulo** en el material de cátedra: este change se apoya sólo en la consigna (E9 y E10) y en `knowledge-base/13_despliegue.md`. No buscar en `docs/catedra/`.
- **Leer antes**:
  - `knowledge-base/13_despliegue.md` (todo: §Infraestructura, §Ejercicio 9, §Ejercicio 10, §`DEPLOY.md`)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (§Casos D)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-03, DD-11, DD-20, DD-22, DD-23, DD-25, DD-27)
  - `knowledge-base/10_preguntas_abiertas.md` (IN-06, IN-08, P-04, P-05)

---

# PARTE 2 — Catálogo y stock (Persona 2)

### [CH-04] `catalogo-auxiliar-repo-uow`
- **Estado**: `[ ]` pendiente
- **Objetivo**: llevar editoriales, géneros y autores a capas repositorio + Unit of Work, con envoltorio de listado y contratos estrictos.
- **Entra**:
  - Por cada módulo (`editoriales`, `generos`, `autores`): `repository.py` (hereda de `BaseRepository`), `unit_of_work.py`, `service.py` que **recibe** el UoW y lo abre con `async with`, `router.py` que arma el UoW con una dependencia y se lo pasa al servicio.
  - Routers separados `router_abierto` / `router_admin` (convención).
  - Endpoints: `GET /editoriales` y `GET /generos` (`page`, `size`) → 200, 422 (envoltorio `{items,total,page,size,pages}`); `POST /editoriales`, `/generos`, `/autores` → 201, 409, 422; `PATCH /editoriales/{id}`, `/autores/{id}` → 200, 404, 409, 422. **No existe `PATCH /generos`** (si el TP lo trae, se elimina).
  - Schemas de entrada con `extra="forbid"`; PATCH con `exclude_unset`; respuestas separadas de los modelos de tabla.
  - Nombre repetido (editorial, género) → 409 con mensaje propio vía `traducir_integrity_error` (entradas `uq_editorial_nombre`, `uq_genero_nombre` en `MENSAJES_CONSTRAINT`), **sin consulta previa**.
- **No entra**: `GET /{x}/{id}/libros` (los hace CH-05), guardas de rol (CH-10).
- **Governance**: MEDIO (refactor de capas con 3 módulos).
- **Dependencias**: CH-01, CH-02.
- **Archivos**:
  - Crear: `parcial/app/modules/{editoriales,generos,autores}/repository.py`, `.../unit_of_work.py`, `parcial/test/CH-04_editoriales_generos_autores.http`.
  - Modificar: `.../service.py`, `.../router.py`, `.../schemas.py` de los tres módulos; `parcial/app/core/errores.py` (agrega entradas); `parcial/app/main.py` (solo `include_router` de los dos routers de cada módulo).
  - **Nota**: `parcial/app/modules/editoriales/models.py` y `parcial/app/modules/generos/models.py` **ya vienen modificados por CH-01** (nombran `uq_editorial_nombre` y `uq_genero_nombre`, que la migración 3 renombra en la base). No volver a tocarlos: partir de lo que dejó CH-01.
- **Imitar**: `parcial/app/modules/editoriales/service.py` y `router.py` del TP (punto de partida) y, para la forma de las clases base, `parcial/app/core/repository.py` (CH-02).
- **RN**: RN-01 (nombre de editorial y género), RN-11 (`extra="forbid"` como patrón), RN-15.
- **Casos C/D**: apoya C-16 (paginación y PATCH parcial) en el catálogo auxiliar.
- **.http a correr**: `CH-04_editoriales_generos_autores.http`:
  - `GET /editoriales?size=2` → 200 con `items,total,page,size,pages`; `GET /editoriales?page=99` → 422 «La página 99 no existe: hay N»; `size=500` → 422.
  - `POST /generos` nombre repetido → 409 con mensaje propio (sin texto de base).
  - `PATCH /editoriales/1` con un solo campo → 200 y solo cambia ese; con campo extra → 422; `PATCH /editoriales/9999` → 404.
  - `PATCH /generos/1` → 404/405 (la ruta no existe).
  - `POST /autores` sin nombre → 422.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap6-uow-transacciones.md` §6.4 — El repositorio (6.4.4 «El catálogo de métodos…»)
  - `docs/catedra/cap6-uow-transacciones.md` §6.5 — La tabla de precarga es parte del contrato
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap1-fastapi.md` §1.10 — Las capas (Router, Service, Repository)
  - `docs/catedra/cap2-contratos.md` §2.5 — Modelos segregados: por qué tres y no uno
  - `docs/catedra/cap2-contratos.md` §2.6 — Actualización parcial: ausente contra nulo (`exclude_unset`)
  - `docs/catedra/cap2-contratos.md` §2.8 — Los verbos y sus códigos
  - `docs/catedra/cap2-contratos.md` §2.9 — Colecciones: envoltorio, paginación y ordenamiento
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (§E3, §E6)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (§Grupo abierto y §ADMIN, filas de editoriales/géneros/autores)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-01, RN-15, §Reglas derivadas)
  - `knowledge-base/08_arquitectura_propuesta.md` (§Responsabilidades por archivo de módulo)

### [CH-05] `libros-baja-logica-patch-sin-stock`
- **Estado**: `[ ]` pendiente
- **Objetivo**: libros con baja lógica, ISBN reutilizable y PATCH que no toca el stock; lecturas de catálogo por entidad.
- **Entra**:
  - `libros/repository.py` con `LibroRepository(SoftDeleteRepository[Libro])`: listados filtran bajas; `listar(page,size,titulo,genero_id)` con **parámetros ligados** e `ILIKE` (sin concatenar SQL; `' OR '1'='1` devuelve lista vacía con `total 0`); precarga declarada adentro del método (autores, editorial, género).
  - `libros/unit_of_work.py` (sesión compartida; para validar `editorial_id`/`genero_id` usa `BaseRepository(session, Editorial)` y `BaseRepository(session, Genero)` **genéricos**, sin depender de CH-04).
  - Endpoints: `GET /libros` (`page,size,titulo,genero_id`) → 200, 422; `GET /libros/{id}` → 200, 404, 422 (un libro dado de baja → 404); `PATCH /libros/{id}` (solo `titulo` y `precio`; `extra="forbid"` → con `stock` 422; `exclude_unset`) → 200, 404, 409, 422; `DELETE /libros/{id}` → **204** (baja lógica: pone `borrado_en`, conserva el dato), 404.
  - `GET /editoriales/{id}/libros`, `/generos/{id}/libros`, `/autores/{id}/libros` → 200, 404 (abiertos; lista de libros vigentes de esa entidad; 404 si la entidad no existe).
  - Mensaje 409 de ISBN en `MENSAJES_CONSTRAINT` (`uq_libro_isbn_vigente`).
  - Las ventas anteriores siguen mostrando el título de un libro dado de baja (la relación no filtra bajas).
- **No entra**: `POST /libros` con `stock_inicial`, reponer, movimientos (CH-06); guardas de rol (CH-10).
- **Governance**: MEDIO.
- **Dependencias**: CH-01, CH-02.
- **Archivos**:
  - Crear: `parcial/app/modules/libros/repository.py`, `parcial/app/modules/libros/unit_of_work.py`, `parcial/test/C-16_busqueda_paginacion_patch.http`.
  - Modificar: `parcial/app/modules/libros/service.py`, `router.py`, `schemas.py`; `parcial/app/core/errores.py` (entrada del ISBN); `parcial/app/main.py` (include_router).
- **Imitar**: `parcial/app/modules/editoriales/` ya refactorizado por CH-04 (si todavía no está, el `router.py`/`service.py` del TP) y `parcial/app/modules/libros/router.py` del TP.
- **RN**: RN-01 (ISBN entre vigentes), RN-11 (PATCH sin stock → 422), RN-13 (baja lógica), RN-15.
- **Casos C/D**: **C-16** (inyección, paginación con filtro, PATCH parcial, PATCH del stock). C-13 se demuestra completo en CH-06 (necesita el alta).
- **.http a correr**: `C-16_busqueda_paginacion_patch.http` (con `python seed.py` antes):
  - `GET /libros?titulo=' OR '1'='1` → 200, `items: []`, `total: 0`.
  - `GET /libros?titulo=ficc&size=1` → 200, `total: 1`, `pages: 1`; `...&page=2` → 422.
  - `GET /libros?size=500` → 422. `GET /libros/abc` → 422.
  - `PATCH /libros/1` con solo `{"titulo": "..."}` → 200, el precio no cambia. `PATCH /libros/1` con `{"stock": 99}` → 422.
  - `DELETE /libros/3` → 204; `GET /libros/3` → 404; `GET /libros` ya no lo lista; `GET /ventas/1` sigue mostrando "Ficciones".
  - `GET /editoriales/1/libros` → 200; `GET /generos/9999/libros` → 404.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap2-contratos.md` §2.6 — Actualización parcial: ausente contra nulo (PATCH)
  - `docs/catedra/cap2-contratos.md` §2.7 — El dinero y las cantidades
  - `docs/catedra/cap2-contratos.md` §2.8 — Los verbos y sus códigos
  - `docs/catedra/cap2-contratos.md` §2.9 — Colecciones: envoltorio, paginación y ordenamiento (búsqueda y filtros)
  - `docs/catedra/cap4-persistencia.md` §4.9 — Borrado lógico: una enumeración taxativa
  - `docs/catedra/cap6-uow-transacciones.md` §6.4 — El repositorio (6.4.4 «El catálogo de métodos…», baja lógica)
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (§E3, §E6)
  - `knowledge-base/04_modelo_de_datos.md` (§`libro`, §Los dos índices únicos parciales)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-01, RN-11, RN-13, §Reglas derivadas)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (filas de `/libros` y `/{x}/{id}/libros`; C-13, C-16)

### [CH-06] `stock-punto-unico-reponer-movimientos`
- **Estado**: `[ ]` pendiente
- **Objetivo**: un único lugar donde se escribe el stock (alta, reposición, venta), y los endpoints que lo usan.
- **Entra**:
  - `libros/stock.py` (o método de servicio) `aplicar_movimiento(uow, libro, cantidad, motivo, usuario_id, venta_id=None)`: actualiza `libro.stock` **y** agrega la fila de `movimiento_stock` en la misma operación. **Es el único código del proyecto que escribe `libro.stock`.** Motivos: "Stock inicial", "Reposición", "Venta" (texto libre).
  - `MovimientoStockRepository` en `libros/repository.py` y su atributo en el UoW de libros.
  - `POST /libros` (con `autores`, `stock_inicial`; el alta deja el movimiento "Stock inicial" hecho por el ADMIN autenticado; `stock_inicial = 0` no genera movimiento por el CHECK `cantidad <> 0`) → 201, 409 (ISBN repetido entre vigentes), 422.
  - `POST /libros/{id}/reponer` (`cantidad > 0`) → 200 con su movimiento "Reposición", 404, **409 si el libro está dado de baja** (RN-13), 422.
  - `GET /libros/{id}/movimientos` → 200, 404.
  - El `usuario_id` sale de `get_usuario_actual` (CH-10).
  - Invariante: `libro.stock = SUM(movimientos)`.
- **No entra**: la venta (CH-14, que **llama** a `aplicar_movimiento`), detalle sin N+1 (CH-15).
- **Governance**: ALTO (integridad del stock; un camino alternativo de escritura rompe el invariante).
- **Dependencias**: CH-02, CH-05, **CH-10** (agregada, ver tabla).
- **Archivos**:
  - Crear: `parcial/app/modules/libros/stock.py`, `parcial/test/C-13_baja_reposicion_isbn.http`.
  - Modificar: `parcial/app/modules/libros/repository.py`, `unit_of_work.py`, `service.py`, `router.py` (`router_admin`), `schemas.py`; `parcial/app/main.py` (include del `router_admin`).
- **Imitar**: `parcial/app/modules/ventas/service.py` del TP (flujo de varias escrituras) y `parcial/app/core/unit_of_work.py` (CH-02).
- **RN**: RN-11, RN-13, RN-01 (ISBN en el alta), RN-12 (los movimientos nunca se editan: solo se agregan).
- **Casos C/D**: **C-13**.
- **.http a correr**: `C-13_baja_reposicion_isbn.http` (sesión de ADMIN con `# @name loginAdmin`):
  - `POST /libros/1/reponer` `{"cantidad": 5}` → 200; `GET /libros/1/movimientos` → 200 con la fila "Reposición" (+5).
  - `DELETE /libros/1` → 204; `GET /libros` ya no lo muestra; `POST /libros/1/reponer` → 409.
  - `POST /libros` con el **mismo ISBN** `978-950-00-0001-1` → 201 (el viejo está de baja); repetir el mismo POST → 409 (dos vigentes).
  - `GET /ventas/1` sigue mostrando el título del libro dado de baja.
  - `POST /libros` con `stock` en lugar de `stock_inicial` → 422.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work (varias escrituras en una transacción; flush/commit)
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap6-uow-transacciones.md` §6.9 — Sólo agregado: dos mecanismos independientes (movimientos de stock)
  - `docs/catedra/cap6-uow-transacciones.md` §6.3 — Las cuatro propiedades de una transacción
  - `docs/catedra/cap2-contratos.md` §2.7 — El dinero y las cantidades
  - `docs/catedra/cap4-persistencia.md` §4.10 — Índices y restricciones (CHECK de stock no negativo)
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-11, RN-13)
  - `knowledge-base/06_funcionalidades.md` (§E6: "un único punto de escritura del stock")
  - `knowledge-base/04_modelo_de_datos.md` (§`movimiento_stock`)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-10, DD-13, DD-14, DD-17)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (cuerpo de `POST /libros`; C-13)

---

# PARTE 3 — Autenticación (Persona 3)

### [CH-07] `security-login-cookie`
- **Estado**: `[x]` hecho (archivado 05/11/2026 en `openspec/changes/archive/2026-11-05-ch-07-security-login-cookie/`)
- **Objetivo**: bcrypt fuera del bucle, JWT y login con cookie, anti-enumeración con hash ficticio.
- **Entra**:
  - `app/core/security.py`: `hashear_password` / `verificar_password` con `asyncio.to_thread` y **semáforo** (limita cuántos bcrypt corren a la vez), costo = `BCRYPT_COSTO`; `crear_token(sub, roles)` y `decodificar_token` con PyJWT (claims `sub`, `exp`, roles vigentes al emitir; firmado con `JWT_SECRET`, duración `JWT_MINUTOS`).
  - `app/core/security.py`: tipo reutilizable **`PasswordBcrypt`** (`Annotated[str, AfterValidator(...)]`) que rechaza con **422** toda contraseña de más de **72 bytes** (`len(v.encode("utf-8")) > 72`, bytes y no caracteres). Se define **una sola vez acá** y lo reusan **todos** los campos que pasan por bcrypt: login (CH-07), registro (CH-08), contraseña actual y nueva del cambio (CH-11) y alta de personal (CH-12). Nadie vuelve a escribir la validación.
  - Lifespan: calcula **una vez** el **hash ficticio** y lo guarda en `app.state` (se pide en el Ej. 1; se completa acá).
  - `usuarios/repository.py` (`UsuarioRepository`, `AsignacionRolRepository` con `roles_vigentes(usuario_id)`: `revocada_en IS NULL` y `vence_en` nulo o futuro, `EventoSeguridadRepository` mínimo) y `usuarios/unit_of_work.py` (los compone con la misma sesión; lo usarán CH-08, CH-09, CH-11 y CH-12).
  - `POST /auth/login` (`LoginIn`: correo y contraseña, `extra="forbid"`, contraseña de tipo `PasswordBcrypt`: más de 72 bytes → 422): busca el usuario; si existe verifica contra su hash, si no contra el **hash ficticio** (mismo mensaje, mismo tiempo); 200 con cuerpo `{"mensaje": "Sesión iniciada", "debe_cambiar_password": false, "expira_en_segundos": 1800}` y el token **solo** en `Set-Cookie: access_token` (`HttpOnly`, `SameSite=Lax`, `Max-Age = JWT_MINUTOS*60`, `Secure = COOKIE_SECURE`). 401 con mensaje único «Credenciales inválidas» (usuario inactivo incluido). El hash se calcula **antes** de abrir la transacción.
  - Router en `usuarios/router.py` (`router_abierto`, prefijo `/auth`).
- **No entra**: límite de intentos y `intento_acceso` (CH-09; dejar el punto de inserción comentado en el servicio), registro/logout/yo (CH-08), lectura de la cookie en `get_usuario_actual` (CH-10).
- **Governance**: CRÍTICO.
- **Dependencias**: CH-01, CH-02.
- **Archivos**:
  - Crear: `parcial/app/core/security.py`, `parcial/app/modules/usuarios/{repository,unit_of_work,service,schemas,router}.py`, `parcial/test/C-03_cookie.http`, `parcial/test/C-04_anti_enumeracion.http`.
  - Modificar: `parcial/app/main.py` (lifespan: hash ficticio; `include_router` de `/auth`).
- **Imitar**: `parcial/app/modules/health/router.py` (router mínimo) y `parcial/app/core/database.py` (cómo el lifespan deja recursos en `app.state`).
- **RN**: RN-08; base de RN-04 y RN-07; 72 bytes (regla derivada).
- **Casos C/D**: **C-03** (cookie, lado login), **C-04**.
- **.http a correr**:
  - `C-03_cookie.http`: login correcto → 200; la cabecera `Set-Cookie` tiene `access_token`, `HttpOnly`, `SameSite=Lax`, `Max-Age=1800`; el cuerpo **no** trae token. (CH-10 agrega al final los pedidos sin cookie / con `Authorization: Bearer` → 401.)
  - `C-04_anti_enumeracion.http`: correo existente con clave mala → 401; correo inexistente → 401 con **el mismo cuerpo** y tiempo parecido (comparar los tiempos que muestra REST Client). Contraseña de 73 bytes (ej. 37 "ñ") → 422, no 500.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.3 — Anatomía de un token (JWT y cookie)
  - `docs/catedra/cap5-autenticacion.md` §5.4 — Por qué el hash de contraseña es lento a propósito (límite de 72 bytes de bcrypt)
  - `docs/catedra/cap2-contratos.md` §2.3.1 — Cuando la restricción no entra en un campo (cómo armar `PasswordBcrypt`)
  - `docs/catedra/cap5-autenticacion.md` §5.5 — El flujo de autenticación, y por qué el orden importa (anti-enumeración)
  - `docs/catedra/cap5-autenticacion.md` §5.6 — bcrypt fuera del bucle, y su semáforo (`asyncio.to_thread`)
  - `docs/catedra/cap3-asincronia.md` §3.6 — Qué significa bloquear, y las tres del sistema (EA-01)
  - `docs/catedra/cap5-autenticacion.md` §5.12 — Seguridad y evolución
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (§E4)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-08, §Reglas derivadas: 72 bytes y cookie)
  - `knowledge-base/08_arquitectura_propuesta.md` (§Seguridad, §Variables de entorno)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-08, DD-16)
  - `knowledge-base/07_flujos_principales.md` (flujo de login)

### [CH-08] `registro-logout-yo`
- **Estado**: `[ ]` pendiente
- **Objetivo**: auto-registro atómico (RN-02), cierre de sesión y `GET /auth/yo`.
- **Entra**:
  - `POST /auth/registro` (`extra="forbid"`: nadie se registra con un rol; contraseña de tipo `PasswordBcrypt` de CH-07, sin validación propia) → 201, 409, 422. **Un solo bloque `async with uow:`** crea `usuario` + `asignacion_rol` CLIENTE + ficha de `cliente` (con `usuario_id`): o quedan las tres filas o ninguna. Hash calculado **antes** de abrir el UoW. Correo ya usado por un usuario → 409 con mensaje propio; correo ya usado por un **cliente** → 409 con otro mensaje y **no se apropia de esa ficha** ni deja filas sueltas. Ambos vía `IntegrityError` (`uq_usuario_email`, `uq_cliente_email`), sin consulta previa. Respuesta 201 sin `password_hash`.
  - `POST /auth/logout` → 200, **funciona sin sesión**; borra la cookie (`Max-Age=0`).
  - `GET /auth/yo` → 200, 401: usuario, **roles vigentes (de la base)** y **roles que dice el token**.
  - La ficha de cliente se crea con `BaseRepository(session, Cliente)` genérico (no depende de CH-13); `UsuariosUnitOfWork` suma ese atributo.
- **No entra**: lectura de cookie (`get_usuario_actual`, es de CH-10; la tarea `/auth/yo` espera a que esté), cambio de contraseña (CH-11).
- **Governance**: CRÍTICO.
- **Dependencias**: CH-07 (y **CH-10 solo para `/auth/yo`**; el change se archiva recién con CH-10 en `main`).
- **Archivos**:
  - Modificar: `parcial/app/modules/usuarios/{service,schemas,router,unit_of_work}.py`, `parcial/app/core/errores.py` (dos entradas).
  - Crear: `parcial/test/C-02_registro.http`.
- **Imitar**: `parcial/app/modules/usuarios/service.py` de CH-07 (mismo patrón de hash antes de transacción) y `parcial/app/modules/ventas/service.py` del TP (varias escrituras).
- **RN**: **RN-02**, RN-01 (correo de usuario y de cliente), RN-15.
- **Casos C/D**: **C-02**.
- **.http a correr**: `C-02_registro.http`:
  - `POST /auth/registro` datos nuevos → 201 (sin `password_hash`); luego login con ese usuario → 200.
  - Mismo correo otra vez → 409 «ese correo ya tiene usuario» (mensaje propio).
  - Registro con el correo de la ficha de "Tomás Ríos" (cliente sin usuario) → 409 con otro mensaje; `GET /clientes/{id}` de Tomás (ADMIN) sigue sin `usuario_id`; no hay usuario nuevo con ese correo (no hay filas sueltas).
  - Cuerpo con `"rol": "ADMIN"` → 422.
  - Contraseña de 73 bytes (ej. 37 "ñ") → 422, no 500 (lo da `PasswordBcrypt`).
  - `POST /auth/logout` sin cookie → 200.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.5 — El flujo de autenticación, y por qué el orden importa
  - `docs/catedra/cap5-autenticacion.md` §5.4 — Por qué el hash de contraseña es lento a propósito (límite de 72 bytes)
  - `docs/catedra/cap2-contratos.md` §2.3.1 — Cuando la restricción no entra en un campo (`PasswordBcrypt`, se reusa de CH-07)
  - `docs/catedra/cap5-autenticacion.md` §5.6 — bcrypt fuera del bucle, y su semáforo
  - `docs/catedra/cap5-autenticacion.md` §5.7 — Los cuatro roles (rol inicial del registro)
  - `docs/catedra/cap5-autenticacion.md` §5.3 — Anatomía de un token (cierre de sesión: cookie)
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra (registro atómico en un solo `async with`)
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-02, RN-01, RN-15)
  - `knowledge-base/06_funcionalidades.md` (§E4, §E6)
  - `knowledge-base/07_flujos_principales.md` (flujo de registro)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-08, DD-18)

### [CH-09] `intento-acceso-limite-429`
- **Estado**: [x] hecho (archivado 05/11/2026 en openspec/changes/archive/2026-11-05-ch-09-intento-acceso-limite-429/)
- **Objetivo**: anotar cada intento de login en sesión propia y limitar a 5 fallos por minuto (RN-07).
- **Entra**:
  - `IntentoAccesoRepository` y una función `registrar_intento(session_factory, email, ip, exito)` que abre **su propia sesión y transacción** y **siempre confirma** (la fábrica sale de `app.state`). Es la **única** escritura que no comparte la transacción de la petición. Va con **un comentario que dice tres cosas**: (1) qué hace distinto, (2) por qué no puede compartir la transacción (el fallo que se cuenta es el mismo que la revierte), (3) su costo (deja filas aunque la petición falle).
  - En el login (CH-07), **orden**: (1) límite de intentos: **una consulta** que cuenta los fallos del mismo correo y la misma IP (`request.client.host`) en los últimos 60 s, **desde el último éxito** (un login correcto reinicia la cuenta; los fallos viejos siguen en la tabla pero no cuentan); si hay 5 → **429** con `Retry-After` (segundos hasta que el fallo más viejo deje de contar) **sin calcular ningún hash**; (2) verificación contra hash real o ficticio.
  - El intento rechazado por 429 **no** se anota (P-14). Éxito y fallo se anotan.
- **No entra**: Redis ni limitador en memoria (Backlog), bloqueo permanente de cuenta.
- **Governance**: CRÍTICO.
- **Dependencias**: CH-07.
- **Archivos**:
  - Modificar: `parcial/app/modules/usuarios/{repository,service,router}.py`.
  - Crear: `parcial/test/C-05_limite_intentos.http`.
- **Imitar**: `parcial/app/core/database.py` (cómo se crea la fábrica) y `parcial/app/modules/usuarios/service.py` (CH-07).
- **RN**: **RN-07**; completa RN-08 (orden).
- **Casos C/D**: **C-05**.
- **.http a correr**: `C-05_limite_intentos.http` (mismo correo `vendedor@example.com`, 6 logins fallidos seguidos):
  - Intentos 1–5 → 401. Intento 6 → **429** con cabecera `Retry-After` y respuesta en pocos milisegundos (sin bcrypt).
  - Consulta SQL (comentada en el archivo): `SELECT * FROM intento_acceso WHERE email='vendedor@example.com'` → los **5 fallos** (el 429 no está).
  - Esperar 60 s → login correcto → 200; luego un fallo cuenta desde cero.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.5 — El flujo de autenticación, y por qué el orden importa (primero el límite de intentos, después el hash)
  - `docs/catedra/cap6-uow-transacciones.md` §6.8.1 — El intento de acceso que debe sobrevivir al rollback
  - `docs/catedra/cap6-uow-transacciones.md` §6.8.2 — Las cuatro sesiones del panel (sesión propia fuera de la transacción de la petición)
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-07, RN-08)
  - `knowledge-base/06_funcionalidades.md` (§E4, §E7)
  - `knowledge-base/04_modelo_de_datos.md` (§`intento_acceso`)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-06, DD-19, SU-08)

---

# PARTE 4 — Autorización (Persona 4)

### [CH-10] `usuario-actual-roles-dos-grupos`
- **Estado**: [x] completado
- **Objetivo**: saber quién es el usuario, qué roles vigentes tiene en la base, y montar los dos grupos de rutas.
- **Entra**:
  - `app/core/dependencies.py`:
    - `get_usuario_actual`: lee `request.cookies["access_token"]` (**nunca** `Authorization`); 401 si falta, es inválido o venció, o el usuario no existe/está inactivo. Devuelve el usuario y los roles que trae el token (informativos).
    - `roles_vigentes`: consulta `asignacion_rol` **en cada petición** (RN-04).
    - `requiere_rol(*roles)`: 403 si no tiene ninguno vigente.
    - `exigir_password_al_dia`: 403 si `debe_cambiar_password` (RN-06).
    - Todas comparten **la misma sesión** que el UoW (`get_session` es una dependencia cacheada por petición): no se toman dos conexiones del pool.
  - `app/main.py` con **dos grupos**: **abierto** (health, `/auth/*`, `GET /libros...`, `GET /editoriales`, `/generos`, `GET /{x}/{id}/libros`) y **protegido** (todo lo demás), con `exigir_password_al_dia` montado **una sola vez** en el grupo protegido. Los `router_admin` se montan con `requiere_rol("ADMIN")`, los `router_staff` con `requiere_rol("VENDEDOR","ADMIN")`. `GET /ventas/{id}` y `GET /mis-ventas` en el protegido **sin** `requiere_rol` (decide el servicio / solo autenticado). `/auth/yo` y `/auth/cambiar-password` van en el grupo abierto pero usan `get_usuario_actual` (401 sin sesión).
  - Cierre de la tarea `/auth/yo` de CH-08 (avisar a la Persona 3).
- **No entra**: endpoints nuevos de roles (CH-12), cambio de contraseña (CH-11).
- **Governance**: CRÍTICO.
- **Dependencias**: CH-01, CH-02, CH-07.
- **Archivos**:
  - Crear: `parcial/app/core/dependencies.py`, `parcial/test/C-01_param_no_entero.http`, `parcial/test/C-06_401_vs_403.http`.
  - Modificar: `parcial/app/main.py` (reestructura en dos grupos), `parcial/test/C-03_cookie.http` (agrega al final los pedidos sin cookie y con Bearer).
- **Imitar**: `parcial/app/modules/usuarios/` de CH-07 (cómo se cargan repos y UoW) y la estructura actual de `parcial/app/main.py`.
- **RN**: **RN-04**, **RN-06** (los dos grupos), RN-14 (autenticado sin rol).
- **Casos C/D**: **C-01**, **C-03** (lado 401), **C-06** (401 vs 403; la parte "la cliente ve su venta" se cierra en CH-14).
- **.http a correr**:
  - `C-01_param_no_entero.http`: con sesión iniciada, `GET /libros/abc` → 422 y `GET /clientes/abc` → 422 (el handler no se ejecuta).
  - `C-03_cookie.http` (lo agregado): `GET /auth/yo` sin cookie → 401; con `Authorization: Bearer <token válido>` y sin cookie → 401.
  - `C-06_401_vs_403.http`: `POST /libros` sin sesión → 401; con sesión de `vendedor@example.com` → 403; con ADMIN → pasa el guarda (la respuesta funcional la define CH-06). Usuario inactivo (poner `activo=false` por SQL) → 401.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.7 — Los cuatro roles
  - `docs/catedra/cap5-autenticacion.md` §5.8 — Por qué SISTEMA no es un rol
  - `docs/catedra/cap5-autenticacion.md` §5.9 — Vigencia: la autorización se decide en la base (401 vs 403, `get_usuario_actual`)
  - `docs/catedra/cap5-autenticacion.md` §5.10 — Cambio obligatorio de contraseña, y los dos routers
  - `docs/catedra/cap1-fastapi.md` §1.8 — Inyección de dependencias
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (§E5, §E6)
  - `knowledge-base/03_actores_y_roles.md` (matriz RBAC, §Cambio obligatorio)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-04, RN-06, RN-14)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-05, DD-09)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (los tres grupos de rutas)

### [CH-11] `cambiar-password-cambio-obligatorio`
- **Estado**: [x] completado
- **Objetivo**: cambio de contraseña con auditoría y desbloqueo del cambio obligatorio.
- **Entra**:
  - `POST /auth/cambiar-password` (`password_actual` y `password_nueva`, **ambas de tipo `PasswordBcrypt`** de CH-07, sin validación propia; `extra="forbid"`) → 200, 401 (sin sesión **o `password_actual` incorrecta**, mismo criterio que el login; DD-30), 422 (cuerpo que rompe el contrato). Ambos hashes/verificaciones se hacen **antes** de abrir la transacción.
  - Un solo `async with uow:`: guarda el hash nuevo, pone `debe_cambiar_password = false` y agrega la línea de `evento_seguridad` ("Cambio de contraseña", actor = correo del usuario) — **RN-16, misma transacción**.
  - **No** invalida las sesiones abiertas ni emite un token nuevo: la misma cookie sirve después.
  - Con cambio pendiente, solo `/auth/*` y rutas sin sesión responden; el resto 403 (lo da el grupo protegido de CH-10).
  - **Decidido (DD-30)**: `password_actual` incorrecta → **401** (no 422). No hay nada pendiente.
- **No entra**: reglas de complejidad de contraseña más allá de los 72 bytes.
- **Governance**: CRÍTICO.
- **Dependencias**: CH-10 (y CH-07 por transitividad).
- **Archivos**:
  - Modificar: `parcial/app/modules/usuarios/{service,schemas,router}.py`.
  - Crear: `parcial/test/C-09_cambio_obligatorio.http`.
- **Imitar**: `parcial/app/modules/usuarios/service.py` (registro de CH-08: hash antes de la transacción, una sola escritura atómica).
- **RN**: **RN-06**, **RN-16** (cambio de contraseña).
- **Casos C/D**: **C-09**.
- **.http a correr**: `C-09_cambio_obligatorio.http` (usuario `nuevo@example.com`):
  - Login → 200 con `"debe_cambiar_password": true`.
  - `GET /libros` (abierto) → 200; `GET /auth/yo` → 200; `GET /ventas` → **403**.
  - `POST /auth/cambiar-password` → 200. Con la **misma cookie**, `GET /ventas` → 200 sin iniciar sesión de nuevo; `GET /auth/yo` muestra `debe_cambiar_password: false`.
  - `password_actual` incorrecta → **401** (y la contraseña no cambia). Contraseña nueva de 73 bytes → 422. Sin sesión → 401. (Consulta SQL comentada: `evento_seguridad` tiene la línea nueva.)
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.10 — Cambio obligatorio de contraseña, y los dos routers
  - `docs/catedra/cap5-autenticacion.md` §5.4 — Por qué el hash de contraseña es lento a propósito (límite de 72 bytes)
  - `docs/catedra/cap2-contratos.md` §2.3.1 — Cuando la restricción no entra en un campo (`PasswordBcrypt`, se reusa de CH-07)
  - `docs/catedra/cap5-autenticacion.md` §5.6 — bcrypt fuera del bucle, y su semáforo
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-06, RN-16)
  - `knowledge-base/03_actores_y_roles.md` (§Cambio obligatorio de contraseña)
  - `knowledge-base/07_flujos_principales.md` (flujo de cambio de contraseña)
  - `knowledge-base/06_funcionalidades.md` (§E4, §E5)
  - `knowledge-base/09_decisiones_y_supuestos.md` (DD-30)

### [CH-12] `roles-vigencia-alta-personal-eventos`
- **Estado**: `[ ]` pendiente
- **Objetivo**: administración de roles con vencimiento, autoprotección (RN-05), alta de personal y consulta del historial de seguridad.
- **Entra**:
  - `POST /usuarios` (alta de personal con contraseña provisoria de tipo `PasswordBcrypt` de CH-07, sin validación propia; `debe_cambiar_password = true`, rol inicial) → 201, 409, 422. Un solo UoW: usuario + asignación + línea de `evento_seguridad` (RN-16), actor = correo del admin. Hash antes de la transacción.
  - `GET /usuarios/{id}/roles` → 200 (con las filas revocadas también), 404.
  - `POST /usuarios/{id}/roles` (`rol`, `vence_en` opcional) → 201, 404, 409, 422. `vence_en` debe traer zona horaria y estar en el futuro; si no, **422** (no 409). Ya hay una asignación abierta del mismo rol → 409 (índice `uq_asignacion_rol_abierta`). Reasignar un rol **vencido**: en el mismo UoW se **cierra la fila anterior** (`revocada_en`) y se abre una nueva. `otorgada_por` = id del admin. Evento de seguridad en la misma transacción.
  - `DELETE /usuarios/{id}/roles/{rol}` → 200, 404, 409. Revoca poniendo `revocada_en` (**no borra la fila**). **RN-05**: un admin no puede revocarse su propio ADMIN, y no se puede dejar al sistema sin ADMIN vigente → 409. Evento en la misma transacción.
  - `GET /eventos` (`page`, `size`) → 200, 422 (más recientes primero).
  - Todo en `router_admin` de `usuarios` (más `GET /eventos`).
- **No entra**: segundo mecanismo de sólo agregado (Backlog), listado de usuarios.
- **Governance**: CRÍTICO.
- **Dependencias**: CH-10 (y CH-07 por transitividad).
- **Archivos**:
  - Modificar: `parcial/app/modules/usuarios/{repository,unit_of_work,service,schemas,router}.py`, `parcial/app/core/errores.py`, `parcial/app/main.py` (include).
  - Crear: `parcial/test/C-07_revocar_rol.http`, `parcial/test/C-08_autoproteccion.http`.
- **Imitar**: `parcial/app/modules/usuarios/service.py` (CH-08, registro atómico) y `parcial/app/core/paginacion.py` (CH-02) para `/eventos`.
- **RN**: **RN-03** (409), **RN-05**, **RN-16** (alta de personal y cambio de rol), RN-04 (se prueba), RN-01 (correo de personal).
- **Casos C/D**: **C-07**, **C-08**.
- **.http a correr**:
  - `C-07_revocar_rol.http` (dos sesiones: `loginAdmin` y `loginVendedor`): con la sesión abierta del vendedor, `POST /clientes` → 201/200 funcional; el ADMIN hace `DELETE /usuarios/<id vendedor>/roles/VENDEDOR` → 200; la **misma cookie** del vendedor en `POST /clientes` → **403**; `GET /auth/yo` del vendedor muestra roles de la base (sin VENDEDOR) vs roles del token (con VENDEDOR); `GET /usuarios/<id>/roles` conserva la fila revocada. `POST /usuarios/<id>/roles` con `vence_en` en el pasado → 422; sin zona horaria → 422; mismo rol abierto → 409.
  - `C-08_autoproteccion.http`: `admin@example.com` hace `DELETE /usuarios/<su id>/roles/ADMIN` → **409**; con `admin2@example.com` activo, `admin2` no puede dejar al sistema sin ADMIN (revocar al último) → 409.
  - Además: `POST /usuarios` → 201 y luego el login del nuevo trae `debe_cambiar_password: true`; `POST /usuarios` con contraseña provisoria de 73 bytes → 422; `GET /eventos` → 200 con las líneas; `GET /eventos?size=500` → 422.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap5-autenticacion.md` §5.7 — Los cuatro roles
  - `docs/catedra/cap5-autenticacion.md` §5.8 — Por qué SISTEMA no es un rol
  - `docs/catedra/cap5-autenticacion.md` §5.9 — Vigencia: la autorización se decide en la base (roles con vigencia y revocación)
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work (usuario + asignación + evento en una transacción)
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap4-persistencia.md` §4.9 — Borrado lógico: una enumeración taxativa (historial, sin borrar)
  - `docs/catedra/cap5-autenticacion.md` §5.4 — Por qué el hash de contraseña es lento a propósito (límite de 72 bytes de la contraseña provisoria)
  - `docs/catedra/cap2-contratos.md` §2.3.1 — Cuando la restricción no entra en un campo (`PasswordBcrypt`, se reusa de CH-07)
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-03, RN-05, RN-16, §Reglas derivadas: vencimiento)
  - `knowledge-base/04_modelo_de_datos.md` (§`asignacion_rol`, §`evento_seguridad`)
  - `knowledge-base/06_funcionalidades.md` (§E5)
  - `knowledge-base/07_flujos_principales.md` (flujo de roles)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (filas de `/usuarios`, `/eventos`; C-07, C-08)

---

# PARTE 5 — Clientes y ventas (Persona 5)

### [CH-13] `clientes-repo-uow-usuario-id`
- **Estado**: `[ ]` pendiente
- **Objetivo**: clientes con repositorio + UoW, ficha vinculable a un usuario, y rutas para VENDEDOR o ADMIN.
- **Entra**:
  - `clientes/repository.py` (`ClienteRepository` con `get_by_email`, `get_by_usuario_id`, precarga del perfil declarada adentro; `PerfilClienteRepository`), `unit_of_work.py`, `service.py` (recibe el UoW), `router.py` (`router_staff`).
  - Endpoints: `POST /clientes` → 201, 409 (correo repetido, `uq_cliente_email`), 422; `GET /clientes/{id}` (con su perfil) → 200, 404; `PATCH /clientes/{id}` (`exclude_unset`, `extra="forbid"`) → 200, 404, 409, 422; `POST /clientes/{id}/perfil` → 201, 404, 409 (ya tiene perfil).
  - El contrato de salida incluye `usuario_id` (nulo si no tiene acceso web); **no es editable** por `POST`/`PATCH` (`extra="forbid"`).
  - Un cliente creado por personal no tiene usuario; el de auto-registro (CH-08) sí.
- **No entra**: `GET /clientes/{id}/ventas` (se define en el módulo ventas, CH-14), alta de usuario para el cliente.
- **Governance**: MEDIO.
- **Dependencias**: CH-01, CH-02, CH-10.
- **Archivos**:
  - Crear: `parcial/app/modules/clientes/repository.py`, `parcial/app/modules/clientes/unit_of_work.py`, `parcial/test/CH-13_clientes.http`.
  - Modificar: `parcial/app/modules/clientes/{service,router,schemas}.py`, `parcial/app/core/errores.py`, `parcial/app/main.py`.
- **Imitar**: `parcial/app/modules/editoriales/` ya refactorizado por CH-04 (misma forma repositorio + UoW + service + routers).
- **RN**: RN-01 (correo de cliente), RN-11 (`extra="forbid"` como patrón), RN-15; soporte de RN-14 (`cliente.usuario_id` identifica al dueño).
- **Casos C/D**: apoya C-06 y C-02 (la ficha). Sin caso propio.
- **.http a correr**: `CH-13_clientes.http` (sesión de `vendedor@example.com`):
  - `POST /clientes` → 201; mismo correo → 409; cuerpo con `usuario_id` → 422; sin nombre → 422.
  - `GET /clientes/1` → 200 con perfil (Lucía) y `usuario_id: null`; `GET /clientes/3` (Ana) → `usuario_id` con valor; `GET /clientes/9999` → 404.
  - `PATCH /clientes/2` parcial → 200; con el correo de otro cliente → 409.
  - `POST /clientes/2/perfil` → 201; repetido → 409; `POST /clientes/9999/perfil` → 404.
  - Sin sesión → 401; sesión de Ana (CLIENTE) → 403.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap6-uow-transacciones.md` §6.4 — El repositorio
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap4-persistencia.md` §4.6 — Relaciones y carga anticipada
  - `docs/catedra/cap1-fastapi.md` §1.10 — Las capas (el Service recibe el actor por parámetro)
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` (§`cliente`)
  - `knowledge-base/06_funcionalidades.md` (§E3, §E6)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (§VENDEDOR o ADMIN)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-01, RN-14)

### [CH-14] `venta-rn10-mis-ventas-dueno`
- **Estado**: `[ ]` pendiente
- **Objetivo**: registrar una venta de forma atómica usando el punto único de stock, y exponer las lecturas "lo propio".
- **Entra**:
  - `ventas/repository.py`, `ventas/unit_of_work.py` (ventas, renglones, libros, movimientos, clientes con `BaseRepository(session, Cliente)` genérico), `service.py`, `router.py`.
  - `POST /ventas` (`cliente_id`, `renglones` ≥ 1 sin libros repetidos; **precio, total y fecha no viajan**; `extra="forbid"`) → 201, 409, 422. **Un solo `async with uow:`**: valida cliente y libros, copia el precio de cada libro al renglón, calcula el total en el servidor, descuenta el stock y deja **un movimiento por renglón** llamando a `aplicar_movimiento` de CH-06 (motivo "Venta", `usuario_id` = vendedor autenticado, `venta_id`). Si un libro no alcanza → **409** y **no queda nada** (ni venta, ni renglones, ni descuentos, ni movimientos). Cliente o libro del cuerpo inexistente, o libro dado de baja → **409** (no 404).
  - El aviso del comprobante (`BackgroundTasks`, `ventas/tasks.py` ya existe en el TP) se agenda **solo si la operación se confirmó**.
  - `GET /ventas` (`page`, `size`) → 200, 422; `GET /ventas/{id}` **sin `requiere_rol`**: el servicio decide (personal, o el cliente dueño `venta.cliente.usuario_id == usuario.id`) → 200, 403, 404 (el 403 va antes de devolver datos); `GET /mis-ventas` (`page`, `size`, autenticado, solo las suyas) → 200, 422; `GET /clientes/{id}/ventas` (staff) → 200, 404 (en `ventas/router.py`, `router_staff`).
  - No hay `PATCH` ni `DELETE` de ventas (RN-09).
- **No entra**: optimización de consultas del detalle (CH-15), bloqueos por concurrencia (Backlog, cap. 7).
- **Governance**: ALTO (dinero y stock).
- **Dependencias**: CH-06, CH-10.
- **Archivos**:
  - Crear: `parcial/app/modules/ventas/repository.py`, `parcial/app/modules/ventas/unit_of_work.py`, `parcial/test/C-10_venta_valida.http`, `parcial/test/C-11_venta_sin_stock.http`, `parcial/test/C-12_venta_referencias_invalidas.http`.
  - Modificar: `parcial/app/modules/ventas/{service,router,schemas}.py`, `parcial/app/modules/ventas/tasks.py` (solo si hace falta el logger), `parcial/app/core/errores.py`, `parcial/test/C-06_401_vs_403.http` (agrega "la cliente ve su venta"), `parcial/app/main.py`.
  - **Nota**: `parcial/app/modules/ventas/models.py` **ya viene modificado por CH-01** (declara `Venta.movimientos` ↔ `MovimientoStock.venta`, navegación en los dos extremos). No volver a tocarlo: partir de lo que dejó CH-01.
- **Imitar**: `parcial/app/modules/ventas/service.py` y `tasks.py` del TP (lógica actual de la venta) y `parcial/app/modules/libros/stock.py` (CH-06).
- **RN**: **RN-09**, **RN-10**, **RN-14**, RN-13 (libro de baja no se vende), RN-11 (solo vía `aplicar_movimiento`), RN-15.
- **Casos C/D**: **C-10**, **C-11**, **C-12**, **C-06** (parte "lo propio").
- **.http a correr** (sesión `vendedor@example.com`):
  - `C-10_venta_valida.http`: `POST /ventas` con 2 renglones (ej. libros 1 y 4) → **201** con `precio_unitario` copiados y `total`; el stock de cada libro bajó; `GET /libros/{id}/movimientos` muestra un movimiento "Venta" por renglón; el aviso del comprobante aparece en la consola del servidor **después** de la respuesta.
  - `C-11_venta_sin_stock.http`: Rayuela ×1 (alcanza) + Bestiario ×2 (hay 1) → **409**; no hay venta nueva; Rayuela sigue en 10; la suma de movimientos = `libro.stock` en los 5 libros (consulta SQL comentada).
  - `C-12_venta_referencias_invalidas.http`: `cliente_id` inexistente → 409; `libro_id` inexistente → 409; libro dado de baja → 409; sin escrituras en ningún caso. Libro repetido en renglones → 422; `renglones: []` → 422; cuerpo con `total` → 422.
  - `C-06_401_vs_403.http` (lo agregado, sesiones `loginAna` y `loginVendedor`): `GET /ventas/1` con `vendedor` → 200; Ana ve su venta (una venta propia creada en el archivo) → 200 y la ajena (`/ventas/1`, de Lucía) → **403**; `GET /mis-ventas` de Ana → solo las suyas; `GET /ventas/9999` → 404.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap6-uow-transacciones.md` §6.3 — Las cuatro propiedades de una transacción (venta atómica)
  - `docs/catedra/cap6-uow-transacciones.md` §6.6 — El Unit of Work (todas las escrituras de la venta; `rollback`)
  - `docs/catedra/cap6-uow-transacciones.md` §6.7 — Quién crea, quién abre, quién confirma y quién cierra
  - `docs/catedra/cap3-asincronia.md` §3.9 — Tareas en segundo plano (`BackgroundTasks`)
  - `docs/catedra/cap1-fastapi.md` §1.10 — Las capas (el Service recibe el actor por parámetro)
  - `docs/catedra/cap4-persistencia.md` §4.6 — Relaciones y carga anticipada (detalle de ventas)
  - `docs/catedra/cap2-contratos.md` §2.8 — Los verbos y sus códigos
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` (RN-09, RN-10, RN-13, RN-14)
  - `knowledge-base/06_funcionalidades.md` (§E6, §E8)
  - `knowledge-base/07_flujos_principales.md` (flujo de venta)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (cuerpo de `POST /ventas`; C-10, C-11, C-12)
  - `knowledge-base/03_actores_y_roles.md` (nota sobre `GET /ventas/{id}`)

### [CH-15] `sin-n-mas-1-background-solo-agregado`
- **Estado**: `[ ]` pendiente
- **Objetivo**: lecturas con número fijo de consultas, aviso visible, evidencia de C-14 y C-15 y cierre del README.
- **Entra**:
  - Carga anticipada **declarada en los repositorios** (`selectinload`/`joinedload`) para: detalle de venta (cliente, renglones, libro de cada renglón **incluso dado de baja**), listados de libros (autores, editorial, género), clientes (perfil) y movimientos. Ninguna lectura depende de carga perezosa. El detalle usa un **número fijo de consultas** que no crece con los renglones.
  - Todos los handlers `async def`; revisión de que ninguna llamada es bloqueante.
  - Configurar el logger para que el aviso del comprobante se vea con el arranque normal de uvicorn (si se usa `logging.getLogger(...)` propio, configurarlo en el lifespan).
  - `parcial/test/solo_agregado.sql`: `UPDATE movimiento_stock ...` y `DELETE FROM movimiento_stock ...` que el disparador rechaza (**C-14**). Único `.sql` permitido.
  - `parcial/evidencia/`: consola con `SQL_ECHO=true` del detalle de venta con **2 y con 4 renglones** (misma cantidad de consultas) y captura `psql` de C-14.
  - `parcial/README.md`: nombres de los integrantes, pasos desde cero (entorno virtual, dependencias, `.env` con cómo generar `JWT_SECRET`, `alembic upgrade head`, `python seed.py`, arranque), y la diferencia entre el seed del TP y el del parcial (IN-04).
- **No entra**: caché (Redis, Backlog), cambios en `despliegue/`.
- **Governance**: BAJO.
- **Dependencias**: CH-14, CH-06, CH-02.
- **Archivos**:
  - Crear: `parcial/test/solo_agregado.sql`, `parcial/test/C-15_sin_n_mas_1.http`, `parcial/evidencia/` (capturas/consola).
  - Modificar: `parcial/app/modules/ventas/repository.py`, `parcial/app/modules/libros/repository.py`, `parcial/app/modules/clientes/repository.py`, `parcial/app/modules/ventas/tasks.py`, `parcial/app/main.py` (logging), `parcial/README.md`.
- **Imitar**: `parcial/app/modules/ventas/tasks.py` (aviso existente) y los repositorios de CH-05/CH-14.
- **RN**: RN-12 (se demuestra), RN-10 (el aviso solo si confirmó); cierra el criterio E8.
- **Casos C/D**: **C-14**, **C-15**.
- **.http a correr**:
  - `C-15_sin_n_mas_1.http` (con `SQL_ECHO=true`): `GET /ventas/1` (2 renglones) y el detalle de una venta nueva con 4 renglones → **200** en ambos y **la misma cantidad de consultas** en la consola (anotarla en un comentario).
  - `solo_agregado.sql` en `psql`: `UPDATE` → error del disparador; `DELETE` → error del disparador; `SELECT` de las filas intactas.
  - `C-10_venta_valida.http` otra vez: el aviso del comprobante aparece en consola con el arranque normal.
- **Leer antes (cátedra)** (`docs/catedra/`: buscar la sección puntual, nunca leer el archivo entero):
  - `docs/catedra/cap3-asincronia.md` §3.8.3 — El N+1 que dejó de ser un problema de rendimiento
  - `docs/catedra/cap3-asincronia.md` §3.8 — La regla del greenlet (3.8.1 y 3.8.2)
  - `docs/catedra/cap4-persistencia.md` §4.6 — Relaciones y carga anticipada (`selectinload`/`joinedload`)
  - `docs/catedra/cap6-uow-transacciones.md` §6.5 — La tabla de precarga es parte del contrato
  - `docs/catedra/cap6-uow-transacciones.md` §6.9 — Sólo agregado: dos mecanismos independientes
  - `docs/catedra/cap3-asincronia.md` §3.9 — Tareas en segundo plano (`BackgroundTasks`)
  - `docs/catedra/cap2-contratos.md` §2.11 — Observabilidad: el identificador de petición (logging)
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (§E8, §E7)
  - `knowledge-base/09_decisiones_y_supuestos.md` (SU-03, DD-07)
  - `knowledge-base/11_endpoints_y_casos_de_prueba.md` (C-14, C-15)
  - `knowledge-base/12_criterios_de_evaluacion.md` (§Formato de entrega, checklist)

---

## Matriz de cobertura

### Reglas de negocio (RN-01..RN-16)

| RN | Se implementa en | Se demuestra en |
|---|---|---|
| RN-01 | CH-01 (UNIQUE/índice parcial), CH-04, CH-05/06, CH-08, CH-12, CH-13 | C-02, C-13 |
| RN-02 | CH-08 | C-02 |
| RN-03 | CH-01 (índice parcial), CH-12 (409) | C-07 |
| RN-04 | CH-10 | C-07 |
| RN-05 | CH-12 | C-08 |
| RN-06 | CH-10 (dos grupos), CH-11 | C-09 |
| RN-07 | CH-09 | C-05 |
| RN-08 | CH-07 (+ orden en CH-09) | C-04 |
| RN-09 | CH-14 | C-10, C-12 |
| RN-10 | CH-14 | C-10, C-11 |
| RN-11 | CH-06 (punto único), CH-05 (PATCH 422) | C-16, C-13 |
| RN-12 | CH-02 (migración 4) | C-14 (CH-15) |
| RN-13 | CH-05, CH-06, CH-14 | C-12, C-13 |
| RN-14 | CH-14 | C-06 |
| RN-15 | CH-02 (`errores.py`), usado por CH-04, 05, 06, 08, 12, 13, 14 | C-02, C-16 |
| RN-16 | CH-02 (línea `SISTEMA`), CH-11, CH-12 | C-09, C-07 (consulta `evento_seguridad`) |

### Casos de prueba C

| Caso | Change | Archivo |
|---|---|---|
| C-01 | CH-10 | `test/C-01_param_no_entero.http` |
| C-02 | CH-08 | `test/C-02_registro.http` |
| C-03 | CH-07 (cookie) + CH-10 (401/Bearer) | `test/C-03_cookie.http` |
| C-04 | CH-07 | `test/C-04_anti_enumeracion.http` |
| C-05 | CH-09 | `test/C-05_limite_intentos.http` |
| C-06 | CH-10 (401/403) + CH-14 (lo propio) | `test/C-06_401_vs_403.http` |
| C-07 | CH-12 | `test/C-07_revocar_rol.http` |
| C-08 | CH-12 | `test/C-08_autoproteccion.http` |
| C-09 | CH-11 | `test/C-09_cambio_obligatorio.http` |
| C-10 | CH-14 | `test/C-10_venta_valida.http` |
| C-11 | CH-14 | `test/C-11_venta_sin_stock.http` |
| C-12 | CH-14 | `test/C-12_venta_referencias_invalidas.http` |
| C-13 | CH-06 (con CH-05) | `test/C-13_baja_reposicion_isbn.http` |
| C-14 | CH-15 (disparador desde CH-02) | `test/solo_agregado.sql` |
| C-15 | CH-15 | `test/C-15_sin_n_mas_1.http` + `evidencia/` |
| C-16 | CH-05 (apoyo: CH-04) | `test/C-16_busqueda_paginacion_patch.http` |

### Casos de despliegue D

| Caso | Change |
|---|---|
| D-01 .. D-08 | CH-03 (todos; D-08 usa el `BackgroundTasks` que el TP ya trae) |

### Brechas detectadas

| Brecha | Estado |
|---|---|
| Todas las RN-01..RN-16 y C-01..C-16 / D-01..D-08 tienen al menos un change | **Sin brechas de cobertura** |
| Precio de Bestiario (P-06) | **Resuelta**: 18000.00, ficticio; dataset completo del seed en CH-02 (DD-26) |
| Puerto público (P-04) | **Resuelta**: 8000 (8001 si está ocupado); fallback de la base: Postgres nuevo (DD-27) |
| Red de EasyPanel (P-04/IN-08) | **Pendiente**: se resuelve durante CH-03; placeholder `<RED>` |
| Nombre del grupo y fecha (P-05) | **Pendiente**; placeholders `<NOMBRE>` / `<FECHA>` |
| Ubicación de `main.py` (IN-03) | **Resuelta**: `app/main.py`, `seed.py` en la raíz de `parcial/` (confirmado por el profesor) |
| Código HTTP de "contraseña actual incorrecta" en `cambiar-password` | **Resuelta**: 401 (DD-30); aplicado en CH-11 |
| Colisión de nombres con `parcial/test/C-01.http..C-08.http` del TP | **Resuelta**: los del TP se borran de `parcial/test/` (CH-02, DD-29); los nuevos son `C-xx_tema.http` |
| `app/core/errores.py` (traducción de `IntegrityError`) | No estaba en la lista original de CH-02; se agregó ahí porque lo usan 7 changes |
| `README.md` de `parcial/` y `parcial/evidencia/` | Sin dueño en la lista original; se asignaron a CH-15 |
| P-13 (material de cátedra citado) | **Resuelta**: `docs/catedra/` (cap1 a cap6); cada change lista las secciones exactas (archivo, §X.Y, título). Docker no tiene capítulo (CH-03 usa sólo la consigna y `13_despliegue.md`); `BackgroundTasks` es §3.9 |

---

## Backlog (fuera de los 15 changes — lo que la consigna deja afuera)

| Tema | Idea |
|---|---|
| **Capítulo 7 — Concurrencia** | Bloqueo de filas (`SELECT ... FOR UPDATE`) o control optimista para que dos ventas simultáneas no dejen el stock en negativo; carreras en el conteo de intentos (RN-07); transacciones con nivel de aislamiento explícito. Hoy el único freno es el CHECK `stock >= 0` (el `IntegrityError` se traduce a 409). |
| **Capítulo 8 — Redis** | Limitador de intentos en Redis (en lugar de contar en `intento_acceso`), caché del catálogo, lista de tokens revocados para logout del lado del servidor. |
| Segundo mecanismo de sólo agregado | Rol de base sin permiso de `UPDATE`/`DELETE` sobre `movimiento_stock` (defensa en profundidad; la consigna no lo pide, DD-07). |
| Detrás de proxy | `request.client.host` es la IP del proxy en EasyPanel/Traefik (SU-08); usar `X-Forwarded-For` con cuidado si el parcial se despliega. |

---

## Checklist de entrega (no es un change)

Armar `Parcial_Cap1a6_<NOMBRE>.zip` con las dos carpetas `parcial/` y `despliegue/`, sin `.env`, `.venv`, `.git` ni credenciales (condición eliminatoria si hay credenciales reales). Verificar `alembic upgrade head` sobre base vacía y que el servicio del VPS siga en línea hasta que se publiquen las notas. Detalle en `knowledge-base/12_criterios_de_evaluacion.md`.
