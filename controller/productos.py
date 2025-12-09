"""FastAPI router for managing product-related HTTP endpoints.

This module provides CRUD operations and filtering capabilities for products,
including:
- Creating new products
- Retrieving products with pagination
- Retrieving individual products by ID
- Updating existing products
- Deleting products
- Filtering products by category

All endpoints interact with the database through SQLAlchemy ORM using
ProductoDAO for database operations and ProductoDTO/ProductoCreateDTO
for data transfer.

Dependencies:
    - FastAPI: Web framework for building the API
    - SQLAlchemy: ORM for database operations
    - Pydantic: Data validation through DTO models

"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.database import get_db
from model.producto import ProductoCreateDTO, ProductoDAO, ProductoDTO

router = APIRouter(prefix='/productos', tags=['productos'])


@router.post('/', response_model=ProductoDTO)
def crear_producto(producto: ProductoCreateDTO, db: Session = Depends(get_db)):
	"""Create a new product in the database.

	Args:
	    producto (ProductoCreateDTO): Data transfer object containing the product details to be
	    created.
	    db (Session): SQLAlchemy database session dependency for executing database operations.

	Returns:
	    ProductoDAO: The created product object with all fields populated, including the
	    auto-generated
	    ID and any default database values after commit and refresh.

	Raises:
	    SQLAlchemy exceptions: May raise database-related exceptions if the commit operation fails.

	"""
	db_producto = ProductoDAO(**producto.model_dump())
	db.add(db_producto)
	db.commit()
	db.refresh(db_producto)
	return db_producto


@router.get('/', response_model=List[ProductoDTO])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""Retrieve a paginated list of products from the database.

	Args:
	    skip (int): Number of records to skip for pagination. Defaults to 0.
	    limit (int): Maximum number of records to return. Defaults to 100.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    list[ProductoDAO]: A list of ProductoDAO objects representing products.

	"""
	productos = db.query(ProductoDAO).offset(skip).limit(limit).all()
	return productos


@router.get('/{producto_id}', response_model=ProductoDTO)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
	"""Retrieve a product by its ID.

	Args:
	    producto_id (int): The unique identifier of the product to retrieve.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    ProductoDAO: The product object if found.

	Raises:
	    HTTPException: If the product with the given ID is not found (status code 404).

	"""
	producto = db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
	if producto is None:
		raise HTTPException(status_code=404, detail='Producto no encontrado')
	return producto


@router.put('/{producto_id}', response_model=ProductoDTO)
def actualizar_producto(
	producto_id: int,
	producto: ProductoCreateDTO,
	db: Session = Depends(get_db),
):
	"""Update an existing product in the database.

	Args:
		producto_id (int): The unique identifier of the product to update.
		producto (ProductoCreateDTO): Data transfer object containing the updated product details.
		db (Session): Database session dependency for executing database operations.

	Returns:
		ProductoDAO: The updated product object with all fields refreshed from the database.

	Raises:
		HTTPException: If the product with the given ID is not found (status code 404).

	"""
	db_producto = db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
	if db_producto is None:
		raise HTTPException(status_code=404, detail='Producto no encontrado')

	for key, value in producto.model_dump().items():
		setattr(db_producto, key, value)

	db.commit()
	db.refresh(db_producto)
	return db_producto


@router.delete('/{producto_id}')
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
	"""Delete a product from the database by its ID.

	Args:
	    producto_id (int): The unique identifier of the product to delete.
	    db (Session): Database session dependency for executing database operations.

	Returns:
	    dict: A dictionary containing a success message.

	Raises:
	    HTTPException: If the product with the given ID is not found (status code 404).

	"""
	db_producto = db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
	if db_producto is None:
		raise HTTPException(status_code=404, detail='Producto no encontrado')

	db.delete(db_producto)
	db.commit()
	return {'message': 'Producto eliminado'}


@router.get('/categoria/{categoria_id}', response_model=List[ProductoDTO])
def listar_productos_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
	"""Retrieve all products associated with a specific category.

	Args:
	    categoria_id (int): The unique identifier of the category whose products to retrieve.
	    db (Session): Database session dependency for executing queries.

	Returns:
	    list[ProductoDAO]: A list of ProductoDAO objects representing all products
	                       belonging to the specified category. Returns an empty list
	                       if no products are found.

	"""
	productos = db.query(ProductoDAO).filter(ProductoDAO.id_categoria == categoria_id).all()
	return productos
