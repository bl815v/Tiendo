from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from data.database import get_db
from model.pedido import (
    PedidoDTO,
    PedidoDAO,
    DetallePedidoDTO,
    DetallePedidoDAO,
    EstadoPedido,
)

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("/", response_model=PedidoDTO)
def crear_pedido(pedido: PedidoDTO, db: Session = Depends(get_db)):
    pedido_data = pedido.model_dump(exclude={"detalles"})
    pedido_data["estado"] = pedido_data["estado"].value
    db_pedido = PedidoDAO(**pedido_data)
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.get("/", response_model=List[PedidoDTO])
def listar_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pedidos = db.query(PedidoDAO).offset(skip).limit(limit).all()
    return pedidos


@router.get("/{pedido_id}", response_model=PedidoDTO)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.get("/cliente/{cliente_id}", response_model=List[PedidoDTO])
def obtener_pedidos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    pedidos = db.query(PedidoDAO).filter(PedidoDAO.id_cliente == cliente_id).all()
    return pedidos


@router.put("/{pedido_id}", response_model=PedidoDTO)
def actualizar_pedido(pedido_id: int, pedido: PedidoDTO, db: Session = Depends(get_db)):
    db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    update_data = pedido.model_dump(exclude={"detalles"})
    update_data["estado"] = update_data["estado"].value

    for key, value in update_data.items():
        setattr(db_pedido, key, value)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.patch("/{pedido_id}/estado")
def actualizar_estado_pedido(
    pedido_id: int, estado: EstadoPedido, db: Session = Depends(get_db)
):
    db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    db_pedido.estado_enum = estado
    db.commit()
    return {"message": f"Estado del pedido actualizado a {estado.value}"}


@router.delete("/{pedido_id}")
def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    db.delete(db_pedido)
    db.commit()
    return {"message": "Pedido eliminado"}


@router.post("/{pedido_id}/detalles", response_model=DetallePedidoDTO)
def agregar_detalle_pedido(
    pedido_id: int, detalle: DetallePedidoDTO, db: Session = Depends(get_db)
):
    detalle_data = detalle.model_dump()
    detalle_data["id_pedido"] = pedido_id
    db_detalle = DetallePedidoDAO(**detalle_data)
    db.add(db_detalle)
    db.commit()
    db.refresh(db_detalle)
    return db_detalle


@router.get("/{pedido_id}/detalles", response_model=List[DetallePedidoDTO])
def listar_detalles_pedido(pedido_id: int, db: Session = Depends(get_db)):
    detalles = (
        db.query(DetallePedidoDAO).filter(DetallePedidoDAO.id_pedido == pedido_id).all()
    )
    return detalles
