# Parcial Librería (Programación III, UTN FRM) — Base de Conocimiento

Base de conocimiento generada a partir de `docs/Parcial_Cap1a6_Consigna.pdf` (fuente primaria). Se centra en el **delta** respecto del TP de los capítulos 1 a 4 (ya implementado): acceso con usuarios y roles, repositorios + Unit of Work, integridad en la base y despliegue aparte en Docker/VPS.

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, 7 objetivos, dos proyectos (`parcial/` y `despliegue/`), alcance y fuera de alcance, entrega |
| [02_descripcion_general.md](02_descripcion_general.md) | Tabla "Qué cambia respecto del TP", stack y versiones, arquitectura general, integraciones |
| [03_actores_y_roles.md](03_actores_y_roles.md) | ADMIN / VENDEDOR / CLIENTE / SISTEMA, roles vigentes, matriz RBAC, rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Tablas nuevas y cambios (`usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad`, `movimiento_stock`, `cliente`, `libro`), índices únicos parciales, migraciones 3 y 4, seed |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | **RN-01..RN-16 del parcial** (reemplazan a las del TP) y reglas derivadas |
| [06_funcionalidades.md](06_funcionalidades.md) | **E1..E10** (Ejercicios 1..10) con puntaje y requisitos; historias de usuario |
| [07_flujos_principales.md](07_flujos_principales.md) | Registro, login, autorización, roles, cambio de contraseña, venta, libros, detalle de venta, despliegue |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura obligatoria (`app/core/*`, `app/modules/<módulo>/*`), restricción de `test/`, seguridad, variables |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | DD-01..DD-32 y SU-01..SU-08 |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Inconsistencias IN-01..IN-08 y preguntas P-01..P-18 (abiertas hoy: red de EasyPanel, nombre del grupo y fecha) |
| [11_endpoints_y_casos_de_prueba.md](11_endpoints_y_casos_de_prueba.md) | Endpoints abiertos/protegidos, cuerpos de ejemplo, casos **C-01..C-16** y **D-01..D-08** |
| [12_criterios_de_evaluacion.md](12_criterios_de_evaluacion.md) | Pesos (suman 100 %), condiciones eliminatorias, formato de entrega, checklist |
| [13_despliegue.md](13_despliegue.md) | Dockerfile, `docker run`, VPS/EasyPanel (`calculadora_db`, base `libreria`), `DEPLOY.md`, evidencia |

> **Material de cátedra:** `docs/catedra/` (cap1 a cap6, Markdown). Regla: buscar la sección puntual con Grep del encabezado, **nunca leer el archivo entero**.

## Quick Start

1. Entender el delta → [02](02_descripcion_general.md), [01](01_vision_y_objetivos.md)
2. Datos → [04](04_modelo_de_datos.md); reglas → [05](05_reglas_de_negocio.md)
3. Arquitectura y estructura obligatoria → [08](08_arquitectura_propuesta.md)
4. Qué hacer y cómo se corrige → [06](06_funcionalidades.md), [12](12_criterios_de_evaluacion.md)
5. Casos de prueba → [11](11_endpoints_y_casos_de_prueba.md)
6. Despliegue → [13](13_despliegue.md)
7. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo

Grupo: Pagano Amanda, Liendo Mateo, Avila Lucas, Valentini Tiziano, García Juan. El trabajo de caps. 5 y 6 va **sólo en `parcial/`**; `despliegue/` es el mismo TP caps. 1–4 con Dockerfile, `env.example`, `DEPLOY.md` y `evidencia/`. Las RN-01..RN-16 del parcial reemplazan a las del TP. `test/` lleva **sólo** `.http` y un `solo_agregado.sql` (sin pytest, por instrucción del profesor). Nunca se escribe la contraseña de la base en un archivo: entra por `--env-file` en el servidor.
