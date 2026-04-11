from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, func
from .models import Categoria
from .schemas import CategoriaCreate, CategoriaUpdate

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