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
    
    def _get_full_or_404(self, uof: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uof.productos.get_full_by_id(producto_id)
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

    def crear(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            nuevo = Producto.model_validate(data)
            print("Nuevo producto: ", nuevo)
            if data.ingredientes and type (data.ingredientes) == list:
                print("Ingredientes a asignar: ", data.ingredientes)
                for ingrediente_id in data.ingredientes:
                    uow.ingredientes.get_by_id(ingrediente_id)
                    uow.productos.link_ingrediente(nuevo.id, ingrediente_id)
            uow.productos.add(nuevo)
            result = Producto.model_validate(nuevo)
            print("Producto creado: ", result)
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
            producto = self._get_full_or_404(uow, producto_id)
                          
            print("Producto con categorias: ",producto)
            result = ProductoReadFull.model_validate(producto)
        return result

    def deactive(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.activo = False
            uow.productos.add(producto)

    def agregar_categoria_a_producto(self, producto_id: int, categoria_id: int) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            self._assert_link_not_exists(uow, producto_id, categoria_id)        
            self._get_categoria_or_404(uow, categoria_id)
            producto = self._get_full_or_404(uow, producto_id)

            uow.productos.link_categoria(producto_id, categoria_id)
            result = ProductoRead.model_validate(producto)
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
    
    def actualizar(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(producto, field, value)

            uow.productos.add(producto)
            result = ProductoRead.model_validate(producto)
        return result
