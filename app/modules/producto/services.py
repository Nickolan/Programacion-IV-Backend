from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from .models import Producto, ProductoCategoriaLink
from .schemas import ProductoRead, ProductoCreate, ProductoUpdate, ProductoPaginadoResponse, ProductoReadFull
from app.modules.categoria.models import Categoria
from app.modules.producto.unit_of_work import ProductoUnitOfWork

class ProductoService:
    """
    
    
    """
    def __init__(self, session: Session) -> None:
        self._session = session

    # Helpers privados

    def _get_or_404(self, uof: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uof.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado."
            )
        return producto
    
    def _get_with_categorias_or_404(self, uof: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uof.productos.get_with_categorias(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado."
            )
        return producto
    
    def _get_categoria_or_404(self, uof: ProductoUnitOfWork, categoria_id: int) -> Categoria:
        categoria = uof.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con ID {categoria_id} no encontrada."
            )
        return categoria
    

    def _assert_link_not_exists(self, uof: ProductoUnitOfWork, producto_id: int, categoria_id: int):
        link = uof.productos.get_link(producto_id, categoria_id)
        if link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto {producto_id} ya tiene asignada la categoría {categoria_id}."
            )
    
    # Casos de uso

    def crear(self, data: ProductoCreate) -> Producto:
        with ProductoUnitOfWork(self._session) as uow:
            nuevo = Producto.model_validate(data)
            uow.productos.add(nuevo)
            result = ProductoRead.model_validate(nuevo)
        return result
    
    def obtener_todos(self, offset: int = 0, limit: int = 20) -> ProductoPaginadoResponse:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_paginado(offset=offset, limit=limit)
            total = uow.productos.count()

            result = ProductoPaginadoResponse(
                items=[ProductoRead.model_validate(p) for p in productos],
                total=total
            )
        return result
    
    def obtener_por_id(self, producto_id: int) -> ProductoReadFull:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_with_categorias_or_404(uow, producto_id)
            print("Producto con categorias: ",producto)
            result = ProductoReadFull.model_validate(producto)
        return result
    
    def switch_active(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.activo = not producto.activo
            uow.productos.add(producto)

    def agregar_categoria_a_producto(self, producto_id: int, categoria_id: int) -> ProductoReadFull:
        with ProductoUnitOfWork(self._session) as uow:
            self._assert_link_not_exists(uow, producto_id, categoria_id)        
            self._get_categoria_or_404(uow, categoria_id)
            producto = self._get_with_categorias_or_404(uow, producto_id)

            uow.productos.link_categoria(producto_id, categoria_id)
            result = ProductoReadFull.model_validate(producto)
        return result
    
    def obtener_estado_stock(self, producto_id: int) -> Optional[dict]:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            alerta_stock = producto.stock < producto.stock_minimo
            result = {
                "stock": producto.stock,
                "bajo_stock_minimo": alerta_stock,
                "activo": producto.activo,
            }
        return result
    
    def remover_categoria_de_producto(self, producto_id: int, categoria_id: int) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            categoria = self._get_categoria_or_404(uow, categoria_id)

            if categoria in producto.categorias:
                uow.productos.unlink_categoria(producto_id, categoria_id)

            result = ProductoRead.model_validate(producto)
        return result

def crear(session: Session, data: ProductoCreate) -> Producto:
    nuevo = Producto.model_validate(data)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo

def obtener_todos(
        session: Session, 
        offset: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None
    ) -> Tuple[int, List[Producto]]:

    query = select(Producto)

    if nombre:
        query = query.where(Producto.nombre.ilike(f"%{nombre}%"))
    
    count_query = select(func.count()).select_from(query.subquery())

    total = session.exec(count_query).one()

    results = session.exec(query.offset(offset).limit(limit)).all()


    return total, list(results)

def obtener_por_id(session: Session, id: int) -> Optional[Producto]:
    stmt = select(Producto).where(Producto.id == id).options(selectinload(Producto.categorias))
    return session.exec(stmt).first()

def actualizar_total(session: Session, id: int, data: ProductoCreate) -> Optional[Producto]:
    producto = session.get(Producto, id)
    if not producto:
        return None
    producto_data = data.model_dump(exclude_unset=True)
    for key, value in producto_data.items():
        setattr(producto, key, value)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto

def desactivar(session: Session, id: int) -> Optional[Producto]:
    producto = session.get(Producto, id)
    if not producto:
        return None
    producto.activo = False
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto

def obtener_estado_stock(session: Session, id: int) -> Optional[dict]:
    producto = session.get(Producto, id)
    if not producto:
        return None
    alerta_stock = producto.stock < producto.stock_minimo
    return {
        "stock": producto.stock,
        "bajo_stock_minimo": alerta_stock,
        "activo": producto.activo,
    }

# ─── Operaciones N:M Producto ↔ Categoria ──────────────────────────────
def agregar_categoria_a_producto(session: Session, producto_id: int, categoria_id: int) -> Optional[Producto]:
    producto = session.get(Producto, producto_id)
    categoria = session.get(Categoria, categoria_id)
    if not producto or not categoria:
        return None

    existing = session.exec(
        select(ProductoCategoriaLink).where(
            ProductoCategoriaLink.producto_id == producto_id,
            ProductoCategoriaLink.categoria_id == categoria_id,
        )
    ).first()

    if not existing:
        link = ProductoCategoriaLink(producto_id=producto_id, categoria_id=categoria_id)
        session.add(link)
        session.commit()

    return obtener_por_id(session, producto_id)

def remover_categoria_de_producto(session: Session, producto_id: int, categoria_id: int) -> Optional[Producto]:
    link = session.exec(
        select(ProductoCategoriaLink).where(
            ProductoCategoriaLink.producto_id == producto_id,
            ProductoCategoriaLink.categoria_id == categoria_id,
        )
    ).first()

    if not link:
        return None

    session.delete(link)
    session.commit()
    return obtener_por_id(session, producto_id)