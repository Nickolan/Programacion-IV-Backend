from typing import Any, Optional

from sqlmodel import select

from app.core.repository import BaseRepository
from app.modules.categoria.models import Categoria

class CategoriaRepository(BaseRepository[Categoria]):
    """
    
    Repositorio de Categorias
    
    """

    def __init__(self, session) -> None:
        super().__init__(session, Categoria)

    def get_paginado_activo(self, offset: int = 0, limit: int = 20, nombre: Optional[str] = None) -> list[Categoria]:
        stmt = select(Categoria).where(Categoria.activo == True)
        if nombre:
            stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
        return list(
            self.session.exec(
                stmt
                .offset(offset)
                .limit(limit)
            ).all()
        )
    

    # Traer subcategorias de una categoria
    def get_subcategorias(self, categoria_id: int) -> list[Categoria]:
        stmt = select(Categoria).where(
            Categoria.parent_id == categoria_id,
            Categoria.activo == True,
            Categoria.deleted_at == None,
        )
        return list(self.session.exec(stmt).all())

    def get_categoria_con_arbol_activas(self, categoria_id: int) -> dict[str, Any] | None:
        stmt = select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.activo == True,
            Categoria.deleted_at == None,
        )
        categoria = self.session.exec(stmt).first()
        if not categoria:
            return None

        return self._armar_arbol_categoria_activa(categoria)

    def _armar_arbol_categoria_activa(self, categoria: Categoria) -> dict[str, Any]:
        subcategorias = self.get_subcategorias(categoria.id)
        return {
            **categoria.model_dump(),
            "subcategorias": [
                self._armar_arbol_categoria_activa(subcategoria)
                for subcategoria in subcategorias
            ],
        }
    
    def count(self) -> int:
        return len(self.session.exec(select(Categoria)).all())
    
    # def get_by_descripcion(self, descripcion: str) -> Categoria | None:
    #     return self.session.exec(
    #         select(Categoria).where(Categoria.descripcion == descripcion)
    #     ).first()
    
    # def get_by_codigo(self, codigo: str) -> Categoria | None:
    #     return self.session.exec(
    #         select(Categoria).where(Categoria.codigo == codigo)
    #     ).first()
    
    def get_by_nombre(self, nombre: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()