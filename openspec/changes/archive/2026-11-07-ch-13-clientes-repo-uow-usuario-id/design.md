# Design — CH-13 `clientes-repo-uow-usuario-id`

## Context

Ver `proposal.md` (por qué) y `specs/clientes/spec.md` (qué). El módulo `clientes` todavía recibe `AsyncSession`, hace `commit()` en `_guardar` y no declara `extra="forbid"`. `main.py` ya monta `router_staff` con `requiere_rol("VENDEDOR", "ADMIN")` si el atributo existe. `uq_cliente_email` e `ix_perfil_cliente_cliente_id` ya tienen mensaje en `errores.py`.

## Goals / Non-Goals

**Goals:**

- Misma forma que editoriales: el router construye el Unit of Work, el servicio lo abre, el repositorio solo hace `flush()`.
- Precarga del perfil dentro de los métodos de lectura del repositorio de clientes.
- `usuario_id` sale en la respuesta y no entra en los contratos.

**Non-Goals:**

- Mover `GET /clientes/{id}/ventas` al módulo ventas (CH-14).
- Crear un usuario al dar de alta un cliente de mostrador.

## Decisions

### D1. Dos repositorios en un solo Unit of Work

`ClienteRepository` hereda de `BaseRepository[Cliente]` y agrega `get_by_email`, `get_by_usuario_id` y `get_con_perfil`. Esos tres declaran `joinedload(Cliente.perfil)` adentro. `PerfilClienteRepository` hereda de la base y no agrega métodos: el alta de perfil usa `add()`. Alternativa descartada: un solo repositorio que escriba las dos tablas. El perfil es otra entidad y CH-15 va a precargar desde el repositorio de clientes.

### D2. 404 en el servicio, 409 en el router

Igual que editoriales. No se busca el correo antes del `INSERT`: el `IntegrityError` sale del `async with`, el Unit of Work revierte y el router llama a `traducir_integrity_error`.

### D3. `usuario_id` no es un campo del contrato de entrada

`ClienteCreate` y `ClienteUpdate` no lo declaran. Con `extra="forbid"`, enviarlo es 422. El alta deja el nulo del modelo. El vínculo lo crea el auto-registro (CH-08), no el personal.

### D4. El listado general se quita

La consigna no lista `GET /clientes`. El router nuevo no lo expone. `GET /clientes/{id}/ventas` no se reimplementa acá: lo toma el módulo ventas en CH-14, montado con la misma guarda de staff, así C-06 sigue respondiendo 403 a un CLIENTE.

### D5. `main.py` no se reestructura

El branch `hasattr(clientes_module, "router_staff")` de CH-10 ya monta el router. Este change solo deja de exportar el `router` plano del TP.

## Risks / Trade-offs

- [Un 409 consume un id de la secuencia] → los `.http` no fijan el id del alta que viene después de un conflicto.
- [C-07 hace `POST /clientes` y espera 201] → el cuerpo `{nombre, email}` sigue siendo válido.
- [Lecturas dentro de `async with` confirman sin cambios] → mismo criterio que CH-04.
