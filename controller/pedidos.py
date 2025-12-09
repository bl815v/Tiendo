"""Controller module for managing orders (pedidos) in the Tiendo application.

This module provides FastAPI endpoints for CRUD operations on orders and their details.
It handles the creation, retrieval, update, and deletion of orders, as well as
management of order detail lines.

Endpoints:
    POST /pedidos/ - Create a new order
    GET /pedidos/ - List all orders (paginated)
    GET /pedidos/{pedido_id} - Retrieve a specific order
    GET /pedidos/cliente/{cliente_id} - Retrieve all orders for a client
    PUT /pedidos/{pedido_id} - Update an existing order
    PATCH /pedidos/{pedido_id}/estado - Update order status
    DELETE /pedidos/{pedido_id} - Delete an order
    POST /pedidos/{pedido_id}/detalles - Add a detail line to an order
    GET /pedidos/{pedido_id}/detalles - Retrieve all details for an order

Dependencies:
    - FastAPI APIRouter for routing
    - SQLAlchemy ORM Session for database operations
    - Data models: PedidoDAO, DetallePedidoDAO for database entities
    - DTOs: PedidoCreateDTO, PedidoDTO, DetallePedidoCreateDTO, DetallePedidoDTO for data transfer
    - EstadoPedido enum for order status management
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.pedido import (
	DetallePedidoCreateDTO,
	DetallePedidoDAO,
	DetallePedidoDTO,
	EstadoPedido,
	PedidoCreateDTO,
	PedidoDAO,
	PedidoDTO,
)

router = APIRouter(prefix='/pedidos', tags=['pedidos'])


@router.post('/', response_model=PedidoDTO)
def crear_pedido(pedido: PedidoCreateDTO, db: Session = Depends(get_db)):
	"""Create a new order in the database, including its details if provided.

	Args:
	    pedido (PedidoCreateDTO): Data transfer object containing the order details to be created,
	        including optional order details.
	    db (Session): SQLAlchemy database session dependency for executing database operations.

	Returns:
	    PedidoDAO: The created order object with all fields populated, including the auto-generated
	    ID and any default database values after commit and refresh.

	Raises:
	    SQLAlchemy exceptions: May raise database-related exceptions if the commit operation fails.

	"""
	pedido_data = pedido.model_dump(exclude={'detalles'})
	pedido_data['estado'] = pedido_data['estado'].value
	db_pedido = PedidoDAO(**pedido_data)
	db.add(db_pedido)
	db.commit()
	db.refresh(db_pedido)

	if pedido.detalles:
		for detalle in pedido.detalles:
			detalle_data = detalle.model_dump()
			detalle_data['id_pedido'] = db_pedido.id_pedido
			db_detalle = DetallePedidoDAO(**detalle_data)
			db.add(db_detalle)
		db.commit()
		db.refresh(db_pedido)

	return db_pedido


@router.get('/', response_model=List[PedidoDTO])
def listar_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""
	Retrieve a paginated list of orders from the database.

	Args:
	    skip (int): Number of records to skip for pagination. Defaults to 0.
	    limit (int): Maximum number of records to return. Defaults to 100.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    list[PedidoDAO]: A list of PedidoDAO objects representing orders.

	"""
	pedidos = db.query(PedidoDAO).offset(skip).limit(limit).all()
	return pedidos


@router.get('/{pedido_id}', response_model=PedidoDTO)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
	"""Retrieve a specific order by its ID.

	Args:
		pedido_id (int): The unique identifier of the order to retrieve.
		db (Session): Database session dependency for querying the database.

	Returns:
		PedidoDAO: The order object with the specified ID.

	Raises:
		HTTPException: If the order with the given ID is not found (status code 404).

	"""
	pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
	if pedido is None:
		raise HTTPException(status_code=404, detail='Pedido no encontrado')
	return pedido


@router.get('/cliente/{cliente_id}', response_model=List[PedidoDTO])
def obtener_pedidos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
	"""
	Retrieve all orders associated with a specific client.

	Args:
	    cliente_id (int): The unique identifier of the client whose orders to retrieve.
	    db (Session): Database session dependency for executing queries.

	Returns:
	    list[PedidoDAO]: A list of PedidoDAO objects representing all orders
	                     belonging to the specified client. Returns an empty list
	                     if no orders are found.

	"""
	pedidos = db.query(PedidoDAO).filter(PedidoDAO.id_cliente == cliente_id).all()
	return pedidos


