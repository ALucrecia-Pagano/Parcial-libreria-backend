# Preguntas Abiertas

> Las respuestas de la consigna oficial (págs. 16–18 y anexos) son autoritativas y pisan lo inferido antes. Lo **Resuelta** se conserva como historial; sólo lo marcado **Abierta** sigue pendiente.

## Inconsistencias detectadas

| ID | Estado | Tema | Resolución |
|---|---|---|---|
| IN-01 | **Resuelta** | Maquetado de las tablas del PDF | Las tablas de endpoints (págs. 16–18) quedaron confirmadas y se reemplazaron en `11`. |
| IN-02 | **Resuelta** | Verbos/rutas de los endpoints | `GET /{editoriales,generos,autores}/{id}/libros` son **abiertos** (200/404). Ver `11`. |
| IN-03 | **Resuelta** | Ubicación de `main.py` | **Confirmado por el profesor:** `app/main.py` (como el TP) y `seed.py` en la raíz de `parcial/`. |
| IN-04 | **Resuelta** | Seed del TP vs. seed del parcial | `parcial/` usa `python seed.py` (vacía las tablas, venta 1 = 69000.00); `despliegue/` sigue con `python -m scripts.seed` (TP, 71000.00). Documentarlo en ambos README. |
| IN-05 | **Resuelta** | `env.example` vs `.env.example` | En `despliegue/` se **agrega** `env.example` y se deja el `.env.example` del TP como está. En `parcial/` se crea `env.example`. |
| IN-06 | **Resuelta** | `SQL_ECHO` vs `DEBUG` | El TP lee `DEBUG`, no `SQL_ECHO`. En `despliegue/` no se toca nada: se anota en `DEPLOY.md` que `SQL_ECHO=false` del `--env-file` no tiene efecto (inofensivo). En `parcial/`, `Settings` lee `SQL_ECHO`. |
| IN-07 | **Resuelta** | Fila de requisitos corrupta | Docker >= 20.10; uvicorn viene con `fastapi[standard]`. |
| IN-08 | **Abierta** (parcial) | Host de la base: consigna vs. VPS | Con `docker run` común el contenedor no resuelve `calculadora_db`; hay que unirlo a la red de EasyPanel. Falta sólo el nombre de la red (se resuelve en CH-03). Ver P-04. |

## Preguntas

| ID | Estado | Pregunta | Respuesta / decisión |
|---|---|---|---|
| P-01 | **Resuelta** | `movimiento_stock.usuario_id` nulo; usuario del "Stock inicial" | **NOT NULL.** Los movimientos "Stock inicial" del seed los hace `admin@example.com`. |
| P-02 | **Resuelta** | Valores de `motivo` | Texto libre: "Stock inicial", "Reposición", "Venta". Sin CHECK. |
| P-03 | **Resuelta** | Nombres de variables de entorno | `JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO`, `COOKIE_SECURE`, `DB_POOL_SIZE`, `POSTGRES_USER/PASSWORD/DB/HOST/PORT` (URL armada con `@computed_field`, driver `postgresql+asyncpg`) y `SQL_ECHO`. **Sin default** para `POSTGRES_PASSWORD` ni `JWT_SECRET`. Ver `08`. |
| P-04 | **Abierta** (parcial) | Red de EasyPanel y puerto público; creación de la base | **Resuelto:** puerto público **8000**; si está ocupado, **8001**. Base: el PostgreSQL de la calculadora con la base nueva `libreria` (la crea Amanda a mano desde la consola de EasyPanel); **si eso falla, se crea un Postgres nuevo** (fallback documentado en `13` y CH-03). **Pendiente:** nombre de la red de EasyPanel para `--network` (se resuelve durante CH-03). |
| P-05 | **Abierta** | Nombre del grupo y fecha límite | Usar placeholders `<NOMBRE>` / `<FECHA>` hasta saberlos. |
| P-06 | **Resuelta** | Precios del seed | Rayuela 25000.00, Antología 30000.00, Respiración artificial 27000.00; Ficciones 22000.00 (de 25000 + 2 x 22000 = 69000.00). **Bestiario 18000.00**, valor ficticio (la consigna no lo da y ningún caso lo usa). Dataset completo del seed (editoriales, géneros, autores, ISBN) ficticio: ver `04` y DD-26. |
| P-07 | **Resuelta** | `otorgada_por` | FK nullable a `usuario.id`; en el seed es NULL (actor SISTEMA). |
| P-08 | **Resuelta** | Reponer un libro dado de baja | **409** (RN-13). |
| P-09 | **Resuelta** | Sesión en logout / yo / cambiar-password | `POST /auth/logout` funciona sin sesión (200); `GET /auth/yo` y `POST /auth/cambiar-password` exigen sesión (401). |
| P-10 | **Resuelta** | PATCH de géneros | **No existe** `PATCH /generos`. |
| P-11 | **Resuelta** | Matriz de `/ventas` y `/clientes` | Confirmada por la tabla de `11`: VENDEDOR o ADMIN. |
| P-12 | **Resuelta** | Figura 1 | No agrega nada fuera de las tablas de las págs. 5–6. |
| P-13 | **Resuelta** | Material de cátedra citado (2.6, 2.8, 2.9, 3.6, ... 6.x) | Está en `docs/catedra/` (cap1 a cap6, Markdown); las «secciones X.Y» refieren a esos archivos. **Nunca leerlos enteros:** Grep del encabezado (`^#+\s*6\.4\.3`) y leer sólo esa sección. Cada change lista en «Leer antes» las secciones que aplican (ver `CHANGES.md`). Docker no tiene capítulo en el material (CH-03 usa sólo la consigna E9/E10 y `13_despliegue.md`); `BackgroundTasks` es §3.9 de `cap3-asincronia.md`. |
| P-14 | **Resuelta** | ¿Se anota en `intento_acceso` el intento rechazado con 429? | **No** se registra. |
| P-15 | **Resuelta** | Mensaje de página inexistente | «La página 4 no existe: hay 3» (con los números que correspondan). |
| P-16 | **Resuelta** | `HEALTHCHECK` | `--interval=30s --retries=3 --start-period=20s`. |
| P-17 | **Abierta** (baja) | `[DISCOVERY]` `scale` inferida como `team` | Sin cifras; no bloquea. |
| P-18 | **Resuelta** | ¿El TP ya trae `BackgroundTasks`? | Sí: `ventas/tasks.py`. D-08 se verifica sin corregir el TP (confirmar al desplegar que el logger se ve en `docker logs`). |

## Abiertas hoy

IN-08/P-04 (sólo el nombre de la red de EasyPanel; se resuelve en CH-03), P-05 (nombre del grupo y fecha), P-17 (baja).
