"""Provide API endpoints for managing shipment ("envío") records in the database.

It defines routes for creating, listing, retrieving, updating, and deleting shipment records,
as well as retrieving a shipment by its associated order ID.

Endpoints:
	- POST   /envios/                : Create a new shipment.
	- GET    /envios/                : List all shipments with optional pagination.
	- GET    /envios/{envio_id}      : Retrieve a shipment by its ID.
	- GET    /envios/pedido/{pedido_id} : Retrieve a shipment by its associated order ID.
	- PUT    /envios/{envio_id}      : Update an existing shipment.
	- DELETE /envios/{envio_id}      : Delete a shipment by its ID.

Dependencies:
	- FastAPI APIRouter for route management.
	- SQLAlchemy Session for database operations.
	- Pydantic models for data validation and serialization.
	- HTTPException: For cases where a shipment is not found or cannot be processed.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.envio import EnvioCreateDTO, EnvioDAO, EnvioDTO

router = APIRouter(prefix='/envios', tags=['envios'])


@router.post('/', response_model=EnvioDTO)
def crear_envio(envio: EnvioCreateDTO, db: Session = Depends(get_db)):
	"""Create a new shipment record in the database.

	Args:
	    envio (EnvioCreateDTO): Data transfer object containing the shipment details to be created.
	    db (Session, optional): SQLAlchemy database session. Automatically injected by FastAPI's
		dependency system.

	Returns:
	    EnvioDAO: The newly created shipment database object, refreshed with the latest data from
		the database.

	"""
	db_envio = EnvioDAO(**envio.model_dump())
	db.add(db_envio)
	db.commit()
	db.refresh(db_envio)
	return db_envio


@router.get('/', response_model=List[EnvioDTO])
def listar_envios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""Retrieve a list of 'Envio' records from the database with optional pagination.

	Args:
	    skip (int, optional): Number of records to skip for pagination. Defaults to 0.
	    limit (int, optional): Maximum number of records to return. Defaults to 100.
	    db (Session, optional): SQLAlchemy database session dependency.

	Returns:
	    List[EnvioDAO]: A list of 'EnvioDAO' objects retrieved from the database.

	"""
	envios = db.query(EnvioDAO).offset(skip).limit(limit).all()
	return envios


@router.get('/{envio_id}', response_model=EnvioDTO)
def obtener_envio(envio_id: int, db: Session = Depends(get_db)):
	"""Retrieve a shipment (envío) from the database by its ID.

	Args:
	    envio_id (int): The unique identifier of the shipment to retrieve.
	    db (Session, optional): SQLAlchemy database session dependency. Defaults to Depends(get_db).

	Returns:
	    EnvioDAO: The shipment object corresponding to the given ID.

	Raises:
	    HTTPException: If no shipment with the specified ID is found, raises a 404 error.

	"""
	envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
	if envio is None:
		raise HTTPException(status_code=404, detail='Envío no encontrado')
	return envio


@router.get('/pedido/{pedido_id}', response_model=EnvioDTO)
def obtener_envio_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
	"""Retrieve the shipping record associated with a given order ID.

	Args:
	    pedido_id (int): The ID of the order for which to retrieve the shipping information.
	    db (Session, optional): SQLAlchemy database session dependency. Defaults to Depends(get_db).

	Returns:
	    EnvioDAO: The shipping record associated with the specified order ID.

	Raises:
	    HTTPException: If no shipping record is found for the given order ID, raises a 404 error.

	"""
	envio = db.query(EnvioDAO).filter(EnvioDAO.id_pedido == pedido_id).first()
	if envio is None:
		raise HTTPException(status_code=404, detail='Envío no encontrado para este pedido')
	return envio


@router.put('/{envio_id}', response_model=EnvioDTO)
def actualizar_envio(envio_id: int, envio: EnvioCreateDTO, db: Session = Depends(get_db)):
	"""Update an existing shipment record in the database.

	:param envio_id: Description
	:type envio_id: int
	:param envio: Description
	:type envio: EnvioCreateDTO
	:param db: Description
	:type db: Session

	"""
	db_envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
	if db_envio is None:
		raise HTTPException(status_code=404, detail='Envío no encontrado')

	for key, value in envio.model_dump().items():
		setattr(db_envio, key, value)

	db.commit()
	db.refresh(db_envio)
	return db_envio


@router.delete('/{envio_id}')
def eliminar_envio(envio_id: int, db: Session = Depends(get_db)):
	"""Delete an existing shipment (envío) from the database by its ID.

	Args:
	    envio_id (int): The ID of the shipment to delete.
	    db (Session, optional): The database session dependency.

	Raises:
	    HTTPException: If the shipment with the given ID is not found (404).

	Returns:
	    dict: A message indicating that the shipment was deleted.

	"""
	db_envio = db.query(EnvioDAO).filter(EnvioDAO.id_envio == envio_id).first()
	if db_envio is None:
		raise HTTPException(status_code=404, detail='Envío no encontrado')

	db.delete(db_envio)
	db.commit()
	return {'message': 'Envío eliminado'}
