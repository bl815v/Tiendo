"""Categorias Router Module.

This module provides REST API endpoints for managing product categories in the Tiendo application.
It implements CRUD (Create, Read, Update, Delete) operations for categories with database
persistence using SQLAlchemy ORM.

The router handles:
- Creating new categories
- Retrieving paginated lists of categories
- Fetching individual categories by ID
- Updating existing categories
- Deleting categories
All endpoints require a valid database session and return properly formatted DTOs.

"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.categoria import CategoriaCreateDTO, CategoriaDAO, CategoriaDTO

router = APIRouter(prefix='/categorias', tags=['categorias'])


@router.post('/', response_model=CategoriaDTO)
def crear_categoria(categoria: CategoriaCreateDTO, db: Session = Depends(get_db)):
	"""Create a new category in the database.

	Args:
	    categoria (CategoriaCreateDTO): Data transfer object containing the category information to
	    be created.
	    db (Session): Database session dependency for performing database operations.

	Returns:
	    CategoriaDAO: The newly created category object with all database-generated fields
	    populated.

	Raises:
	    SQLAlchemyError: If a database error occurs during the commit operation.

	"""
	db_categoria = CategoriaDAO(**categoria.model_dump())
	db.add(db_categoria)
	db.commit()
	db.refresh(db_categoria)
	return db_categoria


@router.get('/', response_model=List[CategoriaDTO])
def listar_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""Retrieve a paginated list of categories from the database.

	Args:
	    skip (int, optional): Number of records to skip for pagination. Defaults to 0.
	    limit (int, optional): Maximum number of records to return. Defaults to 100.
	    db (Session, optional): Database session dependency for querying. Defaults to
	    Depends(get_db).

	Returns:
	    list[CategoriaDAO]: A list of category objects retrieved from the database.

	"""
	categorias = db.query(CategoriaDAO).offset(skip).limit(limit).all()
	return categorias


@router.get('/{categoria_id}', response_model=CategoriaDTO)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
	"""Retrieve a category by its ID.

	Args:
	    categoria_id (int): The unique identifier of the category to retrieve.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    CategoriaDAO: The category object if found.

	Raises:
	    HTTPException: If the category with the given ID is not found (status_code=404).

	"""
	categoria = db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
	if categoria is None:
		raise HTTPException(status_code=404, detail='Categoría no encontrada')
	return categoria


@router.put('/{categoria_id}', response_model=CategoriaDTO)
def actualizar_categoria(
	categoria_id: int, categoria: CategoriaCreateDTO, db: Session = Depends(get_db)
):
	"""Update an existing category in the database.

	Args:
	    categoria_id (int): The ID of the category to update.
	    categoria (CategoriaCreateDTO): DTO object containing the updated category data.
	    db (Session): Database session dependency for executing queries.

	Returns:
	    CategoriaDAO: The updated category object from the database.

	Raises:
	    HTTPException: If the category with the specified ID is not found (status code 404).

	"""
	db_categoria = db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
	if db_categoria is None:
		raise HTTPException(status_code=404, detail='Categoría no encontrada')

	for key, value in categoria.model_dump().items():
		setattr(db_categoria, key, value)

	db.commit()
	db.refresh(db_categoria)
	return db_categoria


@router.delete('/{categoria_id}')
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
	"""Eliminate a category from the database by its ID.

	Args:
	    categoria_id (int): The ID of the category to be deleted.
	    db (Session): Database session dependency for performing the deletion.

	Returns:
	    dict: A dictionary containing a success message.

	Raises:
	    HTTPException: If the category with the given ID is not found (status code 404).

	"""
	db_categoria = db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
	if db_categoria is None:
		raise HTTPException(status_code=404, detail='Categoría no encontrada')

	db.delete(db_categoria)
	db.commit()
	return {'message': 'Categoría eliminada'}
