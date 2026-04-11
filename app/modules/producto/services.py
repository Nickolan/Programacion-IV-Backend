from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from .models import Producto, ProductoCategoriaLink
from .schemas import ProductoCreate, ProductoUpdate
from app.modules.categoria.models import Categoria

def crear(session: Session, data: ProductoCreate) -> Producto:
    nuevo = Producto.model_validate(data)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo

def obtener_todos(session: Session, skip: int, limit: int) -> List[Producto]:
    stmt = select(Producto).options(selectinload(Producto.categorias)).offset(skip).limit(limit)
    return list(session.exec(stmt).all())

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