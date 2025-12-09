"""Define models and data transfer objects for handling payment records in the system.

Classes:
	MetodoPago (enum.Enum): Enum representing available payment methods, including credit card,
	debit card, bank transfer, cash, and PayPal.
	PagoDTO (pydantic.BaseModel): DTO for representing payment information, including payment ID,
	order ID, payment date, amount, method, and reference.
	PagoCreateDTO (pydantic.BaseModel): DTO for creating a payment record, including order ID,
	payment date, amount, method, and reference.
	PagoDAO (Base): SQLAlchemy ORM model for the 'pago' table, representing payment records with
	fields for payment ID, order ID, payment date, amount, method, reference, and relationship to
	the associated order.
	Use these classes to create, validate, and interact with payment records in the database and API
	layer.

"""

import enum
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (
	Column,
	DateTime,
	ForeignKey,
	Integer,
	Numeric,
	String,
)
from sqlalchemy import (
	Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from data.database import Base


class MetodoPago(str, enum.Enum):
	"""Enum representing the available payment methods.

	Attributes:
		tarjeta_credito: Payment via credit card.
		tarjeta_debito: Payment via debit card.
		transferencia: Payment via bank transfer.
		efectivo: Payment with cash.
		paypal: Payment via PayPal.

	"""

	tarjeta_credito = 'tarjeta_credito'
	tarjeta_debito = 'tarjeta_debito'
	transferencia = 'transferencia'
	efectivo = 'efectivo'
	paypal = 'paypal'


class PagoDTO(BaseModel):
	"""Data Transfer Object (DTO) for representing payment information.

	Attributes:
		id_pago (Optional[int]): Unique identifier for the payment.
		id_pedido (int): Identifier for the associated order.
		fecha_pago (Optional[datetime]): Date and time when the payment was made.
		monto (float): Amount paid.
		metodo (MetodoPago): Payment method used.
		referencia_pago (Optional[str]): Reference or transaction number for the payment.

	Config:
		from_attributes (bool): Enables model creation from ORM objects.

	"""

	id_pago: Optional[int] = None
	id_pedido: int
	fecha_pago: Optional[datetime] = None
	monto: float
	metodo: MetodoPago
	referencia_pago: Optional[str] = None

	class Config:
		"""Pydantic configuration for PagoDTO."""

		from_attributes = True


class PagoCreateDTO(BaseModel):
	"""Data Transfer Object (DTO) for creating a payment record.

	Attributes:
		id_pedido (int): Identifier of the associated order.
		fecha_pago (Optional[datetime]): Date and time when the payment was made. Defaults to None.
		monto (float): Amount paid.
		metodo (MetodoPago): Payment method used.
		referencia_pago (Optional[str]): Reference or transaction identifier for the payment.
		Defaults to None.

	Config:
		from_attributes (bool): Allows model initialization from attribute names.

	"""

	id_pedido: int
	fecha_pago: Optional[datetime] = None
	monto: float
	metodo: MetodoPago
	referencia_pago: Optional[str] = None

	class Config:
		"""Pydantic configuration for PagoCreateDTO."""

		from_attributes = True


class PagoDAO(Base):
	"""Data Access Object (DAO) for the 'pago' table, representing payment records.

	Attributes:
		id_pago (int): Primary key for the payment record.
		id_pedido (int): Foreign key referencing the associated order (pedido).
		fecha_pago (datetime): Timestamp of the payment, defaults to current UTC time.
		monto (Decimal): Amount paid, with precision up to 12 digits and 2 decimals.
		metodo (str): Payment method, must be one of 'tarjeta_credito', 'tarjeta_debito',
		'transferencia', 'efectivo', or 'paypal'.
		referencia_pago (str): Optional reference or transaction identifier for the payment.
		pedido (PedidoDAO): Relationship to the associated PedidoDAO object.
	Properties:
		metodo_enum (MetodoPago): Enum representation of the payment method.
	Usage:
		Use this class to interact with payment records in the database, including creating,
		querying, and updating payments.

	"""

	__tablename__ = 'pago'

	id_pago = Column(Integer, primary_key=True, index=True)
	id_pedido = Column(Integer, ForeignKey('pedido.id_pedido'), nullable=False)
	fecha_pago = Column(DateTime, default=datetime.now(timezone.utc))
	monto = Column(Numeric(12, 2), nullable=False)
	metodo = Column(
		SQLEnum(
			'tarjeta_credito',
			'tarjeta_debito',
			'transferencia',
			'efectivo',
			'paypal',
			name='metodo_pago',
		),
		nullable=False,
	)
	referencia_pago = Column(String(100))

	pedido = relationship('PedidoDAO', back_populates='pagos')

	@property
	def metodo_enum(self) -> MetodoPago:
		"""Returns the payment method as a MetodoPago enum.

		Returns:
			MetodoPago: Enum representation of the payment method.

		"""
		return MetodoPago(self.metodo)

	@metodo_enum.setter
	def metodo_enum(self, value: MetodoPago):
		self.metodo = value.value
