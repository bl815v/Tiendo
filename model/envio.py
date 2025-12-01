from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data.database import Base


class EnvioDTO(BaseModel):
    id_envio: Optional[int] = None
    id_pedido: int
    direccion_envio: str
    ciudad_envio: Optional[str] = None
    pais_envio: Optional[str] = None
    fecha_envio: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    empresa_transporte: Optional[str] = None
    numero_guia: Optional[str] = None

    class Config:
        from_attributes = True


class EnvioDAO(Base):
    __tablename__ = "envio"

    id_envio = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    direccion_envio = Column(Text, nullable=False)
    ciudad_envio = Column(String(100))
    pais_envio = Column(String(100))
    fecha_envio = Column(DateTime)
    fecha_entrega = Column(DateTime)
    empresa_transporte = Column(String(100))
    numero_guia = Column(String(100), unique=True)

    pedido = relationship("PedidoDAO", back_populates="envio")
