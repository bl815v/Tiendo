from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.categoria import CategoriaDTO, CategoriaDAO

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.post("/", response_model=CategoriaDTO)
def crear_categoria(categoria: CategoriaDTO, db: Session = Depends(get_db)):
    db_categoria = CategoriaDAO(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


@router.get("/", response_model=List[CategoriaDTO])
def listar_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categorias = db.query(CategoriaDAO).offset(skip).limit(limit).all()
    return categorias


@router.get("/{categoria_id}", response_model=CategoriaDTO)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = (
        db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
    )
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaDTO)
def actualizar_categoria(
    categoria_id: int, categoria: CategoriaDTO, db: Session = Depends(get_db)
):
    db_categoria = (
        db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
    )
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for key, value in categoria.model_dump().items():
        setattr(db_categoria, key, value)

    db.commit()
    db.refresh(db_categoria)
    return db_categoria


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = (
        db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
    )
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    db.delete(db_categoria)
    db.commit()
    return {"message": "Categoría eliminada"}
