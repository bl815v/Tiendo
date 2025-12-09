"""Define the data models and DTOs for the Cliente (Customer) entity in the Tiendo system.

Classes:
    ClienteDAO: SQLAlchemy ORM model representing the 'cliente' table in the database.
        Includes personal and contact information fields, and relationships to shopping carts and
		orders.
    ClienteCreateDTO: Pydantic model for validating and structuring data when creating a new
	customer.
        Enforces required fields and allows optional fields for additional customer information.
    ClienteDTO: Pydantic model for representing a customer, typically used for data transfer.
        Includes all customer attributes except password, and supports ORM mode for easy conversion.
Usage:
    - Use ClienteDAO for database operations and persistence.
    - Use ClienteCreateDTO for validating incoming data when creating a new customer.
    - Use ClienteDTO for returning customer data in API responses.
    All models are designed to work seamlessly with SQLAlchemy and Pydantic for robust data
	validation and ORM integration.

"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from data.database import Base


class ClienteDAO(Base):
	"""Data Access Object for Cliente (Customer) entity.

	Represents a customer in the Tiendo system with personal information and contact details.

	Attributes:
	    id_cliente (int): Primary key identifier for the customer, automatically indexed.
	    nombre (str): Customer's first name, required field (max 100 characters).
	    apellido (str): Customer's last name, required field (max 100 characters).
	    correo (str): Customer's email address, required and unique field (max 150 characters).
	                  Used as a secondary index for quick lookups.
	    contrasena (str): Customer's hashed password, required field (max 255 characters).
	    telefono (str): Customer's phone number, optional field (max 20 characters).
	    direccion (str): Customer's street address, optional field (max 255 characters).
	    ciudad (str): Customer's city, optional field (max 100 characters).
	    pais (str): Customer's country, optional field (max 100 characters).

	Relationships:
	    carritos: One-to-many relationship with CarritoDAO (shopping carts).
	    pedidos: One-to-many relationship with PedidoDAO (orders).

	Note:
	    This class represents the 'cliente' table in the database and serves as the
	    ORM model for customer data persistence and retrieval operations.

	"""

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

	carritos = relationship('CarritoDAO', back_populates='cliente')
	pedidos = relationship('PedidoDAO', back_populates='cliente')


class ClienteCreateDTO(BaseModel):
	"""Data Transfer Object for creating a new Cliente (Customer).

	This DTO is used to validate and structure the incoming data when creating a new customer
	in the system. It enforces required fields and allows optional fields for additional
	customer information.

	Attributes:
	    nombre (str): The customer's first name. Required.
	    apellido (str): The customer's last name. Required.
	    correo (EmailStr): The customer's email address. Required and must be a valid email format.
	    contrasena (str): The customer's password. Required.
	    telefono (Optional[str]): The customer's phone number. Optional.
	    direccion (Optional[str]): The customer's street address. Optional.
	    ciudad (Optional[str]): The customer's city. Optional.
	    pais (Optional[str]): The customer's country. Optional.

	"""

	nombre: str
	apellido: str
	correo: EmailStr
	contrasena: str
	telefono: Optional[str] = None
	direccion: Optional[str] = None
	ciudad: Optional[str] = None
	pais: Optional[str] = None

	class Config:
		"""Pydantic configuration for enabling ORM mode."""

		from_attributes = True


class ClienteDTO(BaseModel):
	"""Data Transfer Object (DTO) for representing a client.

	Attributes:
	    id_cliente (int): Unique identifier for the client.
	    nombre (str): First name of the client.
	    apellido (str): Last name of the client.
	    correo (EmailStr): Email address of the client.
	    telefono (Optional[str]): Phone number of the client (optional).
	    direccion (Optional[str]): Address of the client (optional).
	    ciudad (Optional[str]): City of the client (optional).
	    pais (Optional[str]): Country of the client (optional).

	Config:
	    from_attributes (bool): Enables model creation from ORM objects.

	"""

	id_cliente: int
	nombre: str
	apellido: str
	correo: EmailStr
	telefono: Optional[str] = None
	direccion: Optional[str] = None
	ciudad: Optional[str] = None
	pais: Optional[str] = None

	class Config:
		"""Pydantic configuration for enabling ORM mode."""

		from_attributes = True
