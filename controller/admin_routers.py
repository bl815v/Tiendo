"""Provide FastAPI routes for administrative dashboard functionality.

Includes:
- Admin authentication and session management
- Product management endpoints
- Category management endpoints
- Order management endpoints
- User management endpoints
- Statistical data endpoints for admin dashboard
- Filtering and debugging endpoints

Authentication:
All protected endpoints require valid admin session authentication via the
require_admin_auth() dependency. Sessions are stored in-memory with 3600 second
(1 hour) expiration.

Session Management:
- Sessions are created upon successful login with secure tokens (32-byte URL-safe)
- Sessions are stored server-side with username, creation timestamp, and client IP
- Sessions expire after 3600 seconds of inactivity
- Logout clears both server-side session and client-side cookie

Routes:
GET/POST Routes:
	- /admin/login: Admin login page and authentication
	- /admin: Admin dashboard (requires auth)
	- /admin/check-session: Session validation endpoint
	- /admin/logout: Session cleanup and logout
	- /admin/products: Products management page
	- /admin/products/add: Product creation form
	- /admin/categories: Categories management page
	- /admin/categories/add: Category creation form
	- /admin/orders: Orders management page
	- /admin/orders/pending: Pending orders page
	- /admin/users: Users management page
	- /admin/users/activity: User activity page
API Endpoints:
	- /api/v1/admin/stats/products: Product statistics
	- /api/v1/admin/stats/orders: Order statistics
	- /api/v1/admin/stats/users: User statistics
	- /api/v1/admin/debug: Debug information and connectivity check
	- /api/v1/admin/filter/orders: Advanced order filtering
	- /api/v1/admin/filter/products: Advanced product filtering

Environment Variables:
	- ADMIN_USER: Configured admin username for authentication
	- ADMIN_PASS: Configured admin password for authentication

Dependencies:
	- FastAPI: Web framework
	- SQLAlchemy: ORM for database operations
	- Jinja2Templates: Template rendering
	- dotenv: Environment variable loading

"""

import os
import secrets
import sys
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED

from data.database import get_db
from model.categoria import CategoriaDAO
from model.cliente import ClienteDAO
from model.pedido import PedidoDAO
from model.producto import ProductoDAO

load_dotenv()

router = APIRouter()

if getattr(sys, 'frozen', False):
	BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath('.'))
else:
	BASE_PATH = os.path.abspath('.')

templates_path = os.path.join(BASE_PATH, 'templates')
templates = Jinja2Templates(directory=templates_path)

ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_PASS = os.getenv('ADMIN_PASS')

admin_sessions = {}


def require_admin_auth(request: Request):
	"""Validate and authenticates an admin user based on session cookie.

	Checks for a valid admin session by verifying:
	1. Session cookie exists in the request
	2. Session ID exists in the admin_sessions storage
	3. Session has not expired (within 3600 seconds)

	Args:
		request (Request): The incoming HTTP request object containing cookies.

	Returns:
		dict: The session data associated with the valid session ID.

	Raises:
		HTTPException:
			- 401 Unauthorized if no session cookie is provided ('No autenticado')
			- 401 Unauthorized if session ID is not found ('Sesión inválida')
			- 401 Unauthorized if session has expired ('Sesión expirada')

	"""
	session_id = request.cookies.get('admin_session')

	if not session_id:
		raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='No autenticado')

	session_data = admin_sessions.get(session_id)
	if not session_data:
		raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Sesión inválida')

	if time.time() - session_data.get('created_at', 0) > 3600:
		del admin_sessions[session_id]
		raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Sesión expirada')

	return session_data


@router.get('/admin/login', response_class=HTMLResponse)
def admin_login(request: Request):
	"""Handle admin login page request.

	Args:
		request (Request): The HTTP request object containing request metadata.

	Returns:
		TemplateResponse: A template response rendering the admin login page with the request
		context.

	"""
	return templates.TemplateResponse('admin_login.html', {'request': request})


