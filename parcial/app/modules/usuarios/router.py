"""Rutas de autenticación y usuarios (CH-07 y CH-09)."""

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.database import SessionDep
from app.modules.usuarios.schemas import LoginIn, LoginOut
from app.modules.usuarios.service import UsuariosService
from app.modules.usuarios.unit_of_work import UsuariosUnitOfWork

router_abierto = APIRouter(prefix="/auth", tags=["auth"])
service = UsuariosService()


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
