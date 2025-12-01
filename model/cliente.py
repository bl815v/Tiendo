from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from data.database import Base

class ClienteDTO(BaseModel):
    id_cliente: Optional[int] = None
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str] = None
    direccion: str
    ciudad: Optional[str] = None
    pais: Optional[str] = None

    class Config:
        from_attributes = True

class ClienteDAO(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20))
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(100))
    pais = Column(String(100))

    carritos = relationship("CarritoDAO", back_populates="cliente")
    pedidos = relationship("PedidoDAO", back_populates="cliente")
