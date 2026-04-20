from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.modules.ingrediente.models import Ingrediente, IngredienteProductoLink
from app.modules.producto.models import Producto
from app.modules.ingrediente.schemas import IngredienteRead, IngredienteCreate, IngredienteUpdate, IngredientePaginadoResponse, IngredienteReadFull
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork


class IngredienteService:
    """
    Servicio de Ingredientes

    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # Helpers privados

    def _get_or_404(self, uof: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uof.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con ID {ingrediente_id} no encontrado."
            )
        return ingrediente
    
    def _get_with_productos_or_404(self, uof: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uof.ingredientes.get_with_productos(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con ID {ingrediente_id} no encontrado."
            )
        return ingrediente
    
    def _get_producto_or_404(self, uof: IngredienteUnitOfWork, producto_id: int) -> Producto:
        producto = uof.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado."
            )
        return producto
    
    # Casos de uso

    def crear(self, data: IngredienteCreate) -> Ingrediente:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredienteRead.model_validate(ingrediente)
        return result

    def listar(self, offset: int = 0, limit: int = 20) -> IngredientePaginadoResponse:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_paginado(offset, limit)
            total = uow.ingredientes.count()
            items = [IngredienteRead.model_validate(ing) for ing in ingredientes]

            result = IngredientePaginadoResponse(
                total=total,
                items=items
            )
        return result
    
    def obtener_por_id(self, ingrediente_id: int) -> IngredienteReadFull:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_with_productos_or_404(uow, ingrediente_id)
            result = IngredienteReadFull.model_validate(ingrediente)
        return result
    
    def actualizar(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(ingrediente, key, value)
            uow.ingredientes.update(ingrediente)
            result = IngredienteRead.model_validate(ingrediente)
        return result
    
    def eliminar(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            uow.ingredientes.delete(ingrediente)

    def agregar_a_producto(self, ingrediente_id: int, producto_id: int) -> IngredienteReadFull:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            self._get_producto_or_404(uow, producto_id)
            uow.ingredientes.link_producto(ingrediente_id, producto_id)
            result = IngredienteReadFull.model_validate(ingrediente)
        return result
    
    def remover_de_producto(self, ingrediente_id: int, producto_id: int) -> IngredienteReadFull:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uof=uow, ingrediente_id=ingrediente_id)
            self._get_producto_or_404(uof=uow, producto_id=producto_id)
            uow.ingredientes.unlink_producto(ingrediente_id, producto_id)
            result = IngredienteReadFull.model_validate(ingrediente)
        return result