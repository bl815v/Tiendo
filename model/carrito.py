from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from data.database import Base

class DetalleCarritoDTO(BaseModel):
    id_detalle_carrito: Optional[int] = None
    id_carrito: int
    id_producto: int
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True

class CarritoDTO(BaseModel):
    id_carrito: Optional[int] = None
    id_cliente: int
    fecha_creacion: Optional[datetime] = None
    activo: bool = True
    detalles: List[DetalleCarritoDTO] = []

    class Config:
        from_attributes = True

class DetalleCarritoDAO(Base):
    __tablename__ = "detalle_carrito"

    id_detalle_carrito = Column(Integer, primary_key=True, index=True)
    id_carrito = Column(Integer, ForeignKey('carrito.id_carrito'), nullable=False)
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    carrito = relationship("CarritoDAO", back_populates="detalles")
    producto = relationship("ProductoDAO", back_populates="detalle_carrito")

class CarritoDAO(Base):
    __tablename__ = "carrito"

    id_carrito = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    cliente = relationship("ClienteDAO", back_populates="carritos")
    detalles = relationship("DetalleCarritoDAO", back_populates="carrito")
