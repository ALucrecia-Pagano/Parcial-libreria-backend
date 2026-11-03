# Parcial Librería (Programación III, UTN FRM) — Instrucciones para Agentes

> Este archivo (y su copia idéntica `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. Si se edita uno, se edita el otro (deben quedar idénticos).

Examen grupal (TUP, UTN FRM). Grupo: Pagano Amanda, Liendo Mateo, Avila Lucas, Valentini Tiziano, García Juan. Cada integrante es dueño de una Parte (3 changes) de `CHANGES.md`. Se entrega un `.zip` con `parcial/` y `despliegue/`. Este archivo es corto a propósito: apuntá siempre al archivo exacto y no leas de más.

---

## Stack Tecnológico

| Capa | Tecnología | Versión mínima |
|------|------------|----------------|
| Lenguaje | Python | 3.12 |
| Web | FastAPI (handlers `async def`) | 0.111 |
| Modelos | SQLModel | 0.0.24 |
| ORM/Motor | SQLAlchemy asincrónico | 2.0 |
| Driver | asyncpg | 0.30 |
| BD | PostgreSQL | 16 |
| Migraciones | Alembic (plantilla async) | 1.13 |
| Config | pydantic-settings | 2.0 |
| Hash | bcrypt | 4.0 |
| Token | PyJWT | 2.8 |
| Servidor | uvicorn (viene con `fastapi[standard]`) | — |
| Contenedor | Docker (solo para `despliegue/`) | 20.10 |

Capas por módulo: `router.py -> service.py -> unit_of_work.py -> repository.py -> models.py`. Detalle: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md) y [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md).

---

## Estructura del repo

- `parcial/` — caps. 5 y 6 (todo el trabajo del parcial va SOLO acá).
- `despliegue/` — el TP de caps. 1–4 tal como se entregó, más Dockerfile, `.dockerignore`, `env.example`, `DEPLOY.md`, `evidencia/`.
- Todo lo generado para agentes vive en la RAÍZ y NUNCA dentro de `parcial/` ni `despliegue/`: `openspec/`, `knowledge-base/`, `CHANGES.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.agents/`, `.atl/`, `skills-lock.json`, `.active-orchestrator-state.json` (todos se commitean).

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar** (índice en [knowledge-base/README.md](knowledge-base/README.md)).

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, alcance, entrega |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Auth, RBAC, rutas públicas |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Tablas, índices, migraciones 3 y 4, seed |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | RN-01..RN-16 del parcial |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Ejercicios E1..E10 |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Estructura obligatoria, variables de entorno |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | DD-xx / SU-xx |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Pendientes (hoy: red de EasyPanel IN-08/P-04, nombre del grupo y fecha P-05) |
| [11_endpoints_y_casos_de_prueba.md](knowledge-base/11_endpoints_y_casos_de_prueba.md) | Endpoints y casos C-01..C-16 / D-01..D-08 |
| [12_criterios_de_evaluacion.md](knowledge-base/12_criterios_de_evaluacion.md) | Cómo se corrige, entrega |
| [13_despliegue.md](knowledge-base/13_despliegue.md) | Dockerfile, VPS, `DEPLOY.md` |

> No quedan inconsistencias de prioridad Alta sin resolver; solo IN-08/P-04 (nombre de la red de EasyPanel), que se cierra en CH-03.

**Material de cátedra**: las secciones "X.Y" que cita la consigna refieren a `docs/catedra/` (cap1..cap6, Markdown). Buscar la sección puntual con Grep del encabezado (ej. `^#+\s*6\.4\.3`), NUNCA leer el archivo entero.

---

## Skills Disponibles

Las skills viajan con el repo: copias de proyecto en `.claude/skills/` Y en `.agents/skills/`. Para instalar una nueva: `npx skills add <repo> --skill <name> -a claude-code --copy` (nunca `-g`, nunca `-a '*'`) y copiarla a `.agents/skills/`.

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Backend** | FastAPI / SQLModel / repos + UoW / Alembic | `fastapi`, `postgresql-table-design` |
| **Orquestación** | OPSX: explorar, proponer, aplicar, archivar | `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-archive-change`, `openspec-sync-specs`, `openspec-update-change` |

Cargá la skill correspondiente ANTES de escribir código. Las skills globales de testing (`tdd`, `python-testing-patterns`, `vitest`, partes pytest de `python-pro`) NO aplican en este proyecto.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md`. En ESTE repo el registry SÍ está versionado (los integrantes pueden no tener las skills globales).

---

## Roadmap de Changes

Plan completo en [CHANGES.md](CHANGES.md): **15 changes (CH-01..CH-15) en 5 partes de 3 changes**, una parte por integrante.

- **Camino crítico (7)**: `CH-01 → CH-02 → CH-07 → CH-10 → CH-06 → CH-14 → CH-15`.
- **Independiente**: CH-03 (despliegue Docker/VPS), puede arrancar en paralelo con CH-01.
- **Primer change**: `CH-01` (`base-config-modelos-migracion-3`); CH-01 y CH-03 pueden empezar a la vez.

**Antes de cualquier `/opsx:propose CH-NN-<nombre>`**: leé la ficha de ese change en `CHANGES.md`, sus dependencias y sus archivos de "Leer antes". El prefijo `CH-xx` es de los changes; `C-xx`/`D-xx` son casos de prueba de la consigna: no mezclar.

---

## Reglas Duras (específicas del proyecto)

> Reglas globales ya definidas en `~/.claude/CLAUDE.md` (orquestador, governance, engram): el proyecto las hereda. Acá viven solo las reglas **específicas de este proyecto** + las universales que el global no cubra. El "Strict TDD Mode" del global queda REEMPLAZADO en este proyecto por el "TDD con .http" de abajo.

1. NUNCA commitees nada → los commits los hace la usuaria/el integrante, con conventional commits en español y el change entre paréntesis, ej. `feat(CH-03): ...`.
2. NUNCA escribas credenciales, contraseñas ni claves de firma en el repo → usá solo datos ficticios (los de la consigna, ej. `admin@example.com`). Los secretos entran solo por entorno (`--env-file` en el servidor).
3. NUNCA toques la lógica de `despliegue/` → ahí solo se agregan los archivos del despliegue (`Dockerfile`, `.dockerignore`, `env.example`, `DEPLOY.md`, `evidencia/`).
4. NUNCA escribas pytest ni pruebas en `.py` → verificá con los `.http` de `test/` y con psql (`test/` contiene solo `.http` y un único `solo_agregado.sql`).
5. Si una skill contradice este `AGENTS.md`, manda `AGENTS.md`.
6. NUNCA un schema de entrada sin `extra="forbid"` → los PATCH usan `exclude_unset=True`; NUNCA se devuelve `password_hash` en una respuesta.
7. NUNCA un `commit()` en un repositorio ni en un router → los repositorios solo hacen `flush()`; el servicio recibe el UoW y lo abre con `async with`.
8. NUNCA escribir `libro.stock` fuera del punto único de escritura (CH-06) ni por PATCH → todo cambio de stock genera su `movimiento_stock`; la única excepción es `seed.py`, que igual deja `stock` = suma de movimientos.
9. NUNCA cambiar el esquema fuera de Alembic → nada de `create_all`; leer la migración antes de aplicarla.
10. NUNCA editar las migraciones 1 y 2 → solo se agregan la 3 (autogenerada) y la 4 (a mano, con el disparador).
11. NUNCA consultar antes para chequear duplicados → atrapar `IntegrityError` y devolver 409 con mensaje propio.
12. Usar los nombres EXACTOS de la consigna para tablas, columnas, endpoints y campos (la corrección los usa).
13. Solo vale la numeración RN-01..RN-16 del parcial → las RN del TP no se citan.
14. Los casos de prueba se nombran `C-xx_tema.http` / `D-xx_tema.http`; los `.http` auxiliares de un change, `CH-xx_tema.http` → no mezclar los prefijos.
15. Todos los handlers son `async def` → bcrypt corre en `asyncio.to_thread` con semáforo, nunca bloqueando el loop.
16. El motor y la sesión se crean en el lifespan → `POSTGRES_PASSWORD` y `JWT_SECRET` NUNCA tienen valor por defecto.
17. NUNCA carga perezosa → toda relación que se lee se precarga en el repositorio (`selectinload`/`joinedload`), dentro del método que la necesita.
18. El token viaja SOLO en la cookie HttpOnly `access_token` → NUNCA en el cuerpo de la respuesta ni leído del header `Authorization`.
19. Ningún error devuelve texto de la base ni una traza, y ninguna entrada inválida termina en 500 (RN-15) → `IntegrityError` traducido a mensaje propio.

### TDD con .http (reemplaza al Strict TDD Mode del global)

Sin pytest (regla 4), el ciclo rojo-verde se hace con lo que el proyecto sí permite:

1. **Rojo**: escribir el `.http` de `test/` (o la consulta psql / `solo_agregado.sql`) con la respuesta esperada — código de estado y cuerpo — y correrlo para verlo FALLAR.
2. **Verde**: implementar lo mínimo y volver a correrlo hasta que pase.
3. **Refactor**: mejorar sin cambiar el comportamiento, volviendo a correr los `.http` del change después de cada paso.

Cubrir al menos el caso feliz y un caso de error por comportamiento (ej. 201 y 409). En el resumen de `/opsx:apply`, la evidencia es la tabla `tarea → .http → esperado → obtenido`.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        -> entender el dominio
2. Identificar el change en CHANGES.md           -> respetar dependencias
3. /opsx:propose CH-NN-nombre                    -> proposal + design + specs + tasks
4. /opsx:apply (cargando skills)                 -> respetando las reglas duras
5. Verificar con los .http y psql                -> comparar con los códigos esperados
6. /opsx:archive CH-NN-nombre + marcar [x]       -> cerrar el change y avisar al grupo
```

Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.

---

## Reglas propias

- NUNCA des por terminado un change sin haber corrido sus .http contra la base
  real y pegado la salida (código de estado y cuerpo) en el verify, porque
  "debería funcionar" no es evidencia y el profe corrige los casos C y D
  ejecutándolos.
- NUNCA modifiques archivos que no figuran en el tasks.md del change en curso;
  si hace falta tocar algo de otro change, frená y avisá, porque somos cinco
  trabajando en paralelo y un cambio fuera de alcance pisa el trabajo de otro
  integrante.
- SIEMPRE cerrá cada change con un resumen en criollo de no más de 10 líneas:
  qué hiciste, qué archivos tocaste y por qué, porque cada integrante tiene que
  poder explicar y defender su parte en clase.
