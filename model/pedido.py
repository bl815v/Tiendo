from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from data.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

# Enum para estado del pedido
class EstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    ENVIADO = "ENVIADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"

# Modelo SQLAlchemy
class PedidoDAO(Base):
    __tablename__ = 'pedido'
    
    id_pedido = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    fecha_pedido = Column(DateTime, default=func.now())
    total = Column(Float, nullable=False)
    estado = Column(String(50), default=EstadoPedido.PENDIENTE.value)
    
    # Relaciones
    cliente = relationship("ClienteDAO", back_populates="pedidos")
    detalles = relationship("DetallePedidoDAO", back_populates="pedido", cascade="all, delete-orphan")
    envio = relationship("EnvioDAO", back_populates="pedido", uselist=False, cascade="all, delete-orphan")
    pagos = relationship("PagoDAO", back_populates="pedido", cascade="all, delete-orphan")

# Modelo para detalles del pedido
class DetallePedidoDAO(Base):
    __tablename__ = 'detalle_pedido'
    
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey('pedido.id_pedido'), nullable=False)
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    
    # Relaciones
    pedido = relationship("PedidoDAO", back_populates="detalles")
    producto = relationship("ProductoDAO", back_populates="detalles_pedido")

# DTOs
class DetallePedidoDTO(BaseModel):
    id_detalle: int
    id_pedido: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    
    class Config:
        from_attributes = True

class DetallePedidoCreateDTO(BaseModel):  # Agregar este DTO
    id_producto: int
    cantidad: int
    precio_unitario: float
    
    class Config:
        from_attributes = True

class PedidoDTO(BaseModel):
    id_pedido: int
    id_cliente: int
    fecha_pedido: datetime
    total: float
    estado: str
    detalles: List[DetallePedidoDTO] = []
    
    class Config:
        from_attributes = True

class PedidoCreateDTO(BaseModel):  # Agregar este DTO
    id_cliente: int
    fecha_pedido: Optional[datetime] = None
    total: float
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    detalles: List[DetallePedidoCreateDTO] = []
    
    class Config:
        from_attributes = True