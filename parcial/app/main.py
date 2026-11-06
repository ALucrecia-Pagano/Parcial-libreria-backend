"""Punto de entrada de la API TP Librería.

Estructura de dos grupos de rutas (CH-10):
- Grupo abierto: health, auth y consultas públicas de catálogo.
- Grupo protegido: exige sesión activa y verifica que la contraseña esté al día
  (exigir_password_al_dia, RN-06). Incluye routers con sus respectivas guardas
  de rol (requiere_rol("ADMIN"), requiere_rol("VENDEDOR", "ADMIN")) y rutas sin rol fijo.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from app.core.config import settings
from app.core.database import dispose_resources, init_resources
from app.core.dependencies import exigir_password_al_dia, requiere_rol
from app.core.security import hashear_password
import app.modules.autores.router as autores_module
import app.modules.clientes.router as clientes_module
import app.modules.editoriales.router as editoriales_module
import app.modules.generos.router as generos_module
from app.modules.health.router import router as health_router
import app.modules.libros.router as libros_module
import app.modules.usuarios.router as usuarios_module
import app.modules.ventas.router as ventas_module


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Crea el motor y la fábrica en el arranque, calcula el hash ficticio, cierra al apagar."""
    app.state.engine, app.state.session_factory = init_resources()
    app.state.hash_ficticio = await hashear_password("fake-password-for-anti-enumeration")
    yield
    await dispose_resources(app.state.engine)


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


def _asegurar_sin_trailing_slash(router: APIRouter) -> None:
    """Permite que las peticiones sin barra final ('/recurso') y con barra ('/recurso/')
    funcionen indistintamente sin provocar redirecciones 307."""
    rutas_extra = []
    for r in list(router.routes):
        if isinstance(r, APIRoute) and r.path == "/":
            rutas_extra.append(
                APIRoute(
                    path="",
                    endpoint=r.endpoint,
                    methods=r.methods,
                    response_model=r.response_model,
                    status_code=r.status_code,
                    dependencies=r.dependencies,
                    summary=r.summary,
                    description=r.description,
                    tags=r.tags,
                )
            )
    router.routes.extend(rutas_extra)


# --- GRUPO ABIERTO ---
# No pide autenticación ni el control de cambio obligatorio (consigna pág. 16)
grupo_abierto = APIRouter()
_asegurar_sin_trailing_slash(health_router)
grupo_abierto.include_router(health_router)
_asegurar_sin_trailing_slash(usuarios_module.router_abierto)
grupo_abierto.include_router(usuarios_module.router_abierto)


def _separar_router_catalogo(
    modulo: Any, prefix: str, tags: list[str]
) -> tuple[APIRouter, APIRouter]:
    """Separa rutas de catálogo entre abiertas (GET) y administrativas (escritura)."""
    if hasattr(modulo, "router_abierto") and hasattr(modulo, "router_admin"):
        r_abierto = modulo.router_abierto
        r_admin = modulo.router_admin
    else:
        router_orig = getattr(modulo, "router")
        r_abierto = APIRouter(prefix=prefix, tags=tags)
        r_admin = APIRouter(prefix=prefix, tags=tags)
        for route in router_orig.routes:
            methods = getattr(route, "methods", set())
            if "GET" in methods:
                r_abierto.routes.append(route)
            else:
                r_admin.routes.append(route)

    _asegurar_sin_trailing_slash(r_abierto)
    _asegurar_sin_trailing_slash(r_admin)
    return r_abierto, r_admin


editoriales_abierto, editoriales_admin = _separar_router_catalogo(
    editoriales_module, prefix="/editoriales", tags=["editoriales"]
)
generos_abierto, generos_admin = _separar_router_catalogo(
    generos_module, prefix="/generos", tags=["generos"]
)
autores_abierto, autores_admin = _separar_router_catalogo(
    autores_module, prefix="/autores", tags=["autores"]
)
libros_abierto, libros_admin = _separar_router_catalogo(
    libros_module, prefix="/libros", tags=["libros"]
)

