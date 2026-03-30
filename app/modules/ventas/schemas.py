from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoVenta(str, Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    cancelado = "cancelado"

class VentaBase(BaseModel):
    producto: str = Field(..., example="Silla de Oficina")
    cantidad: int = Field(ge=1, example=2)
    precio_unitario: float = Field(gt=0, example=150.50)

class VentaUpdateEstado(BaseModel):
    estado: EstadoVenta

class VentaCreate(VentaBase):
    pass

class Venta(VentaBase):
    id: int
    total: float = Field(gt=0, example=150.50)
    fecha: datetime    
    estado: EstadoVenta