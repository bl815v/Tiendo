from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from data.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Modelo SQLAlchemy
class CarritoDAO(Base):
    __tablename__ = 'carrito'
    
    id_carrito = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Relaciones
    cliente = relationship("ClienteDAO", back_populates="carritos")
    detalles = relationship("DetalleCarritoDAO", back_populates="carrito")

# Modelo para detalles del carrito
class DetalleCarritoDAO(Base):
    __tablename__ = 'detalle_carrito'
    
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_carrito = Column(Integer, ForeignKey('carrito.id_carrito'), nullable=False)
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    
    # Relaciones
    carrito = relationship("CarritoDAO", back_populates="detalles")
    producto = relationship("ProductoDAO", back_populates="detalles_carrito")

# DTOs
class DetalleCarritoDTO(BaseModel):
    id_detalle: int
    id_carrito: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    
    class Config:
        from_attributes = True

class DetalleCarritoCreateDTO(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float
    
    class Config:
        from_attributes = True

class CarritoDTO(BaseModel):
    id_carrito: int
    id_cliente: int
    fecha_creacion: datetime
    activo: int
    detalles: List[DetalleCarritoDTO] = []
    
    class Config:
        from_attributes = True

class CarritoCreateDTO(BaseModel):
    id_cliente: int
    fecha_creacion: Optional[datetime] = None
    activo: int = 1
    detalles: List[DetalleCarritoCreateDTO] = []
    
    class Config:
        from_attributes = True