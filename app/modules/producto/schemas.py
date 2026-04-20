from typing import List, Optional
from pydantic import Field
from sqlmodel import SQLModel

# ─── Base ──────────────────────────────────────────────────────────────────
class ProductoBase(SQLModel):
    nombre: str = Field(..., examples=["Silla de Oficina"])
    precio: float = Field(gt=0, examples=[150.50])
    stock: int = Field(ge=0, examples=[20])
    stock_minimo: int = Field(ge=0, examples=[5])
    activo: bool = True

# ─── Request schemas ───────────────────────────────────────────────────────
class ProductoCreate(ProductoBase):
    pass 

class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

# ─── Response schemas ──────────────────────────────────────────────────────
class ProductoRead(ProductoBase):
    id: int

class CategoriaBasicRead(SQLModel):
    """Schema reducido para evitar import circular."""
    id: int
    codigo: str
    descripcion: str
    activo: bool

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
    unidad_medida: str

class ProductoReadWithIngredientes(ProductoRead):
    """Producto con sus ingredientes anidados."""
    ingredientes: List[IngredienteBasicRead] = []