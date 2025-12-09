from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from data.database import Base
from pydantic import BaseModel
from typing import Optional

# Modelo SQLAlchemy
class ProductoDAO(Base):
    __tablename__ = 'producto'
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    imagen = Column(String(500))
    id_categoria = Column(Integer, ForeignKey('categoria.id_categoria'))
    stock = Column(Integer, default=0)
    
    # Relaciones
    categoria = relationship("CategoriaDAO", back_populates="productos")
    detalles_pedido = relationship("DetallePedidoDAO", back_populates="producto")
    detalles_carrito = relationship("DetalleCarritoDAO", back_populates="producto")

# DTOs
class ProductoDTO(BaseModel):
    id_producto: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen: Optional[str] = None
    id_categoria: Optional[int] = None
    stock: int = 0
    
    class Config:
        from_attributes = True

# DTO para creación (sin ID)
class ProductoCreateDTO(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen: Optional[str] = None
    id_categoria: Optional[int] = None
    stock: int = 0
    
    class Config:
        from_attributes = True