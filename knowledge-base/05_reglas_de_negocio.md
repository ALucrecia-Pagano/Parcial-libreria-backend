# Reglas de Negocio

> **IMPORTANTE — numeración.** Las reglas **RN-01 a RN-16** de este archivo son las **del PARCIAL** (tabla de la pág. 7–8 de la consigna). "Se numeran de nuevo y **reemplazan a las del TP** en lo que se superponen." **No mezclar** con la numeración RN del TP de los capítulos 1–4 (`parcial/TP_Cap1a4_Consigna.pdf`, `parcial/README.md`). Siguen vigentes, aunque no se repitan, los **CHECK de precio y stock** del libro y la **búsqueda por título con parámetros ligados** del TP.
>
> Los códigos se escriben tal cual los usa el PDF y el material de la cátedra: **RN-01 ... RN-16** (en el PDF aparecen sin guion en la tabla, "RN01", por el maquetado). No se usa el esquema `RN-DOMINIO-NN`; los dominios se indican en la columna Dominio.

## Tabla completa

| Código | Dominio | Enunciado | Garante esperado |
|---|---|---|---|
| **RN-01** | Unicidad | El correo de un usuario, el de un cliente, el nombre de una editorial y el de un género son únicos. El ISBN de un libro es único entre los que no están dados de baja. | UNIQUE e índice único parcial en la base; **409** con mensaje propio |
| **RN-02** | Registro | El auto-registro crea el usuario, su rol CLIENTE y su ficha de cliente: o quedan las tres filas, o ninguna. Si ya existe un cliente con ese correo, el registro da 409 y no se apropia de esa ficha. | Un solo Unit of Work |
| **RN-03** | Roles | Un usuario tiene a lo sumo una asignación abierta por rol. | Índice único parcial; **409** |
| **RN-04** | Autorización | Los permisos se deciden con los roles vigentes en la base, en cada petición. Los roles que trae el token son informativos. | Dependencia que consulta `asignacion_rol` |
| **RN-05** | Autoprotección | Un administrador no puede revocarse su propio rol ADMIN, y el sistema nunca queda sin administradores vigentes. | Comprobación en el servicio; **409** |
| **RN-06** | Cambio de contraseña | Mientras un usuario tenga el cambio de contraseña pendiente, sólo puede usar las rutas de `/auth` y las que no piden sesión. | Dos grupos de rutas; **403** |
| **RN-07** | Límite de intentos | Después de 5 intentos fallidos con el mismo correo desde la misma dirección en 60 segundos, el login responde 429 sin verificar la contraseña. Un login correcto reinicia la cuenta: los fallos anteriores siguen en la tabla, pero dejan de contar. | Conteo sobre `intento_acceso`; `Retry-After` |
| **RN-08** | Anti-enumeración | El login responde lo mismo, y tarda lo mismo, exista o no el correo. | Mismo mensaje; verificación contra un hash ficticio |
| **RN-09** | Venta | Una venta nace con sus renglones (al menos uno, sin libros repetidos), con el precio de cada renglón copiado del libro y el total calculado por el servidor. Las ventas no se modifican. | DTO; el precio y el total nunca viajan en el cuerpo; no hay PATCH |
| **RN-10** | Venta/stock | Registrar una venta descuenta el stock de cada libro y deja un movimiento por renglón. Si un libro no alcanza, no queda ninguna de esas escrituras: ni la venta, ni los renglones, ni los descuentos, ni los movimientos. | Un solo Unit of Work; **409** |
| **RN-11** | Stock | El stock de un libro sólo cambia a través de movimientos: el alta con stock inicial, la reposición y la venta. No se edita por PATCH. | Punto único de escritura de stock |
| **RN-12** | Sólo agregado | `movimiento_stock` es de sólo agregado: nadie puede modificar ni borrar sus filas. | Disparador en la base, instalado por migración |
| **RN-13** | Baja de libro | Un libro dado de baja deja de aparecer en el catálogo y no se puede vender ni reponer, pero sus datos se conservan y las ventas anteriores lo siguen mostrando. | Borrado lógico; **409** |
| **RN-14** | Lo propio | Lo propio sólo pide estar autenticado: un cliente ve sus ventas y ninguna otra. | `/mis-ventas` y comprobación de dueño; **403** |
| **RN-15** | Errores | Ningún error devuelve al cliente texto interno de la base (que entregaría el mapa del esquema). Ninguna entrada inválida termina en un 500. | Traducción del `IntegrityError`; validación en el contrato |
| **RN-16** | Auditoría | Cada alta de personal, cambio de rol y cambio de contraseña deja una línea en `evento_seguridad`, en la misma transacción que el cambio. | Un solo Unit of Work |

## Referencias cruzadas con los ejercicios

- RN-02, RN-10 y RN-16 → "se escriben cada una en **un solo bloque**" `async with uow:` (Ej. 6).
- RN-11 → `extra="forbid"` en los contratos de entrada (nadie se registra con un rol ni edita el stock por PATCH → PATCH con `stock` da 422) (Ej. 3) y **un único punto de escritura del stock** usado por alta de libro, reposición y venta (Ej. 6).
- RN-12 → migración 4 escrita a mano (Ej. 2/7).
- RN-07/RN-08 → orden del login (Ej. 4): primero el límite de intentos (una consulta; si se superó, 429 + `Retry-After` **sin calcular hash**), después la verificación contra el hash del usuario o contra el **hash ficticio** (calculado una vez en el lifespan).
- RN-04/RN-05/RN-06/RN-14 → Ej. 5.
- RN-01/RN-03 → "unicidad garantizada por la base; **no se verifica con una consulta previa**" (requisito no funcional): se atrapa el `IntegrityError` y se traduce a 409 con mensaje propio (RN-15).
- Excepción a "todo en la transacción de la petición": la escritura de `intento_acceso` usa sesión y transacción propias y se confirma siempre (ver `09`, DD-06).

## Reglas derivadas de enunciados de los ejercicios (no tienen código RN)

- Los campos que terminan en bcrypt (contraseña del registro, del login, la actual y la nueva del cambio) aceptan **como máximo 72 bytes** (bytes, no caracteres: una "ñ" ocupa dos); si no, **422** y no 500.
- Vencimiento de un rol: con zona horaria y en el futuro; si no, **422** (no 409).
- Reasignar un rol vencido: cierra la fila anterior y abre una nueva.
- Cambiar la contraseña **no** invalida las sesiones abiertas ni emite un token nuevo.
- Paginación: `page` desde 1, `size` 1..100 (default 20); página más allá de la última → **422** ("La página 4 no existe: hay 3"); con cero resultados hay **una página, vacía**; `total` cuenta con los **mismos filtros** que la página.
- Códigos: 201 al crear, 204 al dar de baja un libro, 404 si el recurso *de la ruta* no existe, 409 si choca con lo guardado, 422 si cuerpo/parámetros no cumplen el contrato. Un cliente o libro *del cuerpo* de una venta que no existe → **409** (C-12), no 404.
- `exclude_unset` en los PATCH (sólo se aplican los campos enviados).
- Ninguna respuesta incluye `password_hash`.
- Cookie: `access_token`, `HttpOnly`, `SameSite=Lax`, `Max-Age` = duración del token, `Secure` configurable; el cuerpo del login no trae el token; **no** se lee de `Authorization: Bearer`.
- Aviso del comprobante (`BackgroundTasks`): corre después de enviar la respuesta y **sólo si la operación se confirmó**; debe verse en consola con el arranque normal de uvicorn (hay que configurar el logger).
