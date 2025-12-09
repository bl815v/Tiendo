"""Payment controller module for managing payment operations.

This module provides REST API endpoints for CRUD operations on payment records.
It handles creation, retrieval, updating, and deletion of payment information
associated with orders in the Tiendo system.
Endpoints:
	POST /pagos/ - Create a new payment record
	GET /pagos/ - Retrieve paginated list of all payments
	GET /pagos/{pago_id} - Retrieve a specific payment by ID
	GET /pagos/pedido/{pedido_id} - Retrieve all payments for a specific order
	PUT /pagos/{pago_id} - Update an existing payment record
	DELETE /pagos/{pago_id} - Delete a payment record
Dependencies:
	- FastAPI APIRouter for endpoint definitions
	- SQLAlchemy Session for database operations
	- PagoDAO: Data access object for payment records
	- PagoDTO: Data transfer object for payment responses
	- PagoCreateDTO: Data transfer object for payment creation/updates
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.pago import PagoCreateDTO, PagoDAO, PagoDTO

router = APIRouter(prefix='/pagos', tags=['pagos'])


@router.post('/', response_model=PagoDTO)
def crear_pago(pago: PagoCreateDTO, db: Session = Depends(get_db)):
	"""Create a new payment record in the database.

	Args:
	    pago (PagoCreateDTO): Data transfer object containing payment information to be created.
	    db (Session): Database session dependency for executing database operations.

	Returns:
	    PagoDAO: The created payment object with generated database ID and timestamp information.

	Raises:
	    SQLAlchemyError: If database commit fails due to integrity or constraint violations.

	"""
	pago_data = pago.model_dump()
	pago_data['metodo'] = pago_data['metodo'].value
	db_pago = PagoDAO(**pago_data)
	db.add(db_pago)
	db.commit()
	db.refresh(db_pago)
	return db_pago


@router.get('/', response_model=List[PagoDTO])
def listar_pagos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""Retrieve a paginated list of payments from the database.

	Args:
	    skip (int, optional): Number of records to skip for pagination. Defaults to 0.
	    limit (int, optional): Maximum number of records to retrieve. Defaults to 100.
	    db (Session, optional): SQLAlchemy database session dependency. Defaults to Depends(get_db).

	Returns:
	    list[PagoDAO]: A list of payment objects from the database.

	"""
	pagos = db.query(PagoDAO).offset(skip).limit(limit).all()
	return pagos


@router.get('/{pago_id}', response_model=PagoDTO)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
	"""Retrieve a payment record by its ID.

	Args:
	    pago_id (int): The unique identifier of the payment to retrieve.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    PagoDAO: The payment object if found.

	Raises:
	    HTTPException: 404 error if the payment with the given ID is not found.

	"""
	pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
	if pago is None:
		raise HTTPException(status_code=404, detail='Pago no encontrado')
	return pago


@router.get('/pedido/{pedido_id}', response_model=List[PagoDTO])
def obtener_pagos_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
	"""Retrieve all payments associated with a specific order.

	Args:
	    pedido_id (int): The ID of the order for which to retrieve payments.
	    db (Session): The database session dependency. Defaults to get_db().

	Returns:
	    list[PagoDAO]: A list of payment objects associated with the given order ID.
	                   Returns an empty list if no payments are found.

	"""
	pagos = db.query(PagoDAO).filter(PagoDAO.id_pedido == pedido_id).all()
	return pagos


@router.put('/{pago_id}', response_model=PagoDTO)
def actualizar_pago(pago_id: int, pago: PagoCreateDTO, db: Session = Depends(get_db)):
	"""Update an existing payment record in the database.

	Args:
		pago_id (int): The unique identifier of the payment to update.
		pago (PagoCreateDTO): Data transfer object containing updated payment information.
		db (Session): Database session dependency for executing database operations.

	Returns:
		PagoDAO: The updated payment object.

	Raises:
		HTTPException: 404 error if the payment with the given ID is not found.

	"""
	db_pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
	if db_pago is None:
		raise HTTPException(status_code=404, detail='Pago no encontrado')

	update_data = pago.model_dump()
	update_data['metodo'] = update_data['metodo'].value

	for key, value in update_data.items():
		setattr(db_pago, key, value)

	db.commit()
	db.refresh(db_pago)
	return db_pago


@router.delete('/{pago_id}')
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
	"""Delete a payment record from the database.

	Args:
		pago_id (int): The unique identifier of the payment to delete.
		db (Session): Database session dependency for executing database operations.

	Returns:
		dict: A dictionary with a success message confirming the deletion.

	Raises:
		HTTPException: 404 error if the payment with the given ID is not found.

	"""
	db_pago = db.query(PagoDAO).filter(PagoDAO.id_pago == pago_id).first()
	if db_pago is None:
		raise HTTPException(status_code=404, detail='Pago no encontrado')

	db.delete(db_pago)
	db.commit()
	return {'message': 'Pago eliminado'}
