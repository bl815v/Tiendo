from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from data.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Modelo SQLAlchemy
class ClienteDAO(Base):
    __tablename__ = 'cliente'
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
    telefono = Column(String(20))
    direccion = Column(String(255))
    ciudad = Column(String(100))
    pais = Column(String(100))
    
    # Relaciones
    carritos = relationship("CarritoDAO", back_populates="cliente")
    pedidos = relationship("PedidoDAO", back_populates="cliente")

# DTOs
class ClienteCreateDTO(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    contrasena: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    
    class Config:
        from_attributes = True

class ClienteDTO(BaseModel):
    id_cliente: int
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    
    class Config:
        from_attributes = True