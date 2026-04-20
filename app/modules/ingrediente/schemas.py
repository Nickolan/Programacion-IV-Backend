from typing import List, Optional
from pydantic import Field
from sqlmodel import SQLModel

# ─── Base ──────────────────────────────────────────────────────────────────
class IngredienteBase(SQLModel):
    nombre: str = Field(..., min_length=3, examples=["Harina"])
    unidad_medida: str = Field(..., examples=["gramo", "litro"])

# ─── Request schemas ───────────────────────────────────────────────────────
class IngredienteCreate(IngredienteBase):
    pass

class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(None, min_length=3)
    unidad_medida: Optional[str] = None

# ─── Response schemas ──────────────────────────────────────────────────────
class IngredienteRead(IngredienteBase):
    id: int

class IngredientePaginadoResponse(SQLModel):
    total: int
    items: List[IngredienteRead]

# ─── Operaciones N:M ──────────────────────────────────────────────────────
class IngredienteProductoAssign(SQLModel):
    producto_id: int

class IngredienteReadFull(IngredienteRead):
    productos: List[IngredienteProductoAssign] = []