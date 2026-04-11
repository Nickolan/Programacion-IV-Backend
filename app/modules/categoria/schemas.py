from typing import List, Optional
from pydantic import Field
from sqlmodel import SQLModel

# ─── Base ──────────────────────────────────────────────────────────────────
class CategoriaBase(SQLModel):
    codigo: str = Field(..., pattern=r"^[A-Z]{3}-\d{2}$", examples=["MUE-01"])
    descripcion: str = Field(..., min_length=3, examples=["Muebles de Oficina"])
    activo: bool = True

# ─── Request schemas ───────────────────────────────────────────────────────
class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(SQLModel):
    codigo: Optional[str] = Field(None, pattern=r"^[A-Z]{3}-\d{2}$")
    descripcion: Optional[str] = Field(None, min_length=3)
    activo: Optional[bool] = None

# ─── Response schemas ──────────────────────────────────────────────────────
class CategoriaRead(CategoriaBase):
    id: int

class ProductoBasicRead(SQLModel):
    """Schema reducido para evitar import circular."""
    id: int
    nombre: str
    precio: float
    activo: bool

class CategoriaReadFull(CategoriaRead):
    """Categoria con sus productos (N:M)."""
    productos: List[ProductoBasicRead] = []

class CategoriaPaginadoResponse(SQLModel):
    total: int
    items: List[CategoriaRead]