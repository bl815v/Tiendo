"""Product model module for the Tiendo application.

This module defines the data models for product management, including:
- ProductoDAO: SQLAlchemy ORM model representing a product in the database
- ProductoDTO: Pydantic model for transferring product data in API responses
- ProductoCreateDTO: Pydantic model for creating new products via API requests
The module handles the relationship between products and categories, order details,
and shopping cart items.

"""

from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import Base


class ProductoDAO(Base):
	"""A Data Access Object class representing a product in the database.

	Attributes:
	    id_producto (int): Unique identifier for the product. Primary key.
	    nombre (str): Name of the product (max 200 characters). Required.
	    descripcion (str): Detailed description of the product.
	    precio (float): Price of the product. Required.
	    imagen (str): URL or path to the product image (max 500 characters).
	    id_categoria (int): Foreign key referencing the category of the product.
	    stock (int): Available quantity of the product in stock. Defaults to 0.
	    categoria (CategoriaDAO): Relationship to the associated category.
	    detalles_pedido (list[DetallePedidoDAO]): Relationship to order details containing this
	    product.
	    detalles_carrito (list[DetalleCarritoDAO]): Relationship to shopping cart details containing
	    this product.

	Inherits from:
	    Base: SQLAlchemy declarative base for ORM mapping.

	"""

	__tablename__ = 'producto'

	id_producto = Column(Integer, primary_key=True, index=True)
	nombre = Column(String(200), nullable=False)
	descripcion = Column(Text)
	precio = Column(Float, nullable=False)
	imagen = Column(String(500))
	id_categoria = Column(Integer, ForeignKey('categoria.id_categoria'))
	stock = Column(Integer, default=0)

	categoria = relationship('CategoriaDAO', back_populates='productos')
	detalles_pedido = relationship('DetallePedidoDAO', back_populates='producto')
	detalles_carrito = relationship('DetalleCarritoDAO', back_populates='producto')


class ProductoDTO(BaseModel):
	"""Data Transfer Object for Product.

	This DTO is used to transfer product information between API endpoints
	and the application layer.

	Attributes:
	    id_producto (int): Unique identifier for the product.
	    nombre (str): Name of the product.
	    descripcion (Optional[str]): Detailed description of the product. Defaults to None.
	    precio (float): Price of the product.
	    imagen (Optional[str]): URL or path to the product image. Defaults to None.
	    id_categoria (Optional[int]): Identifier of the product category. Defaults to None.
	    stock (int): Available quantity in stock. Defaults to 0.

	"""

	id_producto: int
	nombre: str
	descripcion: Optional[str] = None
	precio: float
	imagen: Optional[str] = None
	id_categoria: Optional[int] = None
	stock: int = 0

	class Config:
		"""Pydantic configuration for ProductoDTO."""

		from_attributes = True


class ProductoCreateDTO(BaseModel):
	"""Data Transfer Object for creating a new product.

	Attributes:
	    nombre (str): The name of the product. Required.
	    descripcion (Optional[str]): A detailed description of the product. Defaults to None.
	    precio (float): The price of the product. Required.
	    imagen (Optional[str]): URL or path to the product image. Defaults to None.
	    id_categoria (Optional[int]): The category ID the product belongs to. Defaults to None.
	    stock (int): The initial stock quantity of the product. Defaults to 0.

	"""

	nombre: str
	descripcion: Optional[str] = None
	precio: float
	imagen: Optional[str] = None
	id_categoria: Optional[int] = None
	stock: int = 0

	class Config:
		"""Pydantic configuration for ProductoCreateDTO."""

		from_attributes = True
