"""Rutas de autenticación y usuarios (CH-07, CH-08, CH-09, CH-10 y CH-11)."""

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import SessionDep
from app.core.dependencies import UsuarioActualDep
from app.core.errores import traducir_integrity_error
from app.modules.usuarios.schemas import (
    CambiarPasswordIn,
    CambiarPasswordOut,
    LoginIn,
    LoginOut,
    LogoutOut,
    RegistroIn,
    RegistroOut,
    UsuarioYoOut,
)
from app.modules.usuarios.service import UsuariosService
from app.modules.usuarios.unit_of_work import UsuariosUnitOfWork

router_abierto = APIRouter(prefix="/auth", tags=["auth"])
service = UsuariosService()


@router_abierto.post(
    "/registro",
    response_model=RegistroOut,
    status_code=status.HTTP_201_CREATED,
)
async def registro(
    datos: RegistroIn,
    session: SessionDep,
) -> RegistroOut:
    """Registra atómicamente un nuevo cliente (usuario + rol CLIENTE + cliente)."""
    uow = UsuariosUnitOfWork(session)
    try:
        return await service.registrar_cliente(uow, datos)
    except IntegrityError as exc:
        raise traducir_integrity_error(exc) from None


@router_abierto.post(
    "/logout",
    response_model=LogoutOut,
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
) -> LogoutOut:
    """Cierra sesión eliminando la cookie access_token (idempotente, funciona sin sesión previa)."""
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
    )
    return LogoutOut(mensaje="Sesión cerrada exitosamente")


@router_abierto.get(
    "/yo",
    response_model=UsuarioYoOut,
    status_code=status.HTTP_200_OK,
)
async def yo(
    usuario_actual: UsuarioActualDep,
    session: SessionDep,
) -> UsuarioYoOut:
    """Consulta la identidad del usuario actual, sus roles en BD y los declarados en el token (CH-10)."""
    uow = UsuariosUnitOfWork(session)
    return await service.obtener_yo(
        uow, usuario_actual.id, usuario_actual.roles_token
    )


@router_abierto.post("/login", response_model=LoginOut)
async def login(
    datos: LoginIn,
    request: Request,
    response: Response,
    session: SessionDep,
) -> LoginOut:
    """Inicia sesión validando credenciales, límite de intentos y emitiendo cookie HttpOnly."""
    hash_ficticio = getattr(request.app.state, "hash_ficticio", None)
    if not hash_ficticio:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración interna del servidor: hash ficticio no inicializado",
        )

    session_factory = getattr(request.app.state, "session_factory", None)
    if not session_factory:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración interna del servidor: fábrica de sesiones no inicializada",
        )

    client_ip = request.client.host if request.client else "127.0.0.1"
    uow = UsuariosUnitOfWork(session)

    token, resultado = await service.login(
        uow, datos, hash_ficticio, client_ip, session_factory
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.JWT_MINUTOS * 60,
        secure=settings.COOKIE_SECURE,
    )
    return resultado


@router_abierto.post(
    "/cambiar-password",
    response_model=CambiarPasswordOut,
    status_code=status.HTTP_200_OK,
)
async def cambiar_password(
    datos: CambiarPasswordIn,
    usuario_actual: UsuarioActualDep,
    session: SessionDep,
) -> CambiarPasswordOut:
    """Cambia la contraseña del usuario autenticado, registrando auditoría y desactivando debe_cambiar_password (CH-11)."""
    uow = UsuariosUnitOfWork(session)
    return await service.cambiar_password(uow, usuario_actual, datos)
