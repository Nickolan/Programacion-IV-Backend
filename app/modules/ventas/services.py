from typing import List, Optional
from .schemas import VentaCreate, Venta, EstadoVenta
from datetime import datetime


db_ventas: List[Venta] = []
id_counter = 1

def crear_venta(data: VentaCreate) -> Venta:
    global id_counter
    total = data.cantidad * data.precio_unitario
    fecha = datetime.now()
    estado = EstadoVenta.pendiente
    nuevo = Venta(id=id_counter, estado=estado, total=total, fecha=fecha, **data.model_dump())
    db_ventas.append(nuevo)
    id_counter += 1
    return nuevo

def obtener_todos(skip:int, limit:int) -> List[Venta]:
    return db_ventas[skip : skip + limit]

def obtener_por_ID(id:int) -> Venta:
    for v in db_ventas:
        if v.id == id:
            return v
    return None

def actualizar_estado(id:int, estado: EstadoVenta):
    for i, v in enumerate(db_ventas):
        print(v, i)
        if v.id == id:
            v_dict = v.model_dump()
            v_dict["estado"] = estado
            actualizado = Venta(**v_dict)
            db_ventas[i] = actualizado
            return actualizado
    return None