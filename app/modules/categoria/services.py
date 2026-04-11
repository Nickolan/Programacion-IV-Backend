from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from .models import Categoria
from .schemas import CategoriaCreate, CategoriaUpdate

def crear(session: Session, data: CategoriaCreate) -> Categoria:
    categoria = Categoria.model_validate(data)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

def obtener_todas(session: Session, skip: int = 0, limit: int = 10) -> List[Categoria]:
    stmt = select(Categoria).options(selectinload(Categoria.productos)).offset(skip).limit(limit)
    return list(session.exec(stmt).all())

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