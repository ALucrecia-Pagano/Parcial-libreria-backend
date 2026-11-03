# Visión y Objetivos

> Fuente primaria: `docs/Parcial_Cap1a6_Consigna.pdf` (24 págs.). Todo lo que sigue sale de ahí salvo lo marcado como **Suposición**.

## Propósito del sistema

Parcial grupal de **Programación III** (UTN FRM, Tecnicatura Universitaria en Programación), "Unidades 1 a 6 — Del objeto a la transacción". Es la **continuación del TP de la librería** (capítulos 1 a 4, ya implementado y funcionando) y lo lleva hasta el capítulo 6. A un catálogo, clientes y ventas ya construidos se les agrega:

1. **Acceso con usuarios y roles** (cap. 5): autenticación con bcrypt + JWT en cookie HttpOnly, autorización por roles vigentes consultados en la base.
2. **Repositorios + Unit of Work** (cap. 6): arquitectura en capas `Router → Service → UoW → Repository → Model`, con transacciones que agrupan las escrituras de cada operación de negocio.
3. **Despliegue aparte** (ejercicios 9 y 10): el TP de los capítulos 1 a 4 *tal como se entregó* se empaqueta en Docker y se publica en el VPS.

Grupo: Pagano Amanda, Liendo Mateo, Avila Lucas, Valentini Tiziano, García Juan.

## Dos proyectos en un solo .zip

| Carpeta | Qué es | Qué se toca |
|---|---|---|
| `parcial/` | El TP ampliado con todo lo del parcial **salvo el despliegue** (caps. 5 y 6) | Todo el trabajo de código nuevo |
| `despliegue/` | El TP de caps. 1 a 4 **tal como se entregó** | Sólo se agregan `Dockerfile`, `.dockerignore` (ya existe), `env.example`, `DEPLOY.md` y `evidencia/`. **Su lógica no se toca** (salvo defecto propio que impida arrancar en el contenedor, anotado en `DEPLOY.md`) |

Regla del repo: la `knowledge-base/` vive en la raíz, nunca dentro de `parcial/` ni `despliegue/`.

## Objetivos de aprendizaje (los 7 de la consigna)

1. Reorganizar una API asincrónica en capas Router → Service → UoW → Repository → Model, donde cada capa sabe lo suyo y nada más.
2. Evolucionar un esquema versionado con Alembic: una migración autogenerada y leída antes de aplicarla, y otra escrita a mano para lo que la comparación automática no ve.
3. Autenticar con contraseñas bcrypt y token en cookie HttpOnly, sin frenar el servidor y sin revelar qué cuentas existen.
4. Autorizar consultando los roles en la base en cada petición, con vigencia, distinguiendo siempre 401 de 403.
5. Agrupar en una sola transacción las escrituras de una operación de negocio (un fallo en el medio no deja datos a medias).
6. Delegar en la base lo que la base garantiza: unicidad entre vigentes, claves foráneas, CHECK y el sólo-agregado.
7. Empaquetar el TP de caps. 1–4 en Docker y ponerlo en línea en el VPS sin filtrar secretos ni exponer lo que no debe.

## Objetivos por actor

| Actor | Objetivo principal | Secundarios |
|---|---|---|
| Administrador (ADMIN) | Mantener el catálogo, reponer stock, administrar personal y roles | Ver historial de seguridad (`/eventos`), ver todas las ventas |
| Vendedor (VENDEDOR) | Registrar ventas y atender clientes en el mostrador | Alta/consulta de clientes y sus perfiles |
| Cliente (CLIENTE) | Registrarse solo en la web y consultar **sus** compras | Cambiar contraseña, ver `/auth/yo` |
| Cualquiera (anónimo) | Ver el catálogo de libros (público) | Registrarse, iniciar sesión |
| Equipo de desarrollo | Entregar el .zip con ambos proyectos y evidencia | Mantener el despliegue en línea hasta publicadas las notas |

## Alcance

- Módulos mínimos: `health`, `usuarios`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`.
- 5 tablas nuevas/cambiadas relevantes (ver `04`) + 2 migraciones nuevas (3ª autogenerada, 4ª a mano con el disparador).
- Auth completa (registro, login con límite de intentos, logout, `/auth/yo`, cambio de contraseña), roles con vigencia y revocación sin borrar.
- Venta transaccional con descuento de stock y movimientos; stock con única vía de escritura.
- Listados con envoltorio `{items, total, page, size, pages}`.
- Casos de prueba C-01..C-16 (en `test/` como `.http` + `solo_agregado.sql`) y D-01..D-08 (evidencia del despliegue). Ver `11`.
- Despliegue del TP caps. 1–4 en el VPS (ver `13`).

## Fuera de alcance (explícito en la consigna)

- **Concurrencia (cap. 7)**: no se evalúa. Dos ventas simultáneas del último ejemplar pueden producir una *actualización perdida* (ambas leen `stock = 1` y escriben `0`); el nivel de aislamiento por defecto lo permite y el bloqueo que lo evita es tema de la próxima clase.
- **Colas de tareas con Redis (cap. 8)**: el aviso al cliente se resuelve con `BackgroundTasks` (mismo proceso); si el proceso se reinicia el aviso se pierde y nadie lo reintenta (aceptado: el aviso es simulado).
- Segundo mecanismo de sólo-agregado (rol de base sin permiso de modificar la tabla): no se pide; se usa un solo rol de base.
- Invalidación de sesiones al cambiar contraseña / emisión de token nuevo: no hay; "login tradicional con cookie".
- Docker Compose: no se usa; la base no forma parte del paquete.

## Entrega

- Una por grupo, un único `.zip` llamado `Parcial_Cap1a6_<NombreDelGrupo>.zip`, lo sube un solo integrante al campus (tarea: https://campustest.frm.utn.edu.ar/mod/assign/view.php?id=1915). Fecha límite: se publica en el campus (no figura en el PDF).
- **Sin** `.venv`, `__pycache__` ni `.env` (en ninguna de las dos carpetas). Si incluye `.git`, se revisa el historial: una contraseña subida alguna vez obliga a cambiarla.
- Detalle del contenido: ver `12_criterios_de_evaluacion.md` (sección "Formato de entrega").

## Métricas de éxito

Ver `12_criterios_de_evaluacion.md` (pesos por criterio, suman 100 %). Condición eliminatoria: un proyecto que no levanta, no crea el esquema con `alembic upgrade head` sobre base vacía o contiene credenciales reales (repo, imagen o zip) **no se corrige** hasta subsanar.
