from app.core.repository import BaseRepository
from sqlmodel import select
from app.modules.categoria.models import Categoria

class CategoriaRepository(BaseRepository[Categoria]):
    """
    
    Repositorio de Categorias
    
    """

    def __init__(self, session) -> None:
        super().__init__(session, Categoria)

    def get_paginado_activo(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.activo == True)
                .offset(offset)
                .limit(limit)
            ).all()
        )
    
    def count(self) -> int:
        return len(self.session.exec(select(Categoria)).all())
    
    def get_by_descripcion(self, descripcion: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.descripcion == descripcion)
        ).first()
    
    def get_by_codigo(self, codigo: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.codigo == codigo)
        ).first()