from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from data.database import get_db
from model.producto import ProductoDTO, ProductoDAO

router = APIRouter(prefix="/productos", tags=["productos"])


@router.post("/", response_model=ProductoDTO)
def crear_producto(producto: ProductoDTO, db: Session = Depends(get_db)):
    db_producto = ProductoDAO(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.get("/", response_model=List[ProductoDTO])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = db.query(ProductoDAO).offset(skip).limit(limit).all()
    return productos


@router.get("/{producto_id}", response_model=ProductoDTO)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = (
        db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
    )
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.put("/{producto_id}", response_model=ProductoDTO)
def actualizar_producto(
    producto_id: int, producto: ProductoDTO, db: Session = Depends(get_db)
):
    db_producto = (
        db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
    )
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in producto.model_dump().items():
        setattr(db_producto, key, value)

    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = (
        db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
    )
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_producto)
    db.commit()
    return {"message": "Producto eliminado"}


@router.get("/categoria/{categoria_id}", response_model=List[ProductoDTO])
def listar_productos_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    productos = (
        db.query(ProductoDAO).filter(ProductoDAO.id_categoria == categoria_id).all()
    )
    return productos
