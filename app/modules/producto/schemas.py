from typing import List, Optional
from pydantic import Field
from sqlmodel import SQLModel

# ─── Base ──────────────────────────────────────────────────────────────────
class ProductoBase(SQLModel):
    nombre: str = Field(..., examples=["Cerveza Quilmes"])
    descripcion: str = Field(..., examples=["Cerveza rubia, ideal para acompañar una picada."])
    precio_base: float = Field(gt=0, examples=[150.50])
    stock: int = Field(ge=0, examples=[20])
    stock_minimo: int = Field(ge=0, examples=[5])
    imagenes_url: List[str] = Field(default_factory=list, examples=[["https://example.com/producto/pizza.jpg"]])
    disponible: bool = True

# ─── Request schemas ───────────────────────────────────────────────────────
class ProductoCreate(ProductoBase):
    ingredientes: Optional[List[int]] = Field(default=None, examples=[[1, 2, 3]])
    pass 

class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(..., examples=["Cerveza Quilmes"])
    descripcion: Optional[str] = Field(None, examples=["Cerveza rubia, ideal para acompañar una picada."])
    precio_base: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    imagenes_url: Optional[List[str]] = Field(None, examples=[["https://example.com/producto/pizza.jpg"]])
    disponible: Optional[bool] = None
# ─── Response schemas ──────────────────────────────────────────────────────
class ProductoRead(ProductoBase):
    id: int
    activo: bool
    # created_at: str
    # updated_at: str
    # deleted_at: Optional[str] = None

class CategoriaBasicRead(SQLModel):
    """Schema reducido para evitar import circular."""
    id: int
    descripcion: str
    activo: bool
    imagen_url: Optional[str]

class ProductoReadFull(ProductoRead):
    """Producto con sus categorías anidadas."""
    categorias: List[CategoriaBasicRead] = []
    ingredientes: List[IngredienteBasicRead] = []

class ProductoStockResponse(SQLModel):
    stock: int
    bajo_stock_minimo: bool
    activo: bool

# ─── Operaciones N:M ──────────────────────────────────────────────────────
class ProductoCategoriaAssign(SQLModel):
    categoria_id: int

class ProductoPaginadoResponse(SQLModel):
    total: int
    items: List[ProductoRead]

# ─── Operaciones con Ingredientes ─────────────────────────────────────────
class IngredienteBasicRead(SQLModel):
    """Schema reducido para evitar import circular."""
    id: int
    nombre: str
    es_alergeno: bool
    es_removible: Optional[bool] = None

class ProductoReadWithIngredientes(ProductoRead):
    """Producto con sus ingredientes anidados."""
    ingredientes: List[IngredienteBasicRead] = []