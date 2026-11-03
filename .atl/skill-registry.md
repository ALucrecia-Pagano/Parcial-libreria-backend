# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

Project: Parcial_Libreria. Stack: FastAPI + SQLModel/SQLAlchemy async + asyncpg + PostgreSQL 16 + Alembic + pydantic-settings + bcrypt + PyJWT + Docker.

**REGLA DURA DEL PROYECTO: PROHIBIDO pytest y cualquier test .py.** La verificacion es SOLO con archivos `.http` en `test/` y un unico `solo_agregado.sql` via psql. Las skills de testing de Python (ver "No aplica") NO se inyectan.

## User Skills

| Trigger | Skill | Scope | Path |
|---------|-------|-------|------|
| Working with FastAPI APIs, Pydantic models, dependencies, SSE | fastapi | PROJECT | .claude/skills/fastapi/SKILL.md (copia: .agents/skills/fastapi) |
| Designing/reviewing PostgreSQL schema, types, indexes, constraints | postgresql-table-design | PROJECT | .claude/skills/postgresql-table-design/SKILL.md (copia: .agents/skills/) |
| Implement tasks from an OpenSpec change ("opsx apply") | openspec-apply-change | PROJECT | .claude/skills/openspec-apply-change/SKILL.md |
| Archive completed change ("opsx archive") | openspec-archive-change | PROJECT | .claude/skills/openspec-archive-change/SKILL.md |
| Explore ideas before/during a change ("opsx explore") | openspec-explore | PROJECT | .claude/skills/openspec-explore/SKILL.md |
| Propose a change with all artifacts ("opsx propose") | openspec-propose | PROJECT | .claude/skills/openspec-propose/SKILL.md |
| Sync delta specs to main specs ("opsx sync") | openspec-sync-specs | PROJECT | .claude/skills/openspec-sync-specs/SKILL.md |
| Revise a change's planning artifacts ("opsx update") | openspec-update-change | PROJECT | .claude/skills/openspec-update-change/SKILL.md |
| Foundation flow, KB, roadmap, AGENTS.md generation | active-orchestrator, kb-creator, roadmap-generator, agent-instruction, find-skill(s), discovery-research, web-scraper, skill-creator | GLOBAL (workflow, no coding rules) | ~/.claude/skills/<name>/SKILL.md |

### NO aplica en este proyecto (sin pytest) - NO inyectar reglas
| Skill | Scope | Motivo |
|-------|-------|--------|
| python-testing-patterns | GLOBAL | pytest prohibido |
| tdd | GLOBAL | red-green-refactor con tests .py prohibido; verificacion solo `.http` + `solo_agregado.sql` |
| vitest | GLOBAL | JS/TS, fuera del stack |
| python-pro | GLOBAL | Solo sus partes de tipado/async/ruff son utiles; la parte de pytest NO aplica. No se indexan reglas |

Nota: el "Strict TDD Mode" del CLAUDE.md global choca con la regla dura del proyecto; prevalece la regla del proyecto (sin tests .py).

## Compact Rules

### fastapi
- Usar `Annotated[...]` para Path/Query/Header y `Depends`; crear alias reutilizable (`CurrentUserDep = Annotated[User, Depends(get_current_user)]`).
- NO usar `...` (Ellipsis) como default de params ni de campos Pydantic; no usar `RootModel`.
- Preferir return type annotation; usar `response_model` solo si el schema publico difiere del valor interno (ej: ocultar password hash).
- Declarar `prefix`, `tags` y `dependencies` compartidas en el `APIRouter`; incluir routers con `include_router`.
- Una operacion HTTP por funcion (no mezclar GET/POST en un handler).
- Async: `async def` solo si todo lo que se awaitea es async; codigo bloqueante (bcrypt) en `def` o via threadpool/Asyncer.
- SQLModel preferido sobre SQLAlchemy puro; HTTPX sobre requests; Asyncer sobre AnyIO/asyncio.
- Entrypoint en `pyproject.toml` `[tool.fastapi] entrypoint`; dev con `fastapi dev`, prod con `fastapi run`.
- Dependencias con `yield` para sesion/UoW (cierre y commit/rollback en la dependencia).

### postgresql-table-design
- PK: `BIGINT GENERATED ALWAYS AS IDENTITY` (no `serial`); UUID solo si hace falta opacidad.
- Tipos: `TEXT` (+ `CHECK (length<=n)`), `NUMERIC(p,s)` para dinero (nunca `money`/float), `TIMESTAMPTZ` (nunca `timestamp`), `BOOLEAN NOT NULL`.
- `NOT NULL` donde semanticamente corresponda + `DEFAULT`; `CHECK` row-local (NULL pasa: combinar con NOT NULL), ej `CHECK (precio > 0)`, `CHECK (stock >= 0)`.
- FK: siempre `ON DELETE/UPDATE` explicito e INDEXAR la columna FK a mano (Postgres no la indexa).
- UNIQUE permite multiples NULL; usar `NULLS NOT DISTINCT` (PG15+; PG16 ok) si corresponde.
- Normalizar a 3NF; desnormalizar solo con evidencia medida.
- Enums solo para sets chicos y estables; si evolucionan, `TEXT`+`CHECK` o tabla de lookup.
- Identificadores `snake_case` sin comillas. Los huecos en identity son normales.
- Integridad delegada a la BD (constraints), no solo a la app.

### openspec-apply-change / archive / explore / propose / sync-specs / update-change
- Verificar raiz con `openspec list --json` (`root` no nulo) antes de escribir; nunca crear `openspec/` a mano.
- Estado siempre via CLI: `openspec status --change "<n>" --json`, `openspec instructions apply|<artifact> --change "<n>" --json`.
- apply: implementa tasks.md marcando `[x]`; propose: crea proposal/design/specs/tasks; update-change nunca edita codigo; explore no implementa.
- archive: sincroniza delta specs a `openspec/specs/` y mueve a `openspec/changes/archive/YYYY-MM-DD-<n>/`.
- Si hay `--store <id>`, mantenerlo en todos los comandos.
- En este proyecto las tasks de verificacion son `.http` + `solo_agregado.sql`, NUNCA pytest.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| AGENTS.md (proyecto) | NO existe en la raiz del repo (solo ~ /AGENTS.md del home, que es el orquestador OPSX global) | Pendiente: agent-instruction |
| Roadmap de changes | CHANGES.md | Indice de changes |
| Knowledge base | knowledge-base/ (01..13 + README) | 11_endpoints_y_casos_de_prueba.md, 12_criterios_de_evaluacion.md, 13_despliegue.md |
| OpenSpec | openspec/ | specs y changes |
| Estado foundation | .active-orchestrator-state.json | |
| Skills lock | skills-lock.json | |

Read the convention files listed above for project-specific patterns and rules.
