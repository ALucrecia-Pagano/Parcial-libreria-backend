# Tasks — CH-13 clientes con repositorio y Unit of Work

## 1. Contratos y prueba

- [x] 1.1 Reescribir `schemas.py` con `extra="forbid"`, `usuario_id` solo en la salida y PATCH que rechaza nulos y cuerpo vacío; verificar que un cuerpo con `usuario_id` no valida.
- [x] 1.2 Escribir `parcial/test/CH-13_clientes.http` con los pedidos de la ficha (201, 409, 422, 404, 401 y 403) y la respuesta esperada en comentarios.

## 2. Capas

- [x] 2.1 Crear `repository.py` (`ClienteRepository` con `get_by_email`, `get_by_usuario_id` y lectura con perfil; `PerfilClienteRepository`) y `unit_of_work.py`; verificar que ningún método hace `commit()`.
- [x] 2.2 Reescribir `service.py` para recibir el Unit of Work y abrirlo con `async with`, con 404 propio y sin `commit()`.
- [x] 2.3 Reescribir `router.py` como `router_staff` que traduzca `IntegrityError` a 409. `GET /clientes/{id}/ventas` queda en el módulo ventas (CH-14), también con guarda de staff, para que C-06 siga en 403.

## 3. Verificación

- [x] 3.1 Confirmar que `main.py` monta `router_staff` con `requiere_rol("VENDEDOR", "ADMIN")` y que el arranque importa el módulo.
- [x] 3.2 Correr `python seed.py` y `CH-13_clientes.http` contra PostgreSQL y dejar la evidencia en `verify.md`.

## Workflow follow-up

- Archivar el change y marcar el Estado de CH-13 en `CHANGES.md` después de la verificación.
