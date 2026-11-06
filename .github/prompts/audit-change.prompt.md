---
description: "Auditar un CH-NN completado contra CHANGES.md, OpenSpec, el código, las reglas del repositorio y sus verificaciones"
name: "Auditar Change completado"
argument-hint: "[CH-NN o nombre; opcionalmente: proposal, apply o completed]"
agent: "agent"
---

Actuá como auditor técnico del repositorio Parcial Librería. Esta tarea es de
solo lectura: no modifiques archivos, no crees commits y no marques changes
como completados.

## Change a auditar

Si recibís un argumento, usalo para identificar el change (`CH-NN` o su nombre)
y, si se indica, su etapa (`proposal`, `apply` o `completed`). Si no se indica
la etapa, inferila desde `CHANGES.md`, `openspec/changes/` y el estado de Git.
Si no recibís argumento, detectá el último change marcado como completado en
[CHANGES.md](../../CHANGES.md), considerando su orden, estado y dependencias.
No confundas `CH-NN` con los casos de prueba `C-xx` y `D-xx`.

La auditoría debe adaptarse a la etapa:

- **`proposal`**: validá la coherencia de `proposal.md`, `design.md`,
  `tasks.md`, specs delta, dependencias, alcance, archivos previstos y reglas
  del repositorio. No exijas que exista código aplicado ni `.http` ejecutado.
- **`apply`**: validá que la implementación siga la propuesta y las tareas,
  además del código, migraciones y `.http` disponibles. Señalá tareas
  incompletas como hallazgos.
- **`completed`**: aplicá todos los controles de documentación, código,
  alcance y evidencia, y determiná si el change está listo para archivarse.

## Protocolo

1. Leé la ficha del change en [CHANGES.md](../../CHANGES.md), incluyendo
   dependencias, archivos, criterios de entrada y archivos `.http` esperados.
2. Revisá los artefactos del change en `openspec/changes/`: `proposal.md`,
   `design.md`, `tasks.md` y las specs delta que existan.
3. Leé únicamente los archivos de `knowledge-base/` indicados por el change y
   las secciones puntuales de `docs/catedra/` que correspondan. No leas archivos
   completos de cátedra si alcanza con buscar el encabezado indicado.
4. Inspeccioná `git status --short`, el diff del change y el historial reciente.
   Si hay cambios no commiteados, separalos de los cambios ya integrados y
   declaralo explícitamente.
5. Contrastá documentación y código real:
   - todos los archivos y tareas declarados existen y están implementados;
   - no hay archivos modificados fuera del alcance del change;
   - las dependencias necesarias están disponibles;
   - los nombres de tablas, columnas, endpoints y campos coinciden exactamente
     con la consigna;
   - la implementación respeta
     `router.py -> service.py -> unit_of_work.py -> repository.py -> models.py`;
   - los handlers son `async def`, no hay carga perezosa y los repositorios no
     hacen `commit()`;
   - los cambios de esquema usan únicamente Alembic y no modifican las
     migraciones 1 o 2;
   - los schemas de entrada usan `extra="forbid"`, los PATCH usan
     `exclude_unset=True` y nunca se expone `password_hash`;
   - los errores de integridad e input inválido se traducen a respuestas
     propias, sin texto de base ni trazas;
   - el token, si aplica, viaja únicamente en la cookie HttpOnly
     `access_token`;
   - todo cambio de stock respeta el punto único de escritura y registra su
     `movimiento_stock`.
6. Revisá los `.http` correspondientes y su evidencia. Ejecutalos solo si la
   base real, el servidor y las herramientas ya están disponibles; no inventes
   resultados. Si no pueden ejecutarse, informá la precondición faltante y
   distinguí claramente entre “no verificado” y “falló”.
7. No propongas arreglos genéricos. Para cada problema indicá archivo, símbolo
   o línea aproximada, regla incumplida, impacto y corrección concreta.

## Criterio de veredicto

- **LISTO PARA CERRAR**: el objetivo y las verificaciones pasan, no hay
  incumplimientos bloqueantes y las limitaciones de entorno están explicitadas.
- **REQUIERE AJUSTES MENORES**: solo faltan correcciones acotadas que no
  cambian el diseño ni comprometen seguridad, datos o contratos.
- **BLOQUEADO**: falta funcionalidad, hay una dependencia incumplida, una
  violación de una regla dura, un problema de seguridad/datos o una verificación
  esencial fallida.

## Formato obligatorio de salida

### Veredicto del CHANGE `CH-NN — nombre`: 🟢 LISTO PARA CERRAR | 🟡 REQUIERE AJUSTES MENORES | 🔴 BLOQUEADO

Explicá el veredicto en una o dos oraciones.

### Auditoría cruzada

| Control | Resultado | Evidencia |
|---|---|---|
| `CHANGES.md` / OpenSpec vs código | ✅ / ⚠️ / ❌ | archivos y líneas |
| Objetivo y alcance | ✅ / ⚠️ / ❌ | criterio de aceptación |
| Dependencias | ✅ / ⚠️ / ❌ | changes relacionados |
| Arquitectura y reglas duras | ✅ / ⚠️ / ❌ | archivo y símbolo |
| Migraciones y modelo de datos | ✅ / ⚠️ / ❌ / N/A | migración y tablas |
| `.http` y evidencia | ✅ / ⚠️ No verificado / ❌ | archivo y resultado |
| Cambios fuera de alcance | ✅ / ⚠️ / ❌ | `git status` o diff |

### Hallazgos

Listá primero los bloqueantes, luego los ajustes menores. Cada hallazgo debe
tener:

1. severidad (`BLOQUEANTE` o `MENOR`);
2. archivo y línea o símbolo;
3. regla o criterio incumplido;
4. corrección concreta.

Si no hay hallazgos, escribí: `Ninguno.`

### Acciones antes de avanzar

Si está listo: `Ninguna. La persona responsable puede hacer su commit y
continuar con el siguiente change.` Si no está listo, enumerá únicamente las
acciones necesarias, sin implementarlas.

### Evidencia no ejecutada

Enumerá los `.http`, comandos o verificaciones que no pudieron ejecutarse y la
razón exacta. Nunca presentes una verificación teórica como resultado obtenido.
