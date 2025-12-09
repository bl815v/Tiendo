from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from data.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Modelo SQLAlchemy
class EnvioDAO(Base):
    __tablename__ = 'envio'
    
    id_envio = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey('pedido.id_pedido'), nullable=False, unique=True)
    direccion_envio = Column(String(255), nullable=False)
    ciudad_envio = Column(String(100), nullable=False)  # Cambiado a ciudad_envio
    pais_envio = Column(String(100), nullable=False)    # Cambiado a pais_envio
    estado_envio = Column(String(50), default='PREPARACION')
    fecha_envio = Column(DateTime)
    fecha_entrega = Column(DateTime)
    empresa_transporte = Column(String(100))  # Cambiado a empresa_transporte
    numero_guia = Column(String(100))
    
    # Relación
    pedido = relationship("PedidoDAO", back_populates="envio")

# DTOs
class EnvioDTO(BaseModel):
    id_envio: int
    id_pedido: int
    direccion_envio: str
    ciudad_envio: str  # Cambiado
    pais_envio: str    # Cambiado
    estado_envio: str
    fecha_envio: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    empresa_transporte: Optional[str] = None  # Cambiado
    numero_guia: Optional[str] = None
    
    class Config:
        from_attributes = True

class EnvioCreateDTO(BaseModel):
    id_pedido: int
    direccion_envio: str
    ciudad_envio: str  # Cambiado
    pais_envio: str    # Cambiado
    estado_envio: str = 'PREPARACION'
    fecha_envio: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    empresa_transporte: Optional[str] = None  # Cambiado
    numero_guia: Optional[str] = None
    
    class Config:
        from_attributes = True