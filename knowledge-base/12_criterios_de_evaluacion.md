# Criterios de Evaluación y Formato de Entrega

## Criterios con sus pesos (suman 100 %)

| Criterio | Ejercicio | Peso | Qué se mira |
|---|---|---|---|
| Proyecto, configuración y ciclo de vida | E1 | **6 %** | Estructura, `Settings` sin secretos por defecto, motor y fábrica creados en el lifespan, `get_session`, salud |
| Modelos, relaciones y migraciones | E2 | **10 %** | Restricciones, índices únicos parciales, navegación, dos migraciones nuevas (una a mano), upgrade y downgrade |
| Contratos y CRUD | E3 | **8 %** | Contratos separados, `extra="forbid"`, códigos, ninguna entrada inválida en 500, PATCH parcial, envoltorio y paginación de la sec. 2.9 |
| Autenticación | E4 | **14 %** | bcrypt fuera del bucle y con semáforo, orden del login, límite, hash ficticio, cookie HttpOnly |
| Autorización | E5 | **12 %** | 401 y 403, roles vigentes en la base, autoprotección, dos grupos de rutas, cambio obligatorio de contraseña, lo propio |
| Repositorios y Unit of Work | E6 | **16 %** | Dos jerarquías, clase del modelo, `flush` y no `commit`, precarga en el repositorio, quién crea, abre, confirma y cierra, operaciones de varias escrituras, un solo punto de escritura del stock |
| Integridad | E7 | **10 %** | Disparador de sólo agregado; intento de acceso en su propia sesión con su comentario; eventos en la misma transacción |
| Lecturas sin N+1 y asincronía | E8 | **6 %** | Consultas fijas en el detalle; ninguna llamada bloqueante; aviso en segundo plano visible |
| Contenedor: la imagen | E9 | **11 %** | Sobre el TP caps. 1–4: imagen base `python:3.12-alpine`, capas en orden, usuario sin privilegios, sin secretos en la imagen, migraciones al arrancar, `HEALTHCHECK`, ejecución con `docker run` y variables por `--env-file` |
| Despliegue en el VPS | E10 | **7 %** | El TP caps. 1–4 en línea en la URL declarada, `DEPLOY.md` completo, los casos D con su evidencia |

Suma: 6+10+8+14+12+16+10+6+11+7 = **100**. (Coincide con los puntajes de los Ejercicios; E1–E8 = 82 pts en `parcial/`, E9–E10 = 18 pts en `despliegue/`.)

## Condiciones eliminatorias / descuentos

Un proyecto que **no levanta**, que **no crea su esquema con `alembic upgrade head` sobre una base vacía** o que **contiene credenciales reales en el repositorio, en la imagen o en el zip** **no se corrige** hasta que se subsane.

Si el despliegue **no está accesible** en el momento de la corrección, el criterio de despliegue en el VPS se evalúa **sólo** sobre lo que consta en `DEPLOY.md` y en `evidencia/` del despliegue, y los casos D que no se puedan comprobar **no suman**. El despliegue debe seguir en línea hasta que se publiquen las notas.

## Formato de entrega

- **Una entrega por grupo**, un único `.zip` llamado `Parcial_Cap1a6_<NombreDelGrupo>.zip`, que sube un solo integrante al campus (tarea: https://campustest.frm.utn.edu.ar/mod/assign/view.php?id=1915). La fecha límite se publica en el campus.
- El `.zip` contiene **dos carpetas** (dos proyectos distintos):

### `parcial/`
Proyecto ampliado con todo lo del parcial **salvo el despliegue**: código fuente completo, `requirements.txt`, `env.example`, `alembic.ini`, `migrations/`, `test/`. Incluye:
- `README.md` con **nombres y apellidos** de los integrantes y los pasos desde cero (entorno virtual, dependencias, `.env` con cómo generar la clave de firma, `alembic upgrade head`, `python seed.py`, arranque del servidor).
- `evidencia/` con la captura o fragmento de consola del **caso C-15** (consultas del detalle de una venta con 2 renglones y de otra con 4) y la captura de **`psql` del caso C-14**.

### `despliegue/`
TP caps. 1–4 **tal como se entregó**, con `Dockerfile`, `.dockerignore`, `env.example` (con la forma de `DATABASE_URL`, sin valores reales) y el `DEPLOY.md`. Incluye `evidencia/` con la salida de **cada caso D** (D-01..D-08).

### No debe contener
`.venv`, `__pycache__` (en ninguna de las dos carpetas) ni el archivo `.env`. Si incluye `.git`, también se revisa su historial: una contraseña que alguna vez se subió y se borró sigue en el historial, y se pide además cambiarla.

## Checklist rápido de pre-entrega

- [ ] `alembic upgrade head` sobre base vacía → OK; `downgrade base` → OK; `upgrade head` → OK
- [ ] `python seed.py` deja los datos de `04`
- [ ] `.http` C-01..C-16 con respuesta esperada comentada; `solo_agregado.sql` para C-14
- [ ] `parcial/evidencia/`: C-15 y C-14
- [ ] Sin secretos en repo/imagen/zip; sin `.env`, `.venv`, `__pycache__`
- [ ] `despliegue/`: Dockerfile, .dockerignore, env.example, DEPLOY.md, evidencia/ D-01..D-08
- [ ] Despliegue en línea en la URL declarada
- [ ] README de `parcial/` con integrantes
