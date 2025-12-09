from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.envio import EnvioDTO, EnvioDAO, EnvioCreateDTO

router = APIRouter(prefix="/envios", tags=["envios"])


@router.post("/", response_model=EnvioDTO)
def crear_envio(envio: EnvioCreateDTO, db: Session = Depends(get_db)):  # Usar EnvioCreateDTO
    db_envio = EnvioDAO(**envio.model_dump())
    db.add(db_envio)
    db.commit()
    db.refresh(db_envio)
    return db_envio


@router.get("/", response_model=List[EnvioDTO])
def listar_envios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    envios = db.query(EnvioDAO).offset(skip).limit(limit).all()
    return envios


@router.get("/{envio_id}", response_model=EnvioDTO)
def obtener_envio(envio_id: int, db: Session = Depends(get_db)):
    envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
    if envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@router.get("/pedido/{pedido_id}", response_model=EnvioDTO)
def obtener_envio_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
    envio = db.query(EnvioDAO).filter(EnvioDAO.id_pedido == pedido_id).first()
    if envio is None:
        raise HTTPException(
            status_code=404, detail="Envío no encontrado para este pedido"
        )
    return envio


@router.put("/{envio_id}", response_model=EnvioDTO)
def actualizar_envio(envio_id: int, envio: EnvioCreateDTO, db: Session = Depends(get_db)):  # Usar EnvioCreateDTO
    db_envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
    if db_envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")

    for key, value in envio.model_dump().items():
        setattr(db_envio, key, value)

    db.commit()
    db.refresh(db_envio)
    return db_envio


@router.delete("/{envio_id}")
def eliminar_envio(envio_id: int, db: Session = Depends(get_db)):
    db_envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
    if db_envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")

    db.delete(db_envio)
    db.commit()
    return {"message": "Envío eliminado"}