@router.put('/{pedido_id}', response_model=PedidoDTO)
def actualizar_pedido(pedido_id: int, pedido: PedidoCreateDTO, db: Session = Depends(get_db)):
	"""Update an existing order with new data.

	Args:
		pedido_id (int): The unique identifier of the order to update.
		pedido (PedidoCreateDTO): Data transfer object containing the updated order details.
		db (Session): Database session dependency for executing database operations.

	Returns:
		PedidoDAO: The updated order object with all fields refreshed from the database.

	Raises:
		HTTPException: If the order with the given ID is not found (status code 404).

	"""
	db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
	if db_pedido is None:
		raise HTTPException(status_code=404, detail='Pedido no encontrado')

	update_data = pedido.model_dump(exclude={'detalles'})
	update_data['estado'] = update_data['estado'].value

	for key, value in update_data.items():
		setattr(db_pedido, key, value)

	db.commit()
	db.refresh(db_pedido)
	return db_pedido


@router.patch('/{pedido_id}/estado')
def actualizar_estado_pedido(pedido_id: int, estado: EstadoPedido, db: Session = Depends(get_db)):
	"""Update the status of an existing order.

	Args:
		pedido_id (int): The unique identifier of the order to update.
		estado (EstadoPedido): The new status for the order.
		db (Session): Database session dependency for executing database operations.

	Returns:
		dict: A dictionary with a success message containing the updated status.

	Raises:
		HTTPException: If the order with the given ID is not found (status code 404).

	"""
	db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
	if db_pedido is None:
		raise HTTPException(status_code=404, detail='Pedido no encontrado')

	db_pedido.estado_enum = estado
	db.commit()
	return {'message': f'Estado del pedido actualizado a {estado.value}'}


@router.delete('/{pedido_id}')
def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
	"""Delete an existing order from the database.

	Args:
		pedido_id (int): The unique identifier of the order to delete.
		db (Session): Database session dependency for executing database operations.

	Returns:
		dict: A dictionary with a success message confirming the order was deleted.

	Raises:
		HTTPException: If the order with the given ID is not found (status code 404).

	"""
	db_pedido = db.query(PedidoDAO).filter(PedidoDAO.id_pedido == pedido_id).first()
	if db_pedido is None:
		raise HTTPException(status_code=404, detail='Pedido no encontrado')

	db.delete(db_pedido)
	db.commit()
	return {'message': 'Pedido eliminado'}


@router.post('/{pedido_id}/detalles', response_model=DetallePedidoDTO)
def agregar_detalle_pedido(
	pedido_id: int,
	detalle: DetallePedidoCreateDTO,
	db: Session = Depends(get_db),
):
	"""Add a new detail line to an existing order.

	Args:
		pedido_id (int): The unique identifier of the order to add the detail to.
		detalle (DetallePedidoCreateDTO): Data transfer object containing the detail information to
		be added.
		db (Session): Database session dependency for executing database operations.

	Returns:
		DetallePedidoDTO: The created order detail object with all fields populated, including the
		auto-generated ID.

	"""
	detalle_data = detalle.model_dump()
	detalle_data['id_pedido'] = pedido_id
	db_detalle = DetallePedidoDAO(**detalle_data)
	db.add(db_detalle)
	db.commit()
	db.refresh(db_detalle)
	return db_detalle


@router.get('/{pedido_id}/detalles', response_model=List[DetallePedidoDTO])
def listar_detalles_pedido(pedido_id: int, db: Session = Depends(get_db)):
	"""Retrieve all details for a specific order.

	Args:
		pedido_id (int): The unique identifier of the order whose details to retrieve.
		db (Session): Database session dependency for querying the database.

	Returns:
		list[DetallePedidoDAO]: A list of DetallePedidoDAO objects representing all details
								for the specified order.

	"""
	detalles = db.query(DetallePedidoDAO).filter(DetallePedidoDAO.id_pedido == pedido_id).all()
	return detalles
