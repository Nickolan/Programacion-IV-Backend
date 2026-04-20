from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine

from app.modules.categoria.models import Categoria
from app.modules.producto.models import Producto, ProductoCategoriaLink
from app.modules.ingrediente.models import Ingrediente, IngredienteProductoLink

from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router
from app.modules.ventas.routers import router as vanta_router
from app.modules.ingrediente.routers import router as ingrediente_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: crea todas las tablas registradas en SQLModel.metadata.
    Shutdown: espacio para cerrar conexiones, caches, etc.
    """
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="FastAPI + SQLModel — Relaciones 1:1 · 1:N · N:M",
    version="1.4.0",
    description=(
        "Proyecto modular que demuestra las tres relaciones principales:\n\n"
        "- **1:N** Categoria → Productos (FK `team_id` en Producto, lado N)\n"
        "- **N:M** Producto ↔ Cateogira via `ProductoCategoriaLink`"
    ),
    lifespan=lifespan,
)

app.include_router(producto_router)
app.include_router(categoria_router)
app.include_router(vanta_router)
app.include_router(ingrediente_router)