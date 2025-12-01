from typing import Optional, List
import enum
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from data.database import Base


class EstadoPedido(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    enviado = "enviado"
    entregado = "entregado"
    cancelado = "cancelado"


class DetallePedidoDTO(BaseModel):
    id_detalle_pedido: Optional[int] = None
    id_pedido: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: Optional[float] = None

    class Config:
        from_attributes = True


class PedidoDTO(BaseModel):
    id_pedido: Optional[int] = None
    id_cliente: int
    fecha_pedido: Optional[datetime] = None
    total: float
    estado: EstadoPedido = EstadoPedido.pendiente
    detalles: List[DetallePedidoDTO] = []

    class Config:
        from_attributes = True


class DetallePedidoDAO(Base):
    __tablename__ = "detalle_pedido"

    id_detalle_pedido = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2))

    pedido = relationship("PedidoDAO", back_populates="detalles")
    producto = relationship("ProductoDAO", back_populates="detalle_pedido")


class PedidoDAO(Base):
    __tablename__ = "pedido"

    id_pedido = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.now(timezone.utc))
    total = Column(Numeric(12, 2), nullable=False)
    estado = Column(
        SQLEnum(
            "pendiente",
            "pagado",
            "enviado",
            "entregado",
            "cancelado",
            name="estado_pedido",
        ),
        default="pendiente",
    )

    cliente = relationship("ClienteDAO", back_populates="pedidos")
    detalles = relationship("DetallePedidoDAO", back_populates="pedido")
    pago = relationship("PagoDAO", back_populates="pedido", uselist=False)
    envio = relationship("EnvioDAO", back_populates="pedido", uselist=False)

    @property
    def estado_enum(self) -> EstadoPedido:
        return EstadoPedido(self.estado)

    @estado_enum.setter
    def estado_enum(self, value: EstadoPedido):
        self.estado = value.value
