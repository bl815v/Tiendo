"""Define the data models and DTOs for managing shipping (envío) information in the system.

Classes:
    EnvioDAO: SQLAlchemy ORM model representing the shipping details associated with an order,
	including address, city, country, status, shipment and delivery dates, transport company, and
	tracking number.
    EnvioDTO: Pydantic DTO for transferring shipment details, supporting ORM object conversion.
    EnvioCreateDTO: Pydantic DTO for creating new shipment records, supporting ORM object
	conversion.

Each class provides attributes relevant to shipping management and supports integration with bothS
database and API layers.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from data.database import Base


class EnvioDAO(Base):
	"""EnvioDAO model represents the shipping information associated with an order.

	Attributes:
	    id_envio (int): Primary key for the shipping record.
	    id_pedido (int): Foreign key referencing the associated order (PedidoDAO), unique per
		shipping.
	    direccion_envio (str): Shipping address.
	    ciudad_envio (str): City for the shipping address.
	    pais_envio (str): Country for the shipping address.
	    estado_envio (str): Current status of the shipment (default: 'PREPARACION').
	    fecha_envio (datetime): Date and time when the shipment was sent.
	    fecha_entrega (datetime): Date and time when the shipment was delivered.
	    empresa_transporte (str): Name of the transport company handling the shipment.
	    numero_guia (str): Tracking number for the shipment.
	    pedido (PedidoDAO): Relationship to the associated order.

	"""

	__tablename__ = 'envio'

	id_envio = Column(Integer, primary_key=True, index=True)
	id_pedido = Column(Integer, ForeignKey('pedido.id_pedido'), nullable=False, unique=True)
	direccion_envio = Column(String(255), nullable=False)
	ciudad_envio = Column(String(100), nullable=False)
	pais_envio = Column(String(100), nullable=False)
	estado_envio = Column(String(50), default='PREPARACION')
	fecha_envio = Column(DateTime)
	fecha_entrega = Column(DateTime)
	empresa_transporte = Column(String(100))
	numero_guia = Column(String(100))

	pedido = relationship('PedidoDAO', back_populates='envio')


class EnvioDTO(BaseModel):
	"""EnvioDTO is a data transfer object representing the details of a shipment.

	Attributes:
	id_envio (int): Unique identifier for the shipment.
	id_pedido (int): Identifier for the associated order.
	direccion_envio (str): Shipping address.
	ciudad_envio (str): City for the shipment.
	pais_envio (str): Country for the shipment.
	estado_envio (str): Current status of the shipment.
	fecha_envio (Optional[datetime]): Date when the shipment was sent.
	fecha_entrega (Optional[datetime]): Date when the shipment was delivered.
	empresa_transporte (Optional[str]): Name of the transport company.
	numero_guia (Optional[str]): Tracking number for the shipment.

	Config:
	from_attributes (bool): Enables model creation from ORM objects.

	"""

	id_envio: int
	id_pedido: int
	direccion_envio: str
	ciudad_envio: str
	pais_envio: str
	estado_envio: str
	fecha_envio: Optional[datetime] = None
	fecha_entrega: Optional[datetime] = None
	empresa_transporte: Optional[str] = None
	numero_guia: Optional[str] = None

	class Config:
		"""Configuration for Pydantic model creation from ORM objects."""

		from_attributes = True


class EnvioCreateDTO(BaseModel):
	"""Data Transfer Object (DTO) for creating a new shipping (envío) record.

	Attributes:
	    id_pedido (int): Identifier of the associated order.
	    direccion_envio (str): Shipping address.
	    ciudad_envio (str): City for shipping.
	    pais_envio (str): Country for shipping.
	    estado_envio (str, optional): Current shipping status. Defaults to 'PREPARACION'.
	    fecha_envio (datetime, optional): Date when the shipment was sent.
	    fecha_entrega (datetime, optional): Date when the shipment was delivered.
	    empresa_transporte (str, optional): Name of the transport company.
	    numero_guia (str, optional): Tracking number for the shipment.

	Config:
	    from_attributes (bool): Allows model initialization from attributes.

	"""

	id_pedido: int
	direccion_envio: str
	ciudad_envio: str
	pais_envio: str
	estado_envio: str = 'PREPARACION'
	fecha_envio: Optional[datetime] = None
	fecha_entrega: Optional[datetime] = None
	empresa_transporte: Optional[str] = None
	numero_guia: Optional[str] = None

	class Config:
		"""Configuration for Pydantic model creation from attributes."""

		from_attributes = True
