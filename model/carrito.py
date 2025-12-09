"""SQLAlchemy DAOs and Pydantic DTOs for shopping cart management in an e-commerce application.

Define SQLAlchemy Data Access Objects (DAOs) and Pydantic Data Transfer Objects (DTOs) for managing
shopping carts and their details in an e-commerce application.

Classes
-------
CarritoDAO
    SQLAlchemy model for the 'carrito' table, representing a shopping cart.
    Includes relationships to ClienteDAO and DetalleCarritoDAO.
DetalleCarritoDAO
    SQLAlchemy model for the 'detalle_carrito' table, representing individual items in a cart.
    Includes relationships to CarritoDAO and ProductoDAO.
DetalleCarritoDTO
    Pydantic DTO for transferring 'detalle_carrito' data.
DetalleCarritoCreateDTO
    Pydantic DTO for creating new 'detalle_carrito' entries.
CarritoDTO
    Pydantic DTO for transferring 'carrito' data, including its details.
CarritoCreateDTO
    Pydantic DTO for creating new 'carrito' entries, including their details.

Dependencies
------------
- datetime
- typing (List, Optional)
- pydantic.BaseModel
- sqlalchemy (Column, DateTime, Float, ForeignKey, Integer)
- sqlalchemy.orm.relationship
- sqlalchemy.sql.func
- data.database.Base

"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from data.database import Base


class CarritoDAO(Base):
	"""Data Access Object for the 'carrito' (shopping cart) table.

	Attributes:
		id_carrito (int): Primary key identifier for the shopping cart.
		id_cliente (int): Foreign key referencing the cliente table. Required.
		fecha_creacion (datetime): Timestamp of when the shopping cart was created.
			Defaults to the current date and time.
		activo (int): Status flag indicating if the shopping cart is active. Defaults to 1.

	Relationships:
		cliente (ClienteDAO): Relationship to the ClienteDAO object representing the customer
			who owns this shopping cart.
		detalles (list[DetalleCarritoDAO]): One-to-many relationship to DetalleCarritoDAO objects
			representing the items in this shopping cart.

	"""

	__tablename__ = 'carrito'

	id_carrito = Column(Integer, primary_key=True, index=True)
	id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
	fecha_creacion = Column(DateTime, default=func.now())
	activo = Column(Integer, default=1)

	cliente = relationship('ClienteDAO', back_populates='carritos')
	detalles = relationship('DetalleCarritoDAO', back_populates='carrito')


class DetalleCarritoDAO(Base):
	"""Data Access Object representing a shopping cart line item in the database.

	This class maps to the 'detalle_carrito' table and manages the details of products
	added to a shopping cart.

	Attributes:
		id_detalle (int): Primary key identifier for the cart detail record.
		id_carrito (int): Foreign key reference to the associated shopping cart (carrito table).
		id_producto (int): Foreign key reference to the associated product (producto table).
		cantidad (int): Quantity of the product in the cart. Defaults to 1.
		precio_unitario (float): Unit price of the product at the time it was added to the cart.
		carrito (CarritoDAO): Relationship to the parent CarritoDAO object.
		producto (ProductoDAO): Relationship to the associated ProductoDAO object.

	Relationships:
		- carrito: Back-populated relationship with CarritoDAO for accessing parent cart
		information.
		- producto: Back-populated relationship with ProductoDAO for accessing product details.

	"""

	__tablename__ = 'detalle_carrito'

	id_detalle = Column(Integer, primary_key=True, index=True)
	id_carrito = Column(Integer, ForeignKey('carrito.id_carrito'), nullable=False)
	id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
	cantidad = Column(Integer, nullable=False, default=1)
	precio_unitario = Column(Float, nullable=False)

	carrito = relationship('CarritoDAO', back_populates='detalles')
	producto = relationship('ProductoDAO', back_populates='detalles_carrito')


class DetalleCarritoDTO(BaseModel):
	"""Data Transfer Object (DTO) for shopping cart items.

	Represents a single item in a shopping cart with its associated details.

	Attributes:
		id_detalle (int): Unique identifier for the cart item detail.
		id_carrito (int): Foreign key reference to the shopping cart.
		id_producto (int): Foreign key reference to the product.
		cantidad (int): Quantity of the product in the cart.
		precio_unitario (float): Unit price of the product at the time of adding to cart.

	"""

	id_detalle: int
	id_carrito: int
	id_producto: int
	cantidad: int
	precio_unitario: float

	class Config:
		"""Pydantic configuration for DTO."""

		from_attributes = True


class DetalleCarritoCreateDTO(BaseModel):
	"""Data Transfer Object for creating shopping cart items.

	This DTO is used to transfer data when adding or creating new items in a shopping cart.
	It validates and serializes the required information for a cart item.

	Attributes:
		id_producto (int): The unique identifier of the product being added to the cart.
		cantidad (int): The quantity of the product to add to the cart.
		precio_unitario (float): The unit price of the product at the time of addition.

	"""

	id_producto: int
	cantidad: int
	precio_unitario: float

	class Config:
		"""Pydantic configuration for CarritoCreateDTO."""

		from_attributes = True


class CarritoDTO(BaseModel):
	"""Carrito (Shopping Cart) Data Transfer Object.

	A Pydantic model representing a shopping cart entity with its associated details.

	Attributes:
		id_carrito (int): Unique identifier for the shopping cart.
		id_cliente (int): Unique identifier of the client who owns the cart.
		fecha_creacion (datetime): Timestamp indicating when the cart was created.
		activo (int): Status flag indicating whether the cart is active (1) or inactive (0).
		detalles (List[DetalleCarritoDTO]): List of cart line items/details. Defaults to an empty
		list.
	Config:
		from_attributes (bool): Enables ORM mode to populate the model from ORM objects using their
		attributes.

	"""

	id_carrito: int
	id_cliente: int
	fecha_creacion: datetime
	activo: int
	detalles: List[DetalleCarritoDTO] = []

	class Config:
		"""Pydantic configuration for CarritoCreateDTO."""

		from_attributes = True


class CarritoCreateDTO(BaseModel):
	"""Data Transfer Object for creating a shopping cart.

	Attributes:
		id_cliente (int): The ID of the client who owns the cart.
		fecha_creacion (Optional[datetime]): The creation date and time of the cart.
			Defaults to None if not provided.
		activo (int): Status flag indicating if the cart is active (1) or inactive (0).
			Defaults to 1 (active).
		detalles (List[DetalleCarritoCreateDTO]): List of cart item details.
			Defaults to an empty list if not provided.

	"""

	id_cliente: int
	fecha_creacion: Optional[datetime] = None
	activo: int = 1
	detalles: List[DetalleCarritoCreateDTO] = []

	class Config:
		"""Pydantic configuration for CarritoCreateDTO."""

		from_attributes = True
