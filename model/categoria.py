from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from data.database import Base
from pydantic import BaseModel
from typing import Optional, List

# Modelo SQLAlchemy
class CategoriaDAO(Base):
    __tablename__ = 'categoria'  # Cambiado de 'categorias' a 'categoria'
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    
    # Relaciones
    productos = relationship("ProductoDAO", back_populates="categoria")

# DTOs
class CategoriaDTO(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True

class CategoriaCreateDTO(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True