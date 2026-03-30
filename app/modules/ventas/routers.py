from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List
from . import schemas, services

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post(
    '/', response_model=schemas.Venta, status_code=status.HTTP_201_CREATED
)
def crear_venta(venta: schemas.VentaCreate):
    return services.crear_venta(data=venta)

@router.get(
    '/', response_model=List[schemas.Venta], status_code=status.HTTP_200_OK
)
def listar_ventas(skip: int = Query(0, ge=0), limit: int = Query(10, le=50)):
    return services.obtener_todos(skip, limit)

@router.get(
    "/{id}", response_model=schemas.Venta, status_code=status.HTTP_200_OK
)
def detalle_venta(id: int = Path(..., gt=0)):
    venta = services.obtener_por_ID(id)
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada"
        )
    return venta;

@router.put(
    "/{id}/", response_model=schemas.Venta, status_code=status.HTTP_202_ACCEPTED
)
def actualizar_estado_venta(estado: schemas.EstadoVenta, id:int = Path(..., gt=0)):
    actualizado = services.actualizar_estado(id=id, estado=estado)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro la venta solicitada"
        )
    return actualizado
