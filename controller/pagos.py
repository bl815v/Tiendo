from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from data.database import get_db
from model.pago import PagoDTO, PagoDAO

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("/", response_model=PagoDTO)
def crear_pago(pago: PagoDTO, db: Session = Depends(get_db)):
    pago_data = pago.model_dump()
    pago_data["metodo"] = pago_data["metodo"].value
    db_pago = PagoDAO(**pago_data)
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago


@router.get("/", response_model=List[PagoDTO])
def listar_pagos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pagos = db.query(PagoDAO).offset(skip).limit(limit).all()
    return pagos


@router.get("/{pago_id}", response_model=PagoDTO)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
    if pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago


@router.get("/pedido/{pedido_id}", response_model=List[PagoDTO])
def obtener_pagos_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pagos = db.query(PagoDAO).filter(PagoDAO.id_pedido == pedido_id).all()
    return pagos


@router.put("/{pago_id}", response_model=PagoDTO)
def actualizar_pago(pago_id: int, pago: PagoDTO, db: Session = Depends(get_db)):
    db_pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    update_data = pago.model_dump()
    update_data["metodo"] = update_data["metodo"].value

    for key, value in update_data.items():
        setattr(db_pago, key, value)

    db.commit()
    db.refresh(db_pago)
    return db_pago


@router.delete("/{pago_id}")
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    db.delete(db_pago)
    db.commit()
    return {"message": "Pago eliminado"}
