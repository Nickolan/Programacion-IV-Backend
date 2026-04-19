from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import List, Optional
from sqlmodel import Session
from app.core.database import get_session
from . import schemas, services

from app.modules.producto.services import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    return ProductoService(session)

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
def alta_producto(
    producto: schemas.ProductoCreate, 
    svc: ProductoService = Depends(get_producto_service)
) -> schemas.ProductoRead:
    return svc.crear(producto)

@router.get("/", response_model=schemas.ProductoPaginadoResponse, status_code=status.HTTP_200_OK)
def listar_productos(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre: Optional[str] = None,
    svc: ProductoService = Depends(get_producto_service)
):
    return svc.obtener_todos(
        limit=limit,
        offset=offset
    )


@router.get("/{id}", response_model=schemas.ProductoReadFull, status_code=status.HTTP_200_OK)
def detalle_producto(id: int = Path(..., gt=0), svc: ProductoService = Depends(get_producto_service)):
    producto = svc.obtener_por_id(id)
    return producto

@router.put("/{id}", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
def actualizar_producto(producto: schemas.ProductoCreate, id: int = Path(..., gt=0), svc: ProductoService = Depends(get_producto_service)):
    actualizado = svc.actualizar_total(id, producto)
    return actualizado

@router.put("/{id}/desactivar", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
def borrado_logico(id: int = Path(..., gt=0), svc: ProductoService = Depends(get_producto_service)):
    desactivado = svc.switch_active(id)
    return desactivado

@router.get("/{id}/stock", response_model=schemas.ProductoStockResponse, status_code=status.HTTP_200_OK)
def consultar_stock(id: int = Path(..., gt=0), svc: ProductoService = Depends(get_producto_service)):
    resultado = svc.obtener_estado_stock(id)
    return resultado

# ─── Endpoints para la Relación N:M ─────────────────────────────────────────
@router.post("/{id}/categorias", response_model=schemas.ProductoReadFull)
def asignar_categoria(
    id: int, 
    body: schemas.ProductoCategoriaAssign, 
    svc: ProductoService = Depends(get_producto_service),
):
    producto = svc.agregar_categoria_a_producto(id, body.categoria_id)
    return producto

@router.delete("/{id}/categorias/{categoria_id}", response_model=schemas.ProductoReadFull)
def remover_categoria(id: int, categoria_id: int, svc: ProductoService = Depends(get_producto_service)):
    producto = svc.remover_categoria_de_producto(id, categoria_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relación Producto-Categoría no encontrada")
    return producto