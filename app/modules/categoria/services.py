from fastapi import HTTPException, status
from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, func

from .models import Categoria
from .schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaPaginadoResponse, CategoriaReadFull
from app.modules.categoria.unit_of_work import CategoriaUnitOfWork
from app.modules.producto.schemas import ProductoRead

class CategoriaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    # Helpers

    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        return categoria
    
    def _assert_descripcion_unique(self, uow: CategoriaUnitOfWork, descripcion: str) -> None:
        existing = uow.categorias.get_by_descripcion(descripcion)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoria con descripcion='{descripcion}'",
            )
    
    def _assert_codigo_unique(self, uow: CategoriaUnitOfWork, codigo: str) -> None:
        existing = uow.categorias.get_by_codigo(codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoria con codigo='{codigo}'",
            )
        
    def crear_categoria(self, data: CategoriaCreate) -> CategoriaRead:
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_descripcion_unique(uow, data.descripcion)
            self._asser_codigo_unique(uow, data.codigo)
            nueva = Categoria.model_validate(data)
            uow.categorias.add(nueva)
            result = CategoriaRead.model_validate(nueva)
        return result
    
    def obtener_todas(self, offset: int = 0, limit: int = 20) -> CategoriaPaginadoResponse:
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categorias.get_paginado_activo(offset=offset, limit=limit)
            total = uow.categorias.count()
            items = [CategoriaRead.model_validate(c) for c in categorias]
        return CategoriaPaginadoResponse(total=total, items=items)
    
    def obtener_por_id(self, categoria_id: int) -> CategoriaRead:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaRead.model_validate(categoria)
        return result
    
    def obtener_con_productos(self, categoria_id: int) -> CategoriaReadFull:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            productos = uow.productos.get_by_categoria_id(categoria_id)
            categoria_data = categoria.model_dump()
            productos_data = [ProductoRead.model_validate(p) for p in productos]

        return CategoriaReadFull.model_validate(
            **categoria_data,
            productos=productos_data
        )
    
    def actualizar_total(self, categoria_id: int, data: CategoriaCreate) -> Optional[Categoria]:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            if data.descripcion and data.descripcion != categoria.descripcion:
                self._assert_descripcion_unique(uow, data.descripcion)
            if data.codigo and data.codigo != categoria.codigo:
                self._assert_codigo_unique(uow, data.codigo)
            categoria_data = data.model_dump(exclude_unset=True)
            for key, value in categoria_data.items():
                setattr(categoria, key, value)
            uow.categorias.update(categoria)
        return categoria
    
    def desactivar(self, categoria_id: int) -> Optional[Categoria]:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            categoria.activo = False
            uow.categorias.update(categoria)
        return categoria


def crear(session: Session, data: CategoriaCreate) -> Categoria:
    categoria = Categoria.model_validate(data)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

def obtener_todas(
        session: Session, 
        offset: int = 0,
        limit: int = 100,
        descripcion: Optional[str] = None
    ) -> Tuple[int, List[Categoria]]:
    
    query = select(Categoria)

    if descripcion:
        query = query.where(Categoria.descripcion.ilike(f"%{descripcion}%"))

    count_query = select(func.count()).select_from(query.subquery())

    total = session.exec(count_query).one()

    results = session.exec(query.offset(offset).limit(limit)).all()

    return total, list(results)

def obtener_por_id(session: Session, id: int) -> Optional[Categoria]:
    stmt = select(Categoria).where(Categoria.id == id).options(selectinload(Categoria.productos))
    return session.exec(stmt).first()

def actualizar_total(session: Session, id: int, data: CategoriaCreate) -> Optional[Categoria]:
    categoria = session.get(Categoria, id)
    if not categoria:
        return None
    categoria_data = data.model_dump(exclude_unset=True)
    for key, value in categoria_data.items():
        setattr(categoria, key, value)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

def desactivar(session: Session, id: int) -> Optional[Categoria]:
    categoria = session.get(Categoria, id)
    if not categoria:
        return None
    categoria.activo = False
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria