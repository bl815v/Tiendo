"""Module for Categoria (Category) data models and database interactions.

This module defines the data access object (DAO), data transfer objects (DTOs),
and related models for managing product categories in the application. It provides
the necessary ORM mappings and Pydantic schemas for category operations including
creation, retrieval, and data validation.
Classes:
    CategoriaDAO: SQLAlchemy ORM model representing the 'categoria' database table.
    CategoriaDTO: Pydantic model for transferring complete category data including ID.
    CategoriaCreateDTO: Pydantic model for creating new categories without requiring an ID.

"""

from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import Base


class CategoriaDAO(Base):
	"""Data Access Object for the Categoria (Category) entity.

	This class represents the 'categoria' table in the database and provides
	an ORM mapping for category records. It defines the structure and relationships
	for storing product categories.

	Attributes:
	    id_categoria (int): Primary key identifier for the category, auto-indexed.
	    nombre (str): The name of the category, required field with max length of 100 characters.
	    descripcion (str): Optional detailed description of the category.
	    productos (relationship): One-to-many relationship with ProductoDAO objects,
	                             establishing the link between categories and products.

	"""

	__tablename__ = 'categoria'

	id_categoria = Column(Integer, primary_key=True, index=True)
	nombre = Column(String(100), nullable=False)
	descripcion = Column(Text)

	productos = relationship('ProductoDAO', back_populates='categoria')


class CategoriaDTO(BaseModel):
	"""Data Transfer Object for Categoria (Category).

	This DTO represents a category with basic information including identifier,
	name, and optional description. It is configured to work seamlessly with
	SQLAlchemy ORM models through attribute mapping.

	Attributes:
	    id_categoria (int): The unique identifier for the category.
	    nombre (str): The name of the category.
	    descripcion (Optional[str]): A detailed description of the category. Defaults to None.

	"""

	id_categoria: int
	nombre: str
	descripcion: Optional[str] = None

	class Config:
		"""Pydantic configuration for CategoriaDTO."""

		from_attributes = True


class CategoriaCreateDTO(BaseModel):
	"""Data Transfer Object for creating a new Categoria.

	Attributes:
	    nombre (str): The name of the category. Required field.
	    descripcion (Optional[str]): A detailed description of the category. Optional, defaults to
	            None.

	Config:
	    from_attributes (bool): Enables population of the model from ORM objects by attribute names.

	"""

	nombre: str
	descripcion: Optional[str] = None

	class Config:
		"""Pydantic configuration for CategoriaCreateDTO."""

		from_attributes = True
		from_attributes = True
