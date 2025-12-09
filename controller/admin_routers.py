import json
import os
import secrets
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_
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
	return templates.TemplateResponse('admin_login.html', {'request': request})


@router.post('/admin/login')
async def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
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
	try:
		session_data = require_admin_auth(request)
		return JSONResponse({'status': 'ok', 'username': session_data.get('username')})
	except HTTPException:
		return JSONResponse({'status': 'error', 'message': 'Sesión inválida'}, status_code=401)


@router.post('/admin/logout')
async def admin_logout(request: Request):
	session_id = request.cookies.get('admin_session')

	if session_id in admin_sessions:
		del admin_sessions[session_id]

	response = RedirectResponse(url='/admin/login', status_code=HTTP_302_FOUND)
	response.delete_cookie(key='admin_session')
	return response


@router.get('/admin/products', response_class=HTMLResponse)
def admin_products(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_products.html', {'request': request})


@router.get('/admin/products/add', response_class=HTMLResponse)
def admin_add_product(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_products_add.html', {'request': request})


@router.get('/admin/categories', response_class=HTMLResponse)
def admin_categories(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_categories.html', {'request': request})


@router.get('/admin/categories/add', response_class=HTMLResponse)
def admin_add_category(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_categories_add.html', {'request': request})


@router.get('/admin/orders', response_class=HTMLResponse)
def admin_orders(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_orders.html', {'request': request})


@router.get('/admin/orders/pending', response_class=HTMLResponse)
def admin_orders_pending(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_orders_pending.html', {'request': request})


@router.get('/admin/users', response_class=HTMLResponse)
def admin_users(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_users.html', {'request': request})


@router.get('/admin/users/activity', response_class=HTMLResponse)
def admin_users_activity(request: Request):
	require_admin_auth(request)
	return templates.TemplateResponse('admin_users_activity.html', {'request': request})


# ========== RUTAS API PARA ADMINISTRACIÓN ==========


@router.get('/api/v1/admin/stats/products')
def api_get_products_stats(
	request: Request,
	db: Session = Depends(get_db),
):
	"""Estadísticas de productos para el panel de admin"""
	require_admin_auth(request)

	total_productos = db.query(ProductoDAO).count()
	productos_bajo_stock = db.query(ProductoDAO).filter(ProductoDAO.stock < 10).count()

	productos_sin_imagen = (
		db.query(ProductoDAO)
		.filter((ProductoDAO.imagen == None) | (ProductoDAO.imagen == ''))
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
def api_get_orders_stats(
	request: Request,
	db: Session = Depends(get_db),
):
	"""Estadísticas de pedidos para el panel de admin"""
	require_admin_auth(request)

	from sqlalchemy import func

	# Contar pedidos por estado
	pedidos_por_estado = (
		db.query(PedidoDAO.estado, func.count(PedidoDAO.id_pedido).label('cantidad'))
		.group_by(PedidoDAO.estado)
		.all()
	)

	total_pedidos = db.query(PedidoDAO).count()

	# Pedidos de hoy
	hoy = datetime.now().date()
	pedidos_hoy = db.query(PedidoDAO).filter(func.date(PedidoDAO.fecha_pedido) == hoy).count()

	# Total de ventas
	total_ventas = db.query(func.sum(PedidoDAO.total)).scalar() or 0

	return {
		'total_pedidos': total_pedidos,
		'pedidos_hoy': pedidos_hoy,
		'total_ventas': float(total_ventas),
		'por_estado': {estado: cantidad for estado, cantidad in pedidos_por_estado},
	}


@router.get('/api/v1/admin/stats/users')
def api_get_users_stats(
	request: Request,
	db: Session = Depends(get_db),
):
	"""Estadísticas de usuarios para el panel de admin"""
	require_admin_auth(request)

	total_usuarios = db.query(ClienteDAO).count()

	# Usuarios con pedidos
	usuarios_con_pedidos = db.query(ClienteDAO).join(PedidoDAO).distinct().count()

	# Últimos usuarios registrados (últimos 7 días)
	from datetime import datetime, timedelta
	from sqlalchemy import func

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
def api_admin_debug(
	request: Request,
	db: Session = Depends(get_db),
):
	"""Endpoint de diagnóstico para el administrador"""
	require_admin_auth(request)

	try:
		# Estadísticas básicas
		total_categorias = db.query(CategoriaDAO).count()
		total_productos = db.query(ProductoDAO).count()
		total_clientes = db.query(ClienteDAO).count()
		total_pedidos = db.query(PedidoDAO).count()

		# Verificar conexión a cada tabla
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


# ========== RUTAS ESPECIALES PARA FILTRADO ==========


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
	"""Filtrado avanzado de pedidos para el panel de admin"""
	require_admin_auth(request)

	query = db.query(PedidoDAO)

	# Aplicar filtros
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

	# Ordenar por fecha más reciente
	query = query.order_by(PedidoDAO.fecha_pedido.desc())

	# Aplicar paginación
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
	"""Filtrado avanzado de productos para el panel de admin"""
	require_admin_auth(request)

	from sqlalchemy import and_

	query = db.query(ProductoDAO)

	# Aplicar filtros
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

	# Ordenar por ID
	query = query.order_by(ProductoDAO.id_producto)

	# Aplicar paginación
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


# other routes
