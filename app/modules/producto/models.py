from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.categoria.models import Categoria

# ─────────────────────────────────────────────────────────────────────────────
# Tabla de enlace N:M  →  Producto ↔ Categoria
# ─────────────────────────────────────────────────────────────────────────────
class ProductoCategoriaLink(SQLModel, table=True):
    """
    Relación N:M entre Producto y Categoria.
    PK compuesta evita duplicados. ondelete='CASCADE' limpia enlaces huérfanos.
    """
    __tablename__ = "producto_categoria_link"

    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    categoria_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("categoria.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )

# ─────────────────────────────────────────────────────────────────────────────
# Producto
# ─────────────────────────────────────────────────────────────────────────────
class Producto(SQLModel, table=True):
    """
    Entidad Producto.
    Relación N:M -> Un producto puede pertenecer a múltiples categorías.
    """
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    precio: float
    stock: int = Field(default=0)
    stock_minimo: int = Field(default=0)
    activo: bool = Field(default=True)

    # Relación N:M con Categoria via ProductoCategoriaLink
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoriaLink
    )