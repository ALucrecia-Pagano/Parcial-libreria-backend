# Proposal — CH-13 `clientes-repo-uow-usuario-id`

> **Governance: MEDIO.** Dueño: Juan García (Parte 5). Depende de CH-01, CH-02 y CH-10, ya en `main`.

## Why

El módulo `clientes` sigue en la forma del TP: el servicio recibe la sesión, hace `commit()` y los contratos de entrada aceptan campos de más. La consigna (ejercicios 3 y 6) pide repositorio + Unit of Work, `usuario_id` visible y no editable, y unicidad del correo garantizada por la base.

## What Changes

- `ClienteRepository` (con `get_by_email` y `get_by_usuario_id`, precarga del perfil adentro) y `PerfilClienteRepository`, más `ClientesUnitOfWork`.
- El servicio recibe el Unit of Work y lo abre con `async with`; deja de confirmar.
- Contratos con `extra="forbid"`. La salida incluye `usuario_id` (nulo si no hay acceso web). `POST` y `PATCH` no aceptan `usuario_id`.
- Endpoints de staff (VENDEDOR o ADMIN, la guarda ya la monta `main.py`): `POST /clientes` → 201, 409, 422; `GET /clientes/{id}` → 200, 404; `PATCH /clientes/{id}` → 200, 404, 409, 422; `POST /clientes/{id}/perfil` → 201, 404, 409.
- Colisión de `uq_cliente_email` y de perfil duplicado: 409 con mensaje propio, sin consulta previa. Los mensajes ya están en `errores.py`.
- **BREAKING**: desaparece el listado `GET /clientes` (limit/offset). No está en la consigna del parcial.
- `GET /clientes/{id}/ventas` no entra en este change. Lo expone el módulo ventas en CH-14, con la guarda de staff.

## Capabilities

### New Capabilities

- `clientes`: ficha de cliente vinculable a un usuario, perfil uno a uno, y escritura de personal con repositorio + Unit of Work.

### Modified Capabilities

- *(Ninguna. El esquema de `usuario_id` ya está en `esquema-de-datos`; las clases base no cambian.)*

## Impact

- **Crear**: `parcial/app/modules/clientes/repository.py`, `parcial/app/modules/clientes/unit_of_work.py`, `parcial/test/CH-13_clientes.http`.
- **Modificar**: `parcial/app/modules/clientes/{service,router,schemas}.py`, `parcial/app/main.py` (montar `router_staff`).
- **No entra**: `GET /clientes/{id}/ventas` como capacidad de ventas (CH-14), alta de usuario para el cliente, migraciones, `models.py`, `despliegue/`.
- **Reglas**: RN-01 (correo de cliente), RN-11 (`extra="forbid"`), RN-15, soporte de RN-14 (`cliente.usuario_id` identifica al dueño).
