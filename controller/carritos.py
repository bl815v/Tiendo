"""Shopping Cart Controller Module.

This module provides REST API endpoints for managing shopping carts and their details.
It includes operations for creating, retrieving, updating, and deleting shopping carts,
as well as managing cart line items (detalles).

Endpoints:
	POST /carritos/ - Create a new shopping cart
	GET /carritos/ - List all shopping carts with pagination
	GET /carritos/{carrito_id} - Retrieve a specific shopping cart
	GET /carritos/cliente/{cliente_id} - Retrieve all carts for a specific client
	PUT /carritos/{carrito_id} - Update an existing shopping cart
	DELETE /carritos/{carrito_id} - Delete a shopping cart
	POST /carritos/{carrito_id}/detalles - Add a detail item to a cart
	GET /carritos/{carrito_id}/detalles - List all details for a specific cart

Dependencies:
	- FastAPI for routing and dependency injection
	- SQLAlchemy for ORM database operations
	- Pydantic models for data validation and serialization

"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.carrito import (
	CarritoCreateDTO,
	CarritoDAO,
	CarritoDTO,
	DetalleCarritoCreateDTO,
	DetalleCarritoDAO,
	DetalleCarritoDTO,
)

router = APIRouter(prefix='/carritos', tags=['carritos'])


@router.post('/', response_model=CarritoDTO)
def crear_carrito(carrito: CarritoCreateDTO, db: Session = Depends(get_db)):
	"""Create a new shopping cart in the database.

	Args:
	    carrito (CarritoCreateDTO): Data transfer object containing the cart details to be created.
	        The 'detalles' field is excluded from the database object creation.
	    db (Session): SQLAlchemy database session dependency for executing database operations.

	Returns:
	    CarritoDAO: The created cart object with all fields populated, including the auto-generated
	    ID and any default database values after commit and refresh.

	Raises:
	    SQLAlchemy exceptions: May raise database-related exceptions if the commit operation fails.

	"""
	db_carrito = CarritoDAO(**carrito.model_dump(exclude={'detalles'}))
	db.add(db_carrito)
	db.commit()
	db.refresh(db_carrito)
	return db_carrito


@router.get('/', response_model=List[CarritoDTO])
def listar_carritos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""Retrieve a paginated list of shopping carts from the database.

	Args:
	    skip (int): Number of records to skip for pagination. Defaults to 0.
	    limit (int): Maximum number of records to return. Defaults to 100.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    list[CarritoDAO]: A list of CarritoDAO objects representing shopping carts.

	"""
	carritos = db.query(CarritoDAO).offset(skip).limit(limit).all()
	return carritos


@router.get('/{carrito_id}', response_model=CarritoDTO)
def obtener_carrito(carrito_id: int, db: Session = Depends(get_db)):
	"""Retrieve a shopping cart by its ID.

	Args:
	    carrito_id (int): The unique identifier of the shopping cart to retrieve.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    CarritoDAO: The shopping cart object if found.

	Raises:
	    HTTPException: If the shopping cart with the given ID is not found (status code 404).

	"""
	carrito = db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
	if carrito is None:
		raise HTTPException(status_code=404, detail='Carrito no encontrado')
	return carrito


@router.get('/cliente/{cliente_id}', response_model=List[CarritoDTO])
def obtener_carritos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
	"""Retrieve all shopping carts associated with a specific client.

	Args:
	    cliente_id (int): The unique identifier of the client whose carts to retrieve.
	    db (Session): Database session dependency for executing queries.

	Returns:
	    list[CarritoDAO]: A list of CarritoDAO objects representing all carts
	                     belonging to the specified client. Returns an empty list
	                     if no carts are found.

	"""
	carritos = db.query(CarritoDAO).filter(CarritoDAO.id_cliente == cliente_id).all()
	return carritos


@router.put('/{carrito_id}', response_model=CarritoDTO)
def actualizar_carrito(carrito_id: int, carrito: CarritoCreateDTO, db: Session = Depends(get_db)):
	"""
	Update an existing shopping cart with new data.

	Args:
	    carrito_id (int): The unique identifier of the shopping cart to update.
	    carrito (CarritoCreateDTO): Data transfer object containing the updated cart details.
	        The 'detalles' field is excluded from the update.
	    db (Session): Database session dependency for executing database operations.

	Returns:
	    CarritoDAO: The updated cart object after committing changes to the database.

	Raises:
	    HTTPException: If the shopping cart with the given ID is not found (status code 404).

	"""
	db_carrito = db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
	if db_carrito is None:
		raise HTTPException(status_code=404, detail='Carrito no encontrado')

	for key, value in carrito.model_dump(exclude={'detalles'}).items():
		setattr(db_carrito, key, value)

	db.commit()
	db.refresh(db_carrito)
	return db_carrito


@router.delete('/{carrito_id}')
def eliminar_carrito(carrito_id: int, db: Session = Depends(get_db)):
	"""Delete a shopping cart from the database by its ID.

	Args:
	    carrito_id (int): The unique identifier of the shopping cart to delete.
	    db (Session): Database session dependency for executing database operations.

	Returns:
	    dict: A dictionary containing a success message.

	Raises:
	    HTTPException: If the shopping cart with the given ID is not found (status code 404).

	"""
	db_carrito = db.query(CarritoDAO).filter(CarritoDAO.id_carrito == carrito_id).first()
	if db_carrito is None:
		raise HTTPException(status_code=404, detail='Carrito no encontrado')

	db.delete(db_carrito)
	db.commit()
	return {'message': 'Carrito eliminado'}


@router.post('/{carrito_id}/detalles', response_model=DetalleCarritoDTO)
def agregar_detalle_carrito(
	carrito_id: int,
	detalle: DetalleCarritoCreateDTO,
	db: Session = Depends(get_db),
):
	"""
	Add a new detail item to an existing shopping cart.

	Args:
	    carrito_id (int): The unique identifier of the shopping cart to add the detail to.
	    detalle (DetalleCarritoCreateDTO): Data transfer object containing the detail information to
	        add.
	    db (Session): Database session dependency for executing database operations.

	Returns:
	    DetalleCarritoDAO: The created detail object after committing to the database.

	"""
	detalle_data = detalle.model_dump()
	detalle_data['id_carrito'] = carrito_id
	db_detalle = DetalleCarritoDAO(**detalle_data)
	db.add(db_detalle)
	db.commit()
	db.refresh(db_detalle)
	return db_detalle


@router.get('/{carrito_id}/detalles', response_model=List[DetalleCarritoDTO])
def listar_detalles_carrito(carrito_id: int, db: Session = Depends(get_db)):
	"""
	Retrieve all details associated with a specific shopping cart.

	Args:
		carrito_id (int): The unique identifier of the shopping cart.
		db (Session): Database session dependency for executing queries.

	Returns:
		list[DetalleCarritoDAO]: A list of cart detail objects associated with the given cart ID.
		Returns an empty list if no details are found for the specified cart.

	"""
	detalles = db.query(DetalleCarritoDAO).filter(DetalleCarritoDAO.id_carrito == carrito_id).all()
	return detalles
