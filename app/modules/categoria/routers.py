from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import List, Optional
from sqlmodel import Session
from app.core.database import get_session
from . import schemas, services

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.post("/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED)
def alta_categoria(categoria: schemas.CategoriaCreate, session: Session = Depends(get_session)):
    return services.crear(session, categoria)

@router.get("/", response_model=schemas.CategoriaPaginadoResponse, status_code=status.HTTP_200_OK)
def listar_categorias(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    descripcion: Optional[str] = None,
    session: Session = Depends(get_session)
):
    total, items = services.obtener_todas(
        session=session,
        offset=offset,
        limit=limit,
        descripcion=descripcion
    )
    return {
        "total": total,
        "items": items
    }

@router.get("/{id}", response_model=schemas.CategoriaReadFull, status_code=status.HTTP_200_OK)
def detalle_categoria(id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    categoria = services.obtener_por_id(session, id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return categoria

@router.put("/{id}", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK)
def actualizar_categoria(categoria: schemas.CategoriaCreate, id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    actualizada = services.actualizar_total(session, id, categoria)
    if not actualizada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return actualizada

@router.put("/{id}/desactivar", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK)
def borrado_logico(id: int = Path(..., gt=0), session: Session = Depends(get_session)):
    desactivada = services.desactivar(session, id)
    if not desactivada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return desactivada