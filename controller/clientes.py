"""Provide a FastAPI router for managing client (cliente) resources in the application.

It includes endpoints for creating, retrieving, updating, deleting, and authenticating clients.
Password handling is securely managed using bcrypt for hashing and verification.

Endpoints:
	- POST   /clientes/           : Create a new client with hashed password.
	- GET    /clientes/           : Retrieve a paginated list of clients.
	- GET    /clientes/{id}       : Retrieve a specific client by their ID.
	- PUT    /clientes/{id}       : Update an existing client's information.
	- DELETE /clientes/{id}       : Delete a client by their ID.
	- POST   /clientes/login      : Authenticate a client using email and password.

Functions:
	- hash_contrasena(contrasena: str) -> str:
		Hashes a plaintext password using bcrypt and returns the hashed string.
	- verificar_contrasena(contrasena: str, hashed: str) -> bool:
		Verifies a plaintext password against a bcrypt hashed password.
	- crear_cliente(cliente: ClienteCreateDTO, db: Session):
		Creates a new client after validating email uniqueness and hashing the password.
	- listar_clientes(skip: int, limit: int, db: Session):
		Retrieves a paginated list of clients from the database.
	- obtener_cliente(cliente_id: int, db: Session):
		Retrieves a client by their unique ID.
	- actualizar_cliente(cliente_id: int, cliente_update: ClienteCreateDTO, db: Session):
		Updates an existing client's information, including secure password hashing.
	- eliminar_cliente(cliente_id: int, db: Session):
		Deletes a client from the database by their ID.
	- login_cliente(correo: str, contrasena: str, db: Session):
		Authenticates a client using their email and password.

Notes:
	- All password operations use bcrypt for security.
	- Email uniqueness is enforced during creation and update.
	- Database transactions are rolled back on error to maintain data integrity.
	- Passwords are never returned in API responses.

"""

from typing import List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from data.database import get_db
from model.cliente import ClienteCreateDTO, ClienteDAO, ClienteDTO

router = APIRouter(prefix='/clientes', tags=['clientes'])


def hash_contrasena(contrasena: str) -> str:
	"""Hash a password using bcrypt with a randomly generated salt.

	This function takes a plain text password and applies bcrypt hashing
	with a cryptographically secure salt to produce a hashed password
	suitable for secure storage.

	Args:
	    contrasena (str): The plain text password to be hashed.

	Returns:
	    str: The hashed password as a UTF-8 encoded string.

	Example:
	    >>> hashed = hash_contrasena('miPassword123')
	    >>> isinstance(hashed, str)
	    True

	"""
	salt = bcrypt.gensalt()
	hashed = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
	return hashed.decode('utf-8')


def verificar_contrasena(contrasena: str, hashed: str) -> bool:
	"""Verify a plaintext password against a bcrypt hashed password.

	Args:
	    contrasena (str): The plaintext password to verify.
	    hashed (str): The bcrypt hashed password to compare against.

	Returns:
	    bool: True if the password matches the hash, False otherwise.

	Raises:
	    ValueError: If the hashed password is not a valid bcrypt hash.

	"""
	return bcrypt.checkpw(contrasena.encode('utf-8'), hashed.encode('utf-8'))


@router.post('/', response_model=ClienteDTO, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreateDTO, db: Session = Depends(get_db)):
	"""Create a new client in the database.

	This function creates a new client by validating that the email is not already registered,
	hashing the password, storing the client data in the database, and returning the client
	information without exposing the password.

	Args:
		cliente (ClienteCreateDTO): Data transfer object containing the client information
			to be created (email, password, and other client details).
		db (Session): Database session dependency for executing queries and transactions.
			Defaults to get_db() dependency.

	Returns:
		ClienteDTO: Data transfer object representing the created client, excluding the password.

	Raises:
		HTTPException: With status code 400 if the email is already registered in the database.
		HTTPException: With status code 500 if an error occurs during client creation or
			database transaction.

	Note:
		- The password is hashed before being stored in the database.
		- The database transaction is rolled back if an error occurs during creation.
		- The response excludes the password field for security purposes.

	"""
	existing_cliente = db.query(ClienteDAO).filter(ClienteDAO.correo == cliente.correo).first()
	if existing_cliente:
		raise HTTPException(status_code=400, detail='El correo ya está registrado')

	cliente_data = cliente.model_dump()

	if 'contrasena' in cliente_data:
		cliente_data['contrasena'] = hash_contrasena(cliente_data['contrasena'])

	db_cliente = ClienteDAO(**cliente_data)

	try:
		db.add(db_cliente)
		db.commit()
		db.refresh(db_cliente)

		return ClienteDTO.from_orm(db_cliente)

	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500, detail=f'Error al crear cliente: {str(e)}')


