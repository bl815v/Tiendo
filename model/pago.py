from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import (
	Column,
	Integer,
	Numeric,
	DateTime,
	String,
	ForeignKey,
	Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from data.database import Base
import enum


class MetodoPago(str, enum.Enum):
	tarjeta_credito = 'tarjeta_credito'
	tarjeta_debito = 'tarjeta_debito'
	transferencia = 'transferencia'
	efectivo = 'efectivo'
	paypal = 'paypal'


class PagoDTO(BaseModel):
	id_pago: Optional[int] = None
	id_pedido: int
	fecha_pago: Optional[datetime] = None
	monto: float
	metodo: MetodoPago
	referencia_pago: Optional[str] = None

	class Config:
		from_attributes = True


class PagoCreateDTO(BaseModel):  # Agregar este DTO
	id_pedido: int
	fecha_pago: Optional[datetime] = None
	monto: float
	metodo: MetodoPago
	referencia_pago: Optional[str] = None

	class Config:
		from_attributes = True


class PagoDAO(Base):
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
		return MetodoPago(self.metodo)

	@metodo_enum.setter
	def metodo_enum(self, value: MetodoPago):
		self.metodo = value.value
