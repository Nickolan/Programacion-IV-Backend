from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.producto.models import Producto


class UnidadMedida(str, Enum):
    unidad = "unidad"
    gramo = "gramo"
    kilogramo = "kilogramo"
    mililitro = "mililitro"
    litro = "litro"


class IngredienteProductoLink(SQLModel, table=True):
    __tablename__ = "ingrediente_producto_link"
    ingrediente_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("ingrediente.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )

class Ingrediente(SQLModel, table=True):
    """
    Entidad Ingrediente.
    Relación N:M -> Un ingrediente puede pertenecer a múltiples productos.
    """

    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    unidad_medida: UnidadMedida = Field(
        sa_column=Column(
            SAEnum(UnidadMedida, name="unidad_medida_enum"),
            nullable=False,
        )
    )

    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=IngredienteProductoLink
    )