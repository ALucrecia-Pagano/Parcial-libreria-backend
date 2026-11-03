"""Punto de entrada de la API TP Librería."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import dispose_resources, init_resources
from app.modules.autores.router import router as autores_router
from app.modules.clientes.router import router as clientes_router
from app.modules.editoriales.router import router as editoriales_router
from app.modules.generos.router import router as generos_router
from app.modules.health.router import router as health_router
from app.modules.libros.router import router as libros_router
from app.modules.ventas.router import router as ventas_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Crea el motor y la fábrica en el arranque, cierra el motor al apagar."""
    app.state.engine, app.state.session_factory = init_resources()
    yield
    await dispose_resources()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(health_router)
app.include_router(editoriales_router)
app.include_router(generos_router)
app.include_router(autores_router)
app.include_router(libros_router)
app.include_router(clientes_router)
app.include_router(ventas_router)

@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"app": settings.APP_NAME, "status": "ok"}