grupo_abierto.include_router(editoriales_abierto)
grupo_abierto.include_router(generos_abierto)
grupo_abierto.include_router(autores_abierto)
grupo_abierto.include_router(libros_abierto)

# Rutas públicas de catálogo por entidad de libros si existen (CH-05)
if hasattr(libros_module, "router_por_entidad"):
    _asegurar_sin_trailing_slash(libros_module.router_por_entidad)
    grupo_abierto.include_router(libros_module.router_por_entidad)


# --- GRUPO PROTEGIDO ---
# Exige sesión activa y verificar que la contraseña esté al día (RN-06).
# Montado una sola vez a nivel del grupo protegido.
grupo_protegido = APIRouter(dependencies=[Depends(exigir_password_al_dia)])

# 1. Rutas exclusivas de ADMIN
grupo_protegido.include_router(
    editoriales_admin, dependencies=[Depends(requiere_rol("ADMIN"))]
)
grupo_protegido.include_router(
    generos_admin, dependencies=[Depends(requiere_rol("ADMIN"))]
)
grupo_protegido.include_router(
    autores_admin, dependencies=[Depends(requiere_rol("ADMIN"))]
)
grupo_protegido.include_router(
    libros_admin, dependencies=[Depends(requiere_rol("ADMIN"))]
)

# Rutas administrativas de usuarios (CH-12: alta de personal, roles, eventos)
if hasattr(usuarios_module, "router_admin"):
    _asegurar_sin_trailing_slash(usuarios_module.router_admin)
    grupo_protegido.include_router(
        usuarios_module.router_admin, dependencies=[Depends(requiere_rol("ADMIN"))]
    )

# 2. Rutas de personal (staff: VENDEDOR o ADMIN)
if hasattr(clientes_module, "router_staff"):
    _asegurar_sin_trailing_slash(clientes_module.router_staff)
    grupo_protegido.include_router(
        clientes_module.router_staff,
        dependencies=[Depends(requiere_rol("VENDEDOR", "ADMIN"))],
    )
else:
    _asegurar_sin_trailing_slash(clientes_module.router)
    grupo_protegido.include_router(
        clientes_module.router,
        dependencies=[Depends(requiere_rol("VENDEDOR", "ADMIN"))],
    )

# 3. Rutas de ventas
if hasattr(ventas_module, "router_staff") and hasattr(ventas_module, "router_protegido"):
    _asegurar_sin_trailing_slash(ventas_module.router_staff)
    _asegurar_sin_trailing_slash(ventas_module.router_protegido)
    grupo_protegido.include_router(
        ventas_module.router_staff,
        dependencies=[Depends(requiere_rol("VENDEDOR", "ADMIN"))],
    )
    grupo_protegido.include_router(ventas_module.router_protegido)
else:
    # Segrega GET /{venta_id} (que no lleva requiere_rol en router) del resto (staff)
    ventas_orig = getattr(ventas_module, "router")
    v_staff = APIRouter(prefix="/ventas", tags=["ventas"])
    v_autenticado = APIRouter(prefix="/ventas", tags=["ventas"])
    for route in ventas_orig.routes:
        path = getattr(route, "path", "")
        if path.endswith("/{venta_id}"):
            v_autenticado.routes.append(route)
        else:
            v_staff.routes.append(route)
    _asegurar_sin_trailing_slash(v_staff)
    _asegurar_sin_trailing_slash(v_autenticado)
    grupo_protegido.include_router(
        v_staff, dependencies=[Depends(requiere_rol("VENDEDOR", "ADMIN"))]
    )
    grupo_protegido.include_router(v_autenticado)

app.include_router(grupo_abierto)
app.include_router(grupo_protegido)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"app": settings.APP_NAME, "status": "ok"}