@router.post('/admin/login')
async def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
	"""Handle admin login POST request.

	Authenticates the admin user by comparing provided credentials against
	configured admin username and password. On successful authentication,
	creates a session with a secure token and sets an httponly cookie.

	Args:
		request (Request): The FastAPI request object containing client information.
		username (str): The admin username from the login form.
		password (str): The admin password from the login form.

	Returns:
		TemplateResponse:
			- If admin credentials are not configured: renders admin_login.html with
			  server configuration error message.
			- If credentials match: redirects to /admin with HTTP 302 status and sets
			  admin_session cookie.
			- If credentials do not match: renders admin_login.html with invalid
			  credentials error message.

	Side Effects:
		- On successful authentication, adds a new session to admin_sessions dictionary
		  with session_id as key, containing username, creation timestamp, and client IP.

	"""
	if not ADMIN_USER or not ADMIN_PASS:
		return templates.TemplateResponse(
			'admin_login.html',
			{'request': request, 'error': 'Error de configuración del servidor'},
		)

	if username == ADMIN_USER and password == ADMIN_PASS:
		session_id = secrets.token_urlsafe(32)
		admin_sessions[session_id] = {
			'username': username,
			'created_at': time.time(),
			'ip': request.client.host if request.client else 'unknown',
		}

		response = RedirectResponse(url='/admin', status_code=HTTP_302_FOUND)
		response.set_cookie(
			key='admin_session',
			value=session_id,
			httponly=True,
			secure=False,
			samesite='lax',
			max_age=3600,
		)
		return response

	return templates.TemplateResponse(
		'admin_login.html',
		{'request': request, 'error': 'Usuario o contraseña incorrectos'},
	)


@router.get('/admin', response_class=HTMLResponse)
def admin_index(request: Request):
	"""Handle the admin dashboard index page.

	Requires admin authentication via session. If authentication fails,
	redirects to the admin login page.

	Args:
		request (Request): The HTTP request object.

	Returns:
		TemplateResponse: Rendered admin_index.html template with request context
						 and username from session data.

	Raises:
		HTTPException: Caught internally and handled with redirect to login.

	"""
	try:
		session_data = require_admin_auth(request)
	except HTTPException:
		return RedirectResponse(url='admin/login', status_code=HTTP_302_FOUND)

	return templates.TemplateResponse(
		'admin_index.html',
		{'request': request, 'username': session_data.get('username', 'Admin')},
	)


@router.get('/admin/check-session')
def check_session(request: Request):
	"""Validate the current admin session and return session status.

	This endpoint checks if the provided request contains a valid admin authentication session.
	If the session is valid, it returns the admin's username. If the session is invalid or expired,
	it returns an error response with HTTP 401 status code.

	Args:
		request (Request): The incoming HTTP request object containing session/authentication data.

	Returns:
		JSONResponse: A JSON response object containing:
			- On success: {'status': 'ok', 'username': str} with HTTP 200 status
			- On failure: {'status': 'error', 'message': 'Sesión inválida'} with HTTP 401 status

	Raises:
		HTTPException: Caught internally when authentication fails, converted to JSON error
		response.

	"""
	try:
		session_data = require_admin_auth(request)
		return JSONResponse({'status': 'ok', 'username': session_data.get('username')})
	except HTTPException:
		return JSONResponse({'status': 'error', 'message': 'Sesión inválida'}, status_code=401)


@router.post('/admin/logout')
async def admin_logout(request: Request):
	"""Handle admin user logout by clearing the session.

	This async endpoint removes the admin session from the sessions dictionary
	and clears the admin_session cookie, then redirects the user to the login page.

	Args:
		request (Request): The incoming HTTP request object containing cookies.

	Returns:
		RedirectResponse: A redirect response to '/admin/login' with HTTP 302 status code
						 and the admin_session cookie deleted.

	Note:
		- Safely handles cases where the session_id doesn't exist in admin_sessions
		- Clears both server-side session storage and client-side cookie

	"""
	session_id = request.cookies.get('admin_session')

	if session_id in admin_sessions:
		del admin_sessions[session_id]

	response = RedirectResponse(url='/admin/login', status_code=HTTP_302_FOUND)
	response.delete_cookie(key='admin_session')
	return response


