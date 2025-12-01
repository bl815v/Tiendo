from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from data.database import Base

class CategoriaDTO(BaseModel):
    id_categoria: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class CategoriaDAO(Base):
    __tablename__ = "categoria"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    
    productos = relationship("ProductoDAO", back_populates="categoria")
