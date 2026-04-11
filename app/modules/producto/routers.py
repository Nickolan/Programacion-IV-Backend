from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import List
from sqlmodel import Session
from app.core.database import get_session
from . import schemas, services

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
def alta_producto(producto: schemas.ProductoCreate, session: Session = Depends(get_session)):
    return services.crear(session, producto)

@router.get("/", response_model=List[schemas.ProductoReadFull], status_code=status.HTTP_200_OK)
def listar_productos(skip: int = Query(0, ge=0), limit: int = Query(10, le=50), session: Session = Depends(get_session)):
    return services.obtener_todos(session, skip, limit)

@router.get("/{id}", response_model=schemas.ProductoReadFull, status_code=status.HTTP_200_OK)
def detalle_producto(id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    producto = services.obtener_por_id(session, id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.put("/{id}", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
def actualizar_producto(producto: schemas.ProductoCreate, id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    actualizado = services.actualizar_total(session, id, producto)
    if not actualizado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return actualizado

@router.put("/{id}/desactivar", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
def borrado_logico(id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    desactivado = services.desactivar(session, id)
    if not desactivado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return desactivado

@router.get("/{id}/stock", response_model=schemas.ProductoStockResponse, status_code=status.HTTP_200_OK)
def consultar_stock(id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    resultado = services.obtener_estado_stock(session, id)
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return resultado

# ─── Endpoints para la Relación N:M ─────────────────────────────────────────
@router.post("/{id}/categorias", response_model=schemas.ProductoReadFull)
def asignar_categoria(id: int, body: schemas.ProductoCategoriaAssign, session: Session = Depends(get_session)):
    producto = services.agregar_categoria_a_producto(session, id, body.categoria_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto o Categoría no encontrados")
    return producto

@router.delete("/{id}/categorias/{categoria_id}", response_model=schemas.ProductoReadFull)
def remover_categoria(id: int, categoria_id: int, session: Session = Depends(get_session)):
    producto = services.remover_categoria_de_producto(session, id, categoria_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relación Producto-Categoría no encontrada")
    return producto