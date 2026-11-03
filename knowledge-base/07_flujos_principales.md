# Flujos Principales

Flujos derivados del enunciado (no hay diagramas de secuencia en la consigna). Capas: Router → Service → UoW → Repository → Model.

## Flujo 1: Registro (RN-02, RN-01, RN-16)

**Disparador**: `POST /auth/registro` (anónimo). **Actor**: visitante.

1. Router: valida el contrato (`extra="forbid"`; contraseña ≤ 72 bytes → si no 422). No acepta rol.
2. Service: **calcula el hash bcrypt fuera del bucle (`to_thread` + semáforo) ANTES de abrir la transacción**.
3. Service: `async with uow:` — un solo bloque: crea `usuario`, `asignacion_rol` (CLIENTE) y `cliente` con `usuario_id`.
4. La unicidad la da la base (`usuario.email`, `cliente.email`): `IntegrityError` → se traduce a **409** con mensaje propio; el UoW revierte y **no queda ninguna fila suelta** (C-02).
5. Si ya existía un cliente con ese correo → 409; **no se apropia de esa ficha**.

**Errores**: correo repetido de usuario o de cliente → 409; cuerpo inválido → 422.

## Flujo 2: Login (RN-07, RN-08, E7)

**Disparador**: `POST /auth/login`. **Actor**: cualquiera.

1. Service: cuenta fallos recientes en `intento_acceso` (mismo `email` + `ip`, últimos 60 s, **sólo desde el último login correcto**). Si ≥ 5 → **429 + `Retry-After`**, sin calcular ningún hash.
2. Busca el usuario por correo. Verifica la contraseña con bcrypt (fuera del bucle) contra el hash del usuario **o contra el hash ficticio** si no existe → mismo mensaje y tiempo parecido: **401** igual en ambos casos (C-04).
3. Registra el intento (éxito o fallo) en `intento_acceso` desde **sesión y transacción propias**, que se confirman siempre (aunque la petición termine en error).
4. Si correcto: emite JWT (`sub`, `exp`, roles vigentes al emitirlo) y lo pone en cookie `access_token` (HttpOnly, SameSite=Lax, Max-Age, Secure configurable). Cuerpo: `{ "mensaje": "Sesión iniciada", "debe_cambiar_password": false, "expira_en_segundos": 1800 }` (ejemplo del PDF).

## Flujo 3: Petición autenticada y autorización (RN-04, E5)

1. `get_usuario_actual` (misma sesión que el UoW): lee `request.cookies["access_token"]`, valida firma/`exp`; usuario inexistente o inactivo → **401**.
2. Grupo protegido: control de cambio obligatorio (RN-06) montado una sola vez → **403** si `debe_cambiar_password`.
3. `requiere_rol(...)`: consulta los **roles vigentes** en `asignacion_rol` (no revocada, no vencida) → si no alcanza, **403**.
4. Revocar un rol → la misma cookie obtiene 403 en la petición siguiente; `/auth/yo` muestra roles vigentes vs. los del token (C-07).

## Flujo 4: Asignar / revocar rol (RN-03, RN-05, RN-16)

**Disparador**: `POST /usuarios/{id}/roles`, `DELETE /usuarios/{id}/roles/{rol}` (ADMIN).

- Asignar: vencimiento con zona horaria y futuro (si no, 422). Si hay asignación abierta del mismo rol → 409 (índice parcial). Si la abierta está vencida → cierra la anterior y abre una nueva. Escribe `evento_seguridad` en la **misma transacción**.
- Revocar: pone `revocada_en`, no borra. Si es el propio ADMIN o el último administrador vigente → **409** (RN-05). Escribe evento en la misma transacción.

## Flujo 5: Cambio obligatorio de contraseña (RN-06, RN-16)

1. Usuario con `debe_cambiar_password = true` inicia sesión (permitido: `/auth`).
2. Cualquier ruta del grupo protegido → 403.
3. `POST /auth/cambiar-password` (actual ≤ 72 bytes, nueva ≤ 72 bytes): hash fuera de la transacción; en el UoW actualiza `password_hash`, `debe_cambiar_password = false` y escribe `evento_seguridad`.
4. La **misma cookie** sirve después para las rutas protegidas (200). No se emite token nuevo ni se invalidan otras sesiones.

## Flujo 6: Registrar una venta (RN-09, RN-10, RN-11, E8)

**Disparador**: `POST /ventas` (VENDEDOR/ADMIN). Cuerpo: `{ "cliente_id", "renglones": [{ "libro_id", "cantidad" }] }` (sin precio, total ni fecha).

1. Contrato: ≥ 1 renglón, sin libros repetidos, cantidades válidas (422 si no).
2. Service: `async with uow:` (un solo bloque): verifica cliente y libros (inexistente o dado de baja → **409**, C-12); crea `venta` con total calculado por el servidor; por cada renglón: copia el precio del libro, crea `renglon_venta`, **descuenta stock y escribe `movimiento_stock` (negativo) a través del punto único de escritura de stock**; si algún libro no alcanza → excepción → **rollback total** (409; ni venta, ni renglones, ni descuentos, ni movimientos; C-11).
3. Al confirmarse: se agenda con `BackgroundTasks` el aviso del comprobante (`await asyncio.sleep(0.5)` + log). Corre **después de la respuesta** y sólo si hubo commit.
4. Invariante tras cada caso: `libro.stock == SUM(movimiento_stock.cantidad)` en los 5 libros.

## Flujo 7: Alta, reposición y baja de libro (RN-11, RN-13, RN-01)

- **Alta** `POST /libros` (con `autores` y `stock_inicial`): crea el libro con stock 0 y deja el movimiento "Stock inicial" **por el punto único de escritura** (el libro no se crea con `stock` directo); ISBN duplicado entre vigentes → 409.
- **Reposición** `POST /libros/{id}/reponer`: 200 con su movimiento; libro dado de baja → 409/404 (ver `10`).
- **Baja** `DELETE /libros/{id}`: 204, setea `borrado_en`; deja de aparecer en el catálogo; las ventas viejas lo siguen mostrando (carga anticipada que incluye borrados). Recargar el mismo ISBN → 201; un segundo vigente con ese ISBN → 409 (C-13).
- `PATCH /libros/{id}`: sólo título y precio; con `stock` → 422.

## Flujo 8: Detalle de venta (RN-14, C-08, C-15)

`GET /ventas/{id}` (sin `requiere_rol`): el servicio determina quién es el solicitante: si es personal (VENDEDOR/ADMIN vigente) o el cliente dueño → devuelve el detalle (cliente, renglones, libro de cada renglón, incluso de baja) con **consultas fijas** (carga anticipada en el repositorio); si no → **403**. Venta inexistente → 404.

## Flujo 9: Despliegue (E9/E10; ver `13`)

`docker build` → `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria` → el contenedor corre `alembic upgrade head` y levanta uvicorn en `0.0.0.0:8000`; luego `docker exec libreria ...` con el comando de datos iniciales del README del TP. Actualización: rebuild, `docker rm -f libreria`, volver a correr (los datos viven en la base).
