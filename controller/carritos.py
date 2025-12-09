from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from data.database import get_db
from model.carrito import CarritoDTO, CarritoDAO, DetalleCarritoDTO, DetalleCarritoDAO, CarritoCreateDTO, DetalleCarritoCreateDTO

router = APIRouter(prefix="/carritos", tags=["carritos"])


@router.post("/", response_model=CarritoDTO)
def crear_carrito(carrito: CarritoCreateDTO, db: Session = Depends(get_db)):  # Usar CarritoCreateDTO
    db_carrito = CarritoDAO(**carrito.model_dump(exclude={"detalles"}))
    db.add(db_carrito)
    db.commit()
    db.refresh(db_carrito)
    return db_carrito


@router.get("/", response_model=List[CarritoDTO])
def listar_carritos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    carritos = db.query(CarritoDAO).offset(skip).limit(limit).all()
    return carritos


@router.get("/{carrito_id}", response_model=CarritoDTO)
def obtener_carrito(carrito_id: int, db: Session = Depends(get_db)):
    carrito = db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
    if carrito is None:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return carrito


@router.get("/cliente/{cliente_id}", response_model=List[CarritoDTO])
def obtener_carritos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    carritos = db.query(CarritoDAO).filter(CarritoDAO.id_cliente == cliente_id).all()
    return carritos


@router.put("/{carrito_id}", response_model=CarritoDTO)
def actualizar_carrito(
    carrito_id: int, carrito: CarritoCreateDTO, db: Session = Depends(get_db)  # Usar CarritoCreateDTO
):
    db_carrito = (
        db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
    )
    if db_carrito is None:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    for key, value in carrito.model_dump(exclude={"detalles"}).items():
        setattr(db_carrito, key, value)

    db.commit()
    db.refresh(db_carrito)
    return db_carrito


@router.delete("/{carrito_id}")
def eliminar_carrito(carrito_id: int, db: Session = Depends(get_db)):
    db_carrito = (
        db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
    )
    if db_carrito is None:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    db.delete(db_carrito)
    db.commit()
    return {"message": "Carrito eliminado"}


@router.post("/{carrito_id}/detalles", response_model=DetalleCarritoDTO)
def agregar_detalle_carrito(
    carrito_id: int, detalle: DetalleCarritoCreateDTO, db: Session = Depends(get_db)  # Usar DetalleCarritoCreateDTO
):
    detalle_data = detalle.model_dump()
    detalle_data["id_carrito"] = carrito_id
    db_detalle = DetalleCarritoDAO(**detalle_data)
    db.add(db_detalle)
    db.commit()
    db.refresh(db_detalle)
    return db_detalle


@router.get("/{carrito_id}/detalles", response_model=List[DetalleCarritoDTO])
def listar_detalles_carrito(carrito_id: int, db: Session = Depends(get_db)):
    detalles = (
        db.query(DetalleCarritoDAO)
        .filter(DetalleCarritoDAO.id_carrito == carrito_id)
        .all()
    )
    return detalles