@router.get('/', response_model=List[ClienteDTO])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	"""
	Retrieve a paginated list of clients from the database.

	Args:
	    skip (int): Number of records to skip from the beginning. Defaults to 0.
	    limit (int): Maximum number of records to return. Defaults to 100.
	    db (Session): SQLAlchemy database session dependency. Injected automatically.

	Returns:
	    list[ClienteDAO]: A list of client objects limited by the skip and limit parameters.

	Raises:
	    Exception: If database connection fails or query execution encounters an error.

	"""
	clientes = db.query(ClienteDAO).offset(skip).limit(limit).all()
	return clientes


@router.get('/{cliente_id}', response_model=ClienteDTO)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
	"""Retrieve a client by their ID.

	Args:
	    cliente_id (int): The unique identifier of the client to retrieve.
	    db (Session): Database session dependency for querying the database.

	Returns:
	    ClienteDAO: The client object if found.

	Raises:
	    HTTPException: If the client with the given ID is not found (status_code: 404).

	"""
	cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
	if cliente is None:
		raise HTTPException(status_code=404, detail='Cliente no encontrado')
	return cliente


@router.put('/{cliente_id}', response_model=ClienteDTO)
def actualizar_cliente(
	cliente_id: int, cliente_update: ClienteCreateDTO, db: Session = Depends(get_db)
):
	"""Update an existing client with new information.

	Args:
	    cliente_id (int): The unique identifier of the client to update.
	    cliente_update (ClienteCreateDTO): Data transfer object containing the updated client
	            information.
	    db (Session, optional): Database session dependency. Defaults to get_db().

	Returns:
	    ClienteDAO: The updated client object from the database.

	Raises:
	    HTTPException: If the client with the given cliente_id is not found (status_code=404).
	    HTTPException: If the new email already exists for another client (status_code=400).

	Note:
	    - If the email is being updated, it validates that the new email is not already registered.
	    - Passwords are automatically hashed using hash_contrasena() before storage.
	    - Only non-None values are updated in the database.

	"""
	db_cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
	if db_cliente is None:
		raise HTTPException(status_code=404, detail='Cliente no encontrado')

	if cliente_update.correo != db_cliente.correo:
		existing_cliente = (
			db.query(ClienteDAO).filter(ClienteDAO.correo == cliente_update.correo).first()
		)
		if existing_cliente:
			raise HTTPException(status_code=400, detail='El correo ya está registrado')

	for key, value in cliente_update.model_dump().items():
		if key == 'contrasena' and value:
			setattr(db_cliente, key, hash_contrasena(value))
		elif value is not None:
			setattr(db_cliente, key, value)

	db.commit()
	db.refresh(db_cliente)
	return db_cliente


@router.delete('/{cliente_id}')
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
	"""Delete a client from the database given their ID.

	Args:
	    cliente_id (int): The ID of the client to delete.
	    db (Session, optional): Database session provided by the get_db dependency.

	Raises:
	    HTTPException: If the client with the specified ID is not found (404).

	Returns:
	    dict: A message indicating that the client has been deleted.

	"""
	db_cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
	if db_cliente is None:
		raise HTTPException(status_code=404, detail='Cliente no encontrado')

	db.delete(db_cliente)
	db.commit()
	return {'message': 'Cliente eliminado'}


@router.post('/login')
def login_cliente(correo: str, contrasena: str, db: Session = Depends(get_db)):
	"""Authenticate a client using their email and password.

	Args:
	    correo (str): The email address of the client attempting to log in.
	    contrasena (str): The plaintext password provided by the client.
	    db (Session, optional): SQLAlchemy database session dependency.

	Raises:
	    HTTPException: If the client does not exist or the credentials are invalid
	            (status code 401).

	Returns:
	    dict: A dictionary containing a success message, client ID, name, and email upon successful
	            authentication.

	"""
	cliente = db.query(ClienteDAO).filter(ClienteDAO.correo == correo).first()
	if not cliente:
		raise HTTPException(status_code=401, detail='Credenciales inválidas')

	if not verificar_contrasena(contrasena, cliente.contrasena):
		raise HTTPException(status_code=401, detail='Credenciales inválidas')

	return {
		'message': 'Login exitoso',
		'cliente_id': cliente.id_cliente,
		'nombre': cliente.nombre,
		'correo': cliente.correo,
	}
