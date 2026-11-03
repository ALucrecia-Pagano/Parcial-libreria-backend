# Modelo de Datos

> Los **nombres de tablas y columnas son obligatorios** (los casos de prueba y la corrección los usan). Se pueden **agregar** columnas, pero **no quitar ni renombrar** las indicadas. Las tablas `editorial`, `genero`, `autor`, `libro_autor` y `perfil_cliente` **no cambian** respecto del TP. Todas las fechas nuevas son `timestamptz`. El dinero sigue siendo `NUMERIC` / `Decimal`, nunca `float`. **Cada FK nueva lleva un índice** (PostgreSQL no lo crea solo). La navegación se declara en los **dos extremos**, como en el TP. El esquema se crea **sólo con Alembic** (nada de `create_all`).

## Dominios

- **Acceso**: `usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad` (módulo `usuarios`).
- **Catálogo**: `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `movimiento_stock` (`MovimientoStock` vive en módulo `libros`; `LibroAutor` también).
- **Clientes**: `cliente`, `perfil_cliente` (módulo `clientes`).
- **Ventas**: `venta`, `renglon_venta` (módulo `ventas`).

## ERD (Figura 1 de la consigna, descrita en texto)

La figura (pág. 5, imagen) marca: en verde las clases nuevas, en ámbar las que cambian (`Libro` incorpora borrado lógico; `Cliente`, el acceso opcional), en gris las que no cambian; rombo lleno = composición, rombo vacío = agregación, flecha = asociación; «appendOnly» marca la tabla protegida por el disparador. **`IntentoAcceso` y `EventoSeguridad` no se relacionan con ninguna otra tabla** (`evento_seguridad.actor` es texto; `intento_acceso.email` es texto, sin FK).

```
usuario 1 ──< asignacion_rol          (usuario_id; otorgada_por -> usuario, nulo)
usuario 1 ──0..1 cliente              (cliente.usuario_id UNIQUE, nulo)
cliente 1 ──0..1 perfil_cliente       (TP)
cliente 1 ──< venta 1 ──< renglon_venta >── 1 libro      (TP)
editorial 1 ──< libro >── 1 genero    (TP)
libro >──< autor  vía libro_autor (rol, orden)           (TP)
libro 1 ──< movimiento_stock >── 0..1 venta              (nuevo; movimiento.usuario_id -> usuario)
intento_acceso, evento_seguridad: aisladas (sin FKs)
```

**Resuelto (P-07):** `otorgada_por` es FK nullable a `usuario.id` (con índice); en el seed es NULL (actor SISTEMA). `renglon_venta`/`venta` conservan sus nombres del TP.

## Tablas nuevas

### `usuario`
| Columna | Notas |
|---|---|
| `id` | PK |
| `email` | **UNIQUE** |
| `nombre` | |
| `password_hash` | bcrypt. **Nunca** sale en una respuesta |
| `activo` | usuario inactivo → 401 en `get_usuario_actual` |
| `debe_cambiar_password` | activa el control RN-06 |

No tiene columna `rol`.

### `asignacion_rol`
| Columna | Notas |
|---|---|
| `id` | PK |
| `usuario_id` | FK a `usuario` (+ índice) |
| `rol` | **CHECK** `rol IN ('ADMIN','VENDEDOR','CLIENTE')` |
| `desde` | timestamptz |
| `vence_en` | timestamptz, **nulo** (sin vencimiento) |
| `revocada_en` | timestamptz, **nulo** |
| `otorgada_por` | FK nullable a `usuario.id` (+ índice). NULL en el seed (actor SISTEMA) |

Restricción clave: **índice único parcial** `(usuario_id, rol) WHERE revocada_en IS NULL` (`postgresql_where`) → a lo sumo una asignación *abierta* por rol (RN-03). "Abierta" = no revocada (aunque haya vencido); por eso reasignar un rol vencido obliga a **cerrar primero la fila anterior** (poner `revocada_en`) y abrir una nueva.

### `intento_acceso`
| Columna | Notas |
|---|---|
| `id` | PK |
| `cuando` | timestamptz |
| `email` | texto, no FK (sobrevive aunque el correo no exista) |
| `ip` | dirección del cliente |
| `exito` | bool |

Restricción: **índice** `(email, ip, cuando)` (sirve al conteo de RN-07). Se escribe desde **sesión y transacción propias**, que se confirman siempre (ver `07` y `09`).

### `evento_seguridad`
| Columna | Notas |
|---|---|
| `id` | PK |
| `cuando` | timestamptz |
| `actor` | **texto** (no FK; permite el valor `SISTEMA`) |
| `accion` | texto (alta de personal, cambio de rol, cambio de contraseña, carga de datos iniciales, ...) |

Sin restricciones extra. Se escribe **en la misma transacción** que el cambio auditado (RN-16).

### `movimiento_stock`
| Columna | Notas |
|---|---|
| `id` | PK |
| `libro_id` | FK a `libro` (+ índice) |
| `venta_id` | FK a `venta`, **nulo** (nulo en alta y reposición) (+ índice) |
| `usuario_id` | FK a `usuario` (+ índice), **NOT NULL** (P-01). Los "Stock inicial" del seed los hace `admin@example.com` |
| `cantidad` | entero con signo (+ ingreso, - salida) |
| `motivo` | texto libre: "Stock inicial", "Reposición", "Venta". Sin CHECK (P-02) |
| `cuando` | timestamptz |

Restricciones: **CHECK `cantidad <> 0`**; **sólo agregado** (disparador instalado por la migración 4 a mano; RN-12). Invariante: para cada libro, **`libro.stock = SUM(movimiento_stock.cantidad)`** (se verifica tras cada caso de venta; se rompe si alguna parte escribe el stock sin dejar movimiento).

## Tablas que cambian

### `cliente`
- **Se agrega `usuario_id`** (nulo permitido) con **UNIQUE**: un cliente puede tener o no acceso web. `email` **sigue UNIQUE**.
- Relación `Cliente.usuario` devuelve **un objeto** (no una lista; uselist=False / relación 1 a 0..1), declarada en ambos extremos.

### `libro`
- **Se agrega `borrado_en`** (`timestamptz`, nulo): borrado lógico.
- El `UNIQUE` de `isbn` se **reemplaza** por un **índice único parcial** `(isbn) WHERE borrado_en IS NULL` (`postgresql_where`). Razón: con UNIQUE común no se podría recargar un ISBN dado de baja y la base respondería "ya existe" de un libro que la app no muestra.
- Siguen los CHECK `precio > 0` y `stock >= 0`.
- `libro.stock` es el resultado de sumar los movimientos; **no se edita por PATCH**.

## Los dos índices únicos parciales (resumen para la corrección)

| Tabla | Columnas | Predicado (`postgresql_where`) | Garantiza |
|---|---|---|---|
| `asignacion_rol` | `(usuario_id, rol)` | `revocada_en IS NULL` | RN-03 |
| `libro` | `(isbn)` | `borrado_en IS NULL` | RN-01 (ISBN único entre vigentes) |

## Migraciones

| # | Origen | Contenido |
|---|---|---|
| 1, 2 | TP (ya hechas) | Esquema del TP; `genero` + `libro.genero_id` |
| 3 | **`alembic revision --autogenerate`** | Tablas de acceso (`usuario`, `asignacion_rol`, `intento_acceso`, `evento_seguridad`), `movimiento_stock`, cambios de `cliente` y `libro` |
| 4 | **Escrita a mano** | Función + disparador de sólo agregado sobre `movimiento_stock` (RN-12): la comparación automática no ve funciones ni disparadores |

Cada migración nueva **se lee antes de aplicarla y lleva un comentario que lo diga**; si lo autogenerado tiene un problema, se corrige a mano y el comentario lo explica. Deben funcionar `alembic upgrade head` sobre base vacía, `alembic downgrade base` y otra vez `upgrade head` (la `downgrade` de la 4 debe quitar disparador y función; la de la 3 debe poder revertir el índice parcial del ISBN).

**Suposición:** al reemplazar el UNIQUE de `libro.isbn`, el autogenerate no sabe el nombre del constraint viejo ni detecta bien el cambio a índice parcial; es muy probable que haya que corregir a mano la 3 (y comentarlo). Ver `09`.

## Seed data inicial (`seed.py` en la raíz de `parcial/`)

`seed.py` **vacía las tablas con `TRUNCATE ... RESTART IDENTITY CASCADE`** (un `DELETE` lo frenaría el disparador, y `RESTART IDENTITY` hace que los ids vuelvan a 1: los casos C usan ids fijos como libro 1 o venta 1) y carga como mínimo lo siguiente (los casos de prueba lo usan; es parte de la puesta en marcha, no un extra). Las contraseñas son de mentira y viven sólo en ese archivo.

| Qué | Datos |
|---|---|
| Usuarios | `admin@example.com` y `admin2@example.com` (ADMIN), `vendedor@example.com` (VENDEDOR), `ana@example.com` (CLIENTE), `nuevo@example.com` (VENDEDOR, con `debe_cambiar_password = true`) |
| Editoriales (3, **ficticias**) | 1 Letras del Río, 2 Ediciones del Plata Sur, 3 Editorial Sudamérica Austral |
| Géneros (3) | 1 Novela, 2 Cuento, 3 Antología |
| Autores (6) | 1 Julio Cortázar, 2 Jorge Luis Borges, 3 Silvina Ocampo, 4 Adolfo Bioy Casares, 5 Ricardo Piglia, 6 Juan José Saer (sin libro en el seed) |
| Libros (5; ISBN **ficticios**) | 1 Rayuela, `978-950-00-0001-1`, 25000.00, stock 10, Cortázar, Letras del Río, Novela. 2 Antología de la literatura fantástica, `978-950-00-0002-8`, 30000.00, stock 5, Borges + Ocampo + Bioy Casares, Ediciones del Plata Sur, Antología. 3 Ficciones, `978-950-00-0003-5`, 22000.00, stock 8, Borges, Editorial Sudamérica Austral, Cuento. 4 Respiración artificial, `978-950-00-0004-2`, 27000.00, stock 3, Piglia, Ediciones del Plata Sur, Novela. 5 Bestiario, `978-950-00-0005-9`, **18000.00 (valor ficticio, DD-26)**, stock 1, Cortázar, Editorial Sudamérica Austral, Cuento |
| Clientes | Lucía Fernández (con perfil) y Tomás Ríos, **sin usuario**; Ana Paz, **con** el usuario `ana@example.com` |
| Venta | La 1, de Lucía, registrada por `vendedor@example.com`: 1 Rayuela y 2 Ficciones, total `69000.00` |
| Movimientos | Un "Stock inicial" por libro, hecho por `admin@example.com` (motivo "Venta" para los de la venta 1, hechos por el vendedor). Rayuela y Ficciones se cargan con **11 y 10** ejemplares; la venta 1 deja dos movimientos de salida (**-1 y -2**) → el stock coincide con la suma de movimientos en los 5 libros |
| Historial de seguridad | Una línea con actor `SISTEMA`: "Carga de los datos iniciales" |

Los nombres de editoriales, géneros y autores, los ISBN y el precio de Bestiario son **datos ficticios** inventados para el parcial (DD-26); los precios de los otros cuatro libros salen del TP. Derivado y confirmado: 69000 = 1 × 25000 (Rayuela) + 2 × 22000 (Ficciones) → Ficciones 22000.00. Atención: el seed *del TP* (`python -m scripts.seed`, venta total 71000.00, rechaza base con datos) **es otro** y no debe confundirse con el del parcial (ver IN-04 en `10`).
