from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.cliente import ClienteDTO, ClienteDAO

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/", response_model=ClienteDTO)
def crear_cliente(cliente: ClienteDTO, db: Session = Depends(get_db)):
    existing_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.correo == cliente.correo).first()
    )
    if existing_cliente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    db_cliente = ClienteDAO(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.get("/", response_model=List[ClienteDTO])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = db.query(ClienteDAO).offset(skip).limit(limit).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClienteDTO)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteDTO)
def actualizar_cliente(
    cliente_id: int, cliente: ClienteDTO, db: Session = Depends(get_db)
):
    db_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    )
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if cliente.correo != db_cliente.correo:
        existing_cliente = (
            db.query(ClienteDAO).filter(ClienteDAO.correo == cliente.correo).first()
        )
        if existing_cliente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

    for key, value in cliente.model_dump().items():
        setattr(db_cliente, key, value)

    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    )
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(db_cliente)
    db.commit()
    return {"message": "Cliente eliminado"}