@router.get('/admin/products', response_class=HTMLResponse)
def admin_products(request: Request):
	"""Render the admin products management page.

	Requires admin authentication to access. This endpoint serves the admin
	products template where administrators can view and manage product inventory.

	Args:
		request (Request): The HTTP request object containing client information
						   and session data.

	Returns:
		TemplateResponse: Rendered HTML template 'admin_products.html' with the
						  request context.

	Raises:
		HTTPException: If the user is not authenticated as an administrator
					   (raised by require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_products.html', {'request': request})


@router.get('/admin/products/add', response_class=HTMLResponse)
def admin_add_product(request: Request):
	"""Handle the admin product addition page request.

	Args:
		request (Request): The incoming HTTP request object.

	Returns:
		TemplateResponse: A template response rendering the admin product addition form.

	Raises:
		HTTPException: If the user is not authenticated as an admin.

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_products_add.html', {'request': request})


@router.get('/admin/categories', response_class=HTMLResponse)
def admin_categories(request: Request):
	"""Handle admin categories page request.

	Verifies that the requesting user has admin authentication before
	rendering the admin categories template.

	Args:
		request (Request): The incoming HTTP request object.

	Returns:
		TemplateResponse: Rendered admin_categories.html template with request context.

	Raises:
		HTTPException: If user lacks admin authentication (via require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_categories.html', {'request': request})


@router.get('/admin/categories/add', response_class=HTMLResponse)
def admin_add_category(request: Request):
	"""Handle GET request to display the admin category addition form.

	This endpoint requires admin authentication. It renders the admin categories
	add template which contains the form for creating a new product category.

	Args:
		request (Request): The incoming HTTP request object containing user session
						  and authentication information.

	Returns:
		TemplateResponse: Renders 'admin_categories_add.html' with the request object
						 passed to the template context.

	Raises:
		HTTPException: If the user is not authenticated as an admin (via require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_categories_add.html', {'request': request})


@router.get('/admin/orders', response_class=HTMLResponse)
def admin_orders(request: Request):
	"""Handle the admin orders page request.

	Requires administrator authentication to access this endpoint.

	Args:
		request (Request): The HTTP request object containing client information.

	Returns:
		TemplateResponse: A template response rendering the admin orders page with the request
		context.

	Raises:
		HTTPException: If the user is not authenticated as an administrator (raised by
		require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_orders.html', {'request': request})


@router.get('/admin/orders/pending', response_class=HTMLResponse)
def admin_orders_pending(request: Request):
	"""Render the admin pending orders page.

	Args:
		request (Request): The HTTP request object containing user session information.

	Returns:
		TemplateResponse: A template response rendering 'admin_orders_pending.html' with the request
		context.

	Raises:
		Unauthorized: If the user is not authenticated as an admin (via require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_orders_pending.html', {'request': request})


@router.get('/admin/users', response_class=HTMLResponse)
def admin_users(request: Request):
	"""Handle the admin users page request.

	Verifies that the request is authenticated with admin privileges before
	rendering the admin users template.

	Args:
		request (Request): The incoming HTTP request object.

	Returns:
		TemplateResponse: A template response rendering 'admin_users.html'
						 with the request context.

	Raises:
		HTTPException: If the request does not have valid admin authentication.

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_users.html', {'request': request})


@router.get('/admin/users/activity', response_class=HTMLResponse)
def admin_users_activity(request: Request):
	"""Handle admin request to view users activity page.

	Args:
		request (Request): The HTTP request object containing user session and context.

	Returns:
		TemplateResponse: Rendered HTML template 'admin_users_activity.html' with request context.

	Raises:
		HTTPException: If user is not authenticated as admin (via require_admin_auth).

	"""
	require_admin_auth(request)
	return templates.TemplateResponse('admin_users_activity.html', {'request': request})


@router.get('/api/v1/admin/stats/products')
def api_get_products_stats(request: Request, db: Session = Depends(get_db)):
	"""Retrieve statistics about products from the database for administrative purposes.

	Args:
		request (Request): The incoming HTTP request object, used for authentication.
		db (Session, optional): SQLAlchemy database session dependency.

	Returns:
		dict: A dictionary containing the following product statistics:
			- 'total_productos': Total number of products.
			- 'productos_bajo_stock': Number of products with stock less than 10.
			- 'productos_sin_imagen': Number of products without an image.
			- 'bajo_stock_porcentaje': Percentage of products with low stock (less than 10).

	Raises:
		HTTPException: If the user is not authenticated as an admin.

	"""
	require_admin_auth(request)

	total_productos = db.query(ProductoDAO).count()
	productos_bajo_stock = db.query(ProductoDAO).filter(ProductoDAO.stock < 10).count()

	productos_sin_imagen = (
		db.query(ProductoDAO)
		.filter((ProductoDAO.imagen is None) | (ProductoDAO.imagen == ''))
		.count()
	)

	return {
		'total_productos': total_productos,
		'productos_bajo_stock': productos_bajo_stock,
		'productos_sin_imagen': productos_sin_imagen,
		'bajo_stock_porcentaje': (productos_bajo_stock / total_productos * 100)
		if total_productos > 0
		else 0,
	}


@router.get('/api/v1/admin/stats/orders')
def api_get_orders_stats(request: Request, db: Session = Depends(get_db)):
	"""Retrieve statistics about orders for admin users.

	This endpoint requires admin authentication and provides the following statistics:
	- Total number of orders.
	- Number of orders placed today.
	- Total sales amount.
	- Number of orders grouped by their status.

	Args:
		request (Request): The incoming HTTP request, used for authentication.
		db (Session, optional): SQLAlchemy database session dependency.

	Returns:
		dict: A dictionary containing:
			- 'total_pedidos' (int): Total number of orders.
			- 'pedidos_hoy' (int): Number of orders placed today.
			- 'total_ventas' (float): Total sales amount.
			- 'por_estado' (dict): Mapping of order status to the count of orders in that status.

	"""
	require_admin_auth(request)

	pedidos_por_estado = (
		db.query(PedidoDAO.estado, func.count(PedidoDAO.id_pedido).label('cantidad'))
		.group_by(PedidoDAO.estado)
		.all()
	)

	total_pedidos = db.query(PedidoDAO).count()
	hoy = datetime.now().date()
	pedidos_hoy = db.query(PedidoDAO).filter(func.date(PedidoDAO.fecha_pedido) == hoy).count()
	total_ventas = db.query(func.sum(PedidoDAO.total)).scalar() or 0

	return {
		'total_pedidos': total_pedidos,
		'pedidos_hoy': pedidos_hoy,
		'total_ventas': float(total_ventas),
		'por_estado': {estado: cantidad for estado, cantidad in pedidos_por_estado},
	}


@router.get('/api/v1/admin/stats/users')
def api_get_users_stats(request: Request, db: Session = Depends(get_db)):
	"""Retrieve user statistics for the admin dashboard.

	This endpoint requires admin authentication and returns various statistics about users in the
	system, including:
	- Total number of users.
	- Number of users who have placed at least one order.
	- Number of users registered in the last 7 days.
	- Percentage of users who have placed at least one order.

	Args:
		request (Request): The incoming HTTP request, used for authentication.
		db (Session, optional): SQLAlchemy database session, injected via dependency.

	Returns:
		dict: A dictionary containing the following keys:
			- 'total_usuarios' (int): Total number of users.
			- 'usuarios_con_pedidos' (int): Number of users with at least one order.
			- 'nuevos_usuarios_7dias' (int): Number of users registered in the last 7 days.
			- 'usuarios_activos_porcentaje' (float): Percentage of users with at least one order.

	"""
	require_admin_auth(request)
	total_usuarios = db.query(ClienteDAO).count()
	usuarios_con_pedidos = db.query(ClienteDAO).join(PedidoDAO).distinct().count()
	siete_dias_atras = datetime.now() - timedelta(days=7)
	nuevos_usuarios = (
		db.query(ClienteDAO)
		.filter(func.date(ClienteDAO.fecha_registro) >= siete_dias_atras.date())
		.count()
		if hasattr(ClienteDAO, 'fecha_registro')
		else 0
	)

	return {
		'total_usuarios': total_usuarios,
		'usuarios_con_pedidos': usuarios_con_pedidos,
		'nuevos_usuarios_7dias': nuevos_usuarios,
		'usuarios_activos_porcentaje': (usuarios_con_pedidos / total_usuarios * 100)
		if total_usuarios > 0
		else 0,
	}


@router.get('/api/v1/admin/debug')
def api_admin_debug(request: Request, db: Session = Depends(get_db)):
	"""Provide a debug endpoint for admin users to retrieve basic statistics, verify connectivity.

	Args:
		request (Request): The incoming HTTP request, used for authentication.
		db (Session, optional): SQLAlchemy database session, injected by dependency.

	Returns:
		dict: A dictionary containing:
			- 'status': Operation status ('OK' or 'ERROR').
			- 'database': Connection status ('connected' or 'connection_failed').
			- 'timestamp': ISO formatted timestamp of the response.
			- 'counts': Dictionary with total counts for 'categorias', 'productos', 'clientes', and
			'pedidos'.
			- 'last_records': Dictionary with the last record for each table (categoria, producto,
			cliente, pedido), including key fields.
			- 'error': Error message (only present if an exception occurs).

	Raises:
		Exception: Any exception encountered during database operations is caught and returned in
		the response.

	"""
	require_admin_auth(request)

	try:
		total_categorias = db.query(CategoriaDAO).count()
		total_productos = db.query(ProductoDAO).count()
		total_clientes = db.query(ClienteDAO).count()
		total_pedidos = db.query(PedidoDAO).count()

		ultima_categoria = db.query(CategoriaDAO).order_by(CategoriaDAO.id_categoria.desc()).first()
		ultimo_producto = db.query(ProductoDAO).order_by(ProductoDAO.id_producto.desc()).first()
		ultimo_cliente = db.query(ClienteDAO).order_by(ClienteDAO.id_cliente.desc()).first()
		ultimo_pedido = db.query(PedidoDAO).order_by(PedidoDAO.id_pedido.desc()).first()

		return {
			'status': 'OK',
			'database': 'connected',
			'timestamp': datetime.now().isoformat(),
			'counts': {
				'categorias': total_categorias,
				'productos': total_productos,
				'clientes': total_clientes,
				'pedidos': total_pedidos,
			},
			'last_records': {
				'categoria': {
					'id': ultima_categoria.id_categoria if ultima_categoria else None,
					'nombre': ultima_categoria.nombre if ultima_categoria else None,
				}
				if ultima_categoria
				else None,
				'producto': {
					'id': ultimo_producto.id_producto if ultimo_producto else None,
					'nombre': ultimo_producto.nombre if ultimo_producto else None,
				}
				if ultimo_producto
				else None,
				'cliente': {
					'id': ultimo_cliente.id_cliente if ultimo_cliente else None,
					'nombre': ultimo_cliente.nombre if ultimo_cliente else None,
				}
				if ultimo_cliente
				else None,
				'pedido': {
					'id': ultimo_pedido.id_pedido if ultimo_pedido else None,
					'total': float(ultimo_pedido.total) if ultimo_pedido else None,
				}
				if ultimo_pedido
				else None,
			},
		}
	except Exception as e:
		return {
			'status': 'ERROR',
			'database': 'connection_failed',
			'error': str(e),
			'timestamp': datetime.now().isoformat(),
		}


@router.get('/api/v1/admin/filter/orders')
def api_filter_orders(
	request: Request,
	estado: str = Query(None),
	cliente_id: int = Query(None),
	fecha_desde: str = Query(None),
	fecha_hasta: str = Query(None),
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db),
):
	"""
	Filter and retrieves orders (pedidos) from the database based on provided query parameters.

	Args:
		request (Request): The incoming HTTP request object.
		estado (str, optional): Filter orders by their status. Defaults to None.
		cliente_id (int, optional): Filter orders by client ID. Defaults to None.
		fecha_desde (str, optional): ISO 8601 date string to filter orders from this date
		(inclusive). Defaults to None.
		fecha_hasta (str, optional): ISO 8601 date string to filter orders up to this date
		(inclusive). Defaults to None.
		skip (int, optional): Number of records to skip for pagination. Defaults to 0.
		limit (int, optional): Maximum number of records to return (between 1 and 200). Defaults to
		100.
		db (Session): SQLAlchemy database session dependency.

	Returns:
		list[dict]: A list of dictionaries, each representing an order with keys:
			- 'id_pedido': Order ID
			- 'id_cliente': Client ID
			- 'fecha_pedido': Order date in ISO format (or None)
			- 'total': Total amount as float
			- 'estado': Order status

	Raises:
		None directly, but may raise exceptions from authentication or database access.

	"""
	require_admin_auth(request)

	query = db.query(PedidoDAO)

	if estado:
		query = query.filter(PedidoDAO.estado == estado)

	if cliente_id:
		query = query.filter(PedidoDAO.id_cliente == cliente_id)

	if fecha_desde:
		try:
			fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
			query = query.filter(PedidoDAO.fecha_pedido >= fecha_desde_dt)
		except ValueError:
			pass

	if fecha_hasta:
		try:
			fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
			query = query.filter(PedidoDAO.fecha_pedido <= fecha_hasta_dt)
		except ValueError:
			pass

	query = query.order_by(PedidoDAO.fecha_pedido.desc())

	pedidos = query.offset(skip).limit(limit).all()

	return [
		{
			'id_pedido': p.id_pedido,
			'id_cliente': p.id_cliente,
			'fecha_pedido': p.fecha_pedido.isoformat() if p.fecha_pedido else None,
			'total': float(p.total),
			'estado': p.estado,
		}
		for p in pedidos
	]


@router.get('/api/v1/admin/filter/products')
def api_filter_products(
	request: Request,
	categoria_id: int = Query(None),
	stock_min: int = Query(None),
	stock_max: int = Query(None),
	precio_min: float = Query(None),
	precio_max: float = Query(None),
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db),
):
	"""
	Filter and retrieve products with pagination and optional filters.

	Retrieves a paginated list of products from the database with support for
	filtering by category, price range, and stock range. Requires admin authentication.

	Args:
		request (Request): The HTTP request object used for authentication.
		categoria_id (int, optional): Filter by product category ID. Defaults to None.
		stock_min (int, optional): Minimum stock quantity filter. Defaults to None.
		stock_max (int, optional): Maximum stock quantity filter. Defaults to None.
		precio_min (float, optional): Minimum price filter. Defaults to None.
		precio_max (float, optional): Maximum price filter. Defaults to None.
		skip (int): Number of records to skip for pagination. Defaults to 0, must be >= 0.
		limit (int): Maximum number of records to return. Defaults to 100, must be between 1-200.
		db (Session): Database session dependency. Injected by FastAPI's Depends().

	Returns:
		list[dict]: A list of dictionaries containing filtered product information with keys:
			- id_producto (int): Product ID
			- nombre (str): Product name
			- descripcion (str): Product description
			- precio (float): Product price
			- stock (int): Current stock quantity
			- id_categoria (int): Category ID
			- imagen (str): Product image URL/path
	Raises:
		HTTPException: If user is not authenticated as admin.

	"""
	require_admin_auth(request)

	query = db.query(ProductoDAO)

	if categoria_id:
		query = query.filter(ProductoDAO.id_categoria == categoria_id)

	if stock_min is not None:
		query = query.filter(ProductoDAO.stock >= stock_min)

	if stock_max is not None:
		query = query.filter(ProductoDAO.stock <= stock_max)

	if precio_min is not None:
		query = query.filter(ProductoDAO.precio >= precio_min)

	if precio_max is not None:
		query = query.filter(ProductoDAO.precio <= precio_max)

	query = query.order_by(ProductoDAO.id_producto)

	productos = query.offset(skip).limit(limit).all()

	return [
		{
			'id_producto': p.id_producto,
			'nombre': p.nombre,
			'descripcion': p.descripcion,
			'precio': float(p.precio),
			'stock': p.stock,
			'id_categoria': p.id_categoria,
			'imagen': p.imagen,
		}
		for p in productos
	]
