"""Module for managing orders (Pedidos) and their details in the Tiendo system.

This module provides data models and transfer objects for handling orders, including:
- Order state management through the EstadoPedido enum
- SQLAlchemy ORM models (DAO) for database operations
- Pydantic models (DTO) for API data transfer
The module defines relationships between orders, customers, order details, shipments,
and payments, with proper cascade delete handling and foreign key constraints.

"""

import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from data.database import Base


class EstadoPedido(str, enum.Enum):
	"""Enum representing the possible states of an order (Pedido).

	Attributes:
	    PENDIENTE: The order is pending and has not been processed yet.
	    PROCESANDO: The order is currently being processed.
	    ENVIADO: The order has been shipped.
	    ENTREGADO: The order has been delivered to the customer.
	    CANCELADO: The order has been cancelled.

	"""

	PENDIENTE = 'PENDIENTE'
	PROCESANDO = 'PROCESANDO'
	ENVIADO = 'ENVIADO'
	ENTREGADO = 'ENTREGADO'
	CANCELADO = 'CANCELADO'


class PedidoDAO(Base):
	"""PedidoDAO is a SQLAlchemy ORM model representing a 'pedido' (order) in the database.

	Attributes:
	    id_pedido (int): Primary key identifier for the order.
	    id_cliente (int): Foreign key referencing the associated client.
	    fecha_pedido (datetime): Timestamp of when the order was placed. Defaults to current time.
	    total (float): Total amount for the order.
	    estado (str): Current status of the order. Defaults to 'PENDIENTE'.

	Relationships:
	    cliente (ClienteDAO): The client associated with the order.
	    detalles (list[DetallePedidoDAO]): List of order detail items.
	    envio (EnvioDAO): Shipping information for the order (one-to-one).
	    pagos (list[PagoDAO]): List of payments associated with the order.

	"""

	__tablename__ = 'pedido'

	id_pedido = Column(Integer, primary_key=True, index=True)
	id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
	fecha_pedido = Column(DateTime, default=func.now())
	total = Column(Float, nullable=False)
	estado = Column(String(50), default=EstadoPedido.PENDIENTE.value)

	cliente = relationship('ClienteDAO', back_populates='pedidos')
	detalles = relationship(
		'DetallePedidoDAO', back_populates='pedido', cascade='all, delete-orphan'
	)
	envio = relationship(
		'EnvioDAO', back_populates='pedido', uselist=False, cascade='all, delete-orphan'
	)
	pagos = relationship('PagoDAO', back_populates='pedido', cascade='all, delete-orphan')


class DetallePedidoDAO(Base):
	"""DetallePedidoDAO - Data Access Object for order details.

	This class represents the 'detalle_pedido' table and manages the relationship
	between orders and products, including quantity and unit price information.

	Attributes:
	    id_detalle (int): Primary key identifier for the detail record.
	    id_pedido (int): Foreign key reference to the pedido (order) table.
	    id_producto (int): Foreign key reference to the producto (product) table.
	    cantidad (int): Quantity of the product ordered.
	    precio_unitario (float): Unit price of the product at the time of order.
	    pedido (PedidoDAO): Relationship to the associated PedidoDAO object.
	    producto (ProductoDAO): Relationship to the associated ProductoDAO object.

	"""

	__tablename__ = 'detalle_pedido'

	id_detalle = Column(Integer, primary_key=True, index=True)
	id_pedido = Column(Integer, ForeignKey('pedido.id_pedido'), nullable=False)
	id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
	cantidad = Column(Integer, nullable=False)
	precio_unitario = Column(Float, nullable=False)

	pedido = relationship('PedidoDAO', back_populates='detalles')
	producto = relationship('ProductoDAO', back_populates='detalles_pedido')


class DetallePedidoDTO(BaseModel):
	"""Data Transfer Object representing the details of a purchase order line item.

	Attributes:
	    id_detalle (int): Unique identifier for the order detail record.
	    id_pedido (int): Foreign key reference to the associated purchase order.
	    id_producto (int): Foreign key reference to the product included in this order detail.
	    cantidad (int): Quantity of the product ordered.
	    precio_unitario (float): Unit price of the product at the time of the order.

	Configuration:
	    from_attributes (bool): Enables ORM mode to populate the model from ORM objects.

	"""

	id_detalle: int
	id_pedido: int
	id_producto: int
	cantidad: int
	precio_unitario: float

	class Config:
		"""Pydantic configuration for DetallePedidoDTO."""

		from_attributes = True


class DetallePedidoCreateDTO(BaseModel):
	"""Data Transfer Object for creating a new order detail.

	This DTO is used to transfer order detail information from the client
	to the server when creating a new order detail entry.

	Attributes:
	    id_producto (int): The unique identifier of the product.
	    cantidad (int): The quantity of the product ordered.
	    precio_unitario (float): The unit price of the product at the time of the order.

	"""

	id_producto: int
	cantidad: int
	precio_unitario: float

	class Config:
		"""Pydantic configuration for DetallePedidoCreateDTO."""

		from_attributes = True


class PedidoDTO(BaseModel):
	"""Data Transfer Object for Pedido (Order).

	Represents an order with its basic information including identification,
	customer reference, order date, total amount, and current status.

	Attributes:
	    id_pedido (int): Unique identifier for the order.
	    id_cliente (int): Unique identifier of the customer who placed the order.
	    fecha_pedido (datetime): Date and time when the order was created.
	    total (float): Total amount of the order.
	    estado (str): Current status of the order (e.g., 'pending', 'completed', 'cancelled').

	"""

	id_pedido: int
	id_cliente: int
	fecha_pedido: datetime
	total: float
	estado: str

	class Config:
		"""Pydantic configuration for PedidoDTO."""

		from_attributes = True


class PedidoCreateDTO(BaseModel):
	"""Data Transfer Object for creating a new order.

	This DTO is used to transfer order information from the client
	to the server when creating a new order entry.

	Attributes:
		id_cliente (int): The unique identifier of the customer placing the order.
		fecha_pedido (Optional[datetime]): Date and time when the order is created. Defaults to
		None.
		total (float): Total amount of the order.
		estado (EstadoPedido): Current status of the order. Defaults to PENDIENTE.
		detalles (List[DetallePedidoCreateDTO]): List of order detail items. Defaults to an empty
		list.

	Configuration:
		from_attributes (bool): Enables ORM mode to populate the model from ORM objects.

	"""

	id_cliente: int
	fecha_pedido: Optional[datetime] = None
	total: float
	estado: EstadoPedido = EstadoPedido.PENDIENTE
	detalles: List[DetallePedidoCreateDTO] = []

	class Config:
		"""Pydantic configuration for PedidoCreateDTO."""

		from_attributes = True
