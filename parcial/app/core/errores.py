"""Traducción de IntegrityError a 409 con mensaje propio (RN-15).

Convención para todos los módulos (D9, consigna pág. 9):
- El servicio recibe el UnitOfWork, lo abre con `async with uow:` y deja
  propagar el IntegrityError, para que el UnitOfWork haga rollback.
- El router lo atrapa y lo traduce:
      except IntegrityError as exc:
          raise traducir_integrity_error(exc) from None

Nunca se devuelve str(exc) ni str(exc.orig): tienen texto interno de la base.
Cada change agrega acá los mensajes de sus restricciones nuevas.
"""
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

MENSAJE_POR_DEFECTO = "Los datos enviados entran en conflicto con el estado actual"

MENSAJES_CONSTRAINT: dict[str, str] = {
    "uq_usuario_email": "Ya existe un usuario con ese email",
    "uq_cliente_email": "Ya existe un cliente con ese email",
    "uq_cliente_usuario_id": "Ese usuario ya está vinculado a otro cliente",
    "ix_perfil_cliente_cliente_id": "El cliente ya tiene un perfil registrado",
    "uq_editorial_nombre": "Ya existe una editorial con ese nombre",
    "uq_genero_nombre": "Ya existe un género con ese nombre",
    "uq_libro_isbn_vigente": "Ya existe un libro activo con ese ISBN",
    "uq_asignacion_rol_abierta": "El usuario ya tiene ese rol activo asignado",
    "ck_libro_precio_positivo": "El precio del libro debe ser mayor a cero",
    "ck_libro_stock_no_negativo": "El stock del libro no puede quedar negativo",
    "ck_movimiento_stock_cantidad_no_cero": "La cantidad del movimiento de stock no puede ser cero",
    "ck_asignacion_rol_rol_valido": "El rol indicado no es válido",
    "ck_libro_autor_orden_minimo": "El orden del autor debe ser al menos 1",
    "ck_libro_autor_rol_valido": "El rol del autor en el libro no es válido",
    "ck_venta_total_no_negativo": "El total de la venta no puede ser negativo",
    "ck_renglon_cantidad_positiva": "La cantidad del renglón debe ser mayor a cero",
    "ck_renglon_precio_unitario_positivo": "El precio unitario del renglón debe ser mayor a cero",
}


def _nombre_constraint(exc: IntegrityError) -> str | None:
    orig = exc.orig
    # SQLAlchemy envuelve el error de asyncpg, que queda en __cause__ con el
    # nombre exacto. Se usa primero porque el texto incluye datos del usuario.
    nombre = getattr(getattr(orig, "__cause__", None), "constraint_name", None)
    if nombre:
        return nombre
    texto = str(orig)
    return next((clave for clave in MENSAJES_CONSTRAINT if clave in texto), None)


def traducir_integrity_error(
    exc: IntegrityError, default: str = MENSAJE_POR_DEFECTO
) -> HTTPException:
    """Devuelve la excepción (no la lanza): quien llama hace `raise ... from None`."""
    mensaje = MENSAJES_CONSTRAINT.get(_nombre_constraint(exc), default)
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)
