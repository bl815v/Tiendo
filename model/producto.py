from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from data.database import Base

class ProductoDTO(BaseModel):
    id_producto: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    id_categoria: int
    imagen: Optional[str] = None

    class Config:
        from_attributes = True

class ProductoDAO(Base):
    __tablename__ = "producto"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    id_categoria = Column(Integer, ForeignKey('categoria.id_categoria'), nullable=False)
    imagen = Column(Text)
    
    categoria = relationship("CategoriaDAO", back_populates="productos")
    detalle_carrito = relationship("DetalleCarritoDAO", back_populates="producto")
    detalle_pedido = relationship("DetallePedidoDAO", back_populates="producto")
