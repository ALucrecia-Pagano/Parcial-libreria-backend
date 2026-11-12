"""Errores del dominio, manejador global HTTP y traducción de IntegrityError (RN-15).

- Jerarquía `ErrorDominio(Exception)`: las reglas de negocio en los servicios
  lanzan estas excepciones sin acoplarse a FastAPI ni a HTTPException.
- Manejador global `manejar_error_dominio`: registrado en `app/main.py` con
  `app.add_exception_handler(ErrorDominio, manejar_error_dominio)`.
- `traducir_integrity_error`: lo llaman los routers al atrapar `IntegrityError`
  de SQLAlchemy (que sale del `UnitOfWork` tras hacer rollback) para responder
  409 con mensaje propio, sin exponer texto interno de la base.
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class ErrorDominio(Exception):
    """Error base de dominio lanzado por los servicios."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorDominio):
    """Recurso inexistente o dado de baja (404)."""


class Conflicto(ErrorDominio):
    """Operación incompatible con las reglas o el estado actual (409)."""


class NoAutenticado(ErrorDominio):
    """Credenciales inválidas o sesión inexistente/inactiva (401)."""


class Prohibido(ErrorDominio):
    """El usuario autenticado carece de permisos para la operación (403)."""


class DemasiadosIntentos(ErrorDominio):
    """Límite de intentos excedido; informa segundos de espera (429)."""

    def __init__(self, mensaje: str, retry_after: int) -> None:
        super().__init__(mensaje)
        self.retry_after = retry_after


_CODIGOS_ERROR_DOMINIO: dict[type[ErrorDominio], int] = {
    NoEncontrado: status.HTTP_404_NOT_FOUND,
    Conflicto: status.HTTP_409_CONFLICT,
    NoAutenticado: status.HTTP_401_UNAUTHORIZED,
    Prohibido: status.HTTP_403_FORBIDDEN,
    DemasiadosIntentos: status.HTTP_429_TOO_MANY_REQUESTS,
}


async def manejar_error_dominio(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Manejador global único: traduce ErrorDominio a JSONResponse {"detail": mensaje}."""
    if not isinstance(exc, ErrorDominio):
        raise exc
    status_code = _CODIGOS_ERROR_DOMINIO.get(type(exc))
    if status_code is None:
        status_code = next(
            (
                codigo
                for cls, codigo in _CODIGOS_ERROR_DOMINIO.items()
                if isinstance(exc, cls)
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    headers: dict[str, str] | None = None
    if isinstance(exc, DemasiadosIntentos):
        headers = {"Retry-After": str(exc.retry_after)}
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.mensaje},
        headers=headers,
    )

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
