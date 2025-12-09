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
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED

from controller.categorias import CategoriaDAO
from controller.clientes import ClienteDAO
from controller.pedidos import PedidoDAO
from controller.productos import ProductoDAO
from data.database import get_db

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


# Rutas API para los templates
@router.get('/api/admin/products')
def api_get_products(
	request: Request,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db),
):
	require_admin_auth(request)
	productos = db.query(ProductoDAO).offset(skip).limit(limit).all()
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


@router.get('/api/admin/categories')
def api_get_categories(
	request: Request,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db),
):
	require_admin_auth(request)
	categorias = db.query(CategoriaDAO).offset(skip).limit(limit).all()
	return [
		{'id_categoria': c.id_categoria, 'nombre': c.nombre, 'descripcion': c.descripcion}
		for c in categorias
	]


@router.get('/api/admin/orders')
def api_get_orders(
	request: Request,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	estado: str = Query(None),
	db: Session = Depends(get_db),
):
	require_admin_auth(request)
	query = db.query(PedidoDAO)

	if estado:
		query = query.filter(PedidoDAO.estado == estado)

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


@router.get('/api/admin/users')
def api_get_users(
	request: Request,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db),
):
	require_admin_auth(request)
	clientes = db.query(ClienteDAO).offset(skip).limit(limit).all()
	return [
		{
			'id_cliente': c.id_cliente,
			'nombre': c.nombre,
			'apellido': c.apellido,
			'correo': c.correo,
			'telefono': c.telefono,
			'direccion': c.direccion,
			'ciudad': c.ciudad,
			'pais': c.pais,
		}
		for c in clientes
	]


@router.delete('/api/admin/products/{producto_id}')
def api_delete_product(producto_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	db_producto = db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
	if db_producto is None:
		raise HTTPException(status_code=404, detail='Producto no encontrado')

	db.delete(db_producto)
	db.commit()
	return {'message': 'Producto eliminado'}


@router.delete('/api/admin/categories/{categoria_id}')
def api_delete_category(categoria_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	db_categoria = db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
	if db_categoria is None:
		raise HTTPException(status_code=404, detail='Categoría no encontrada')

	db.delete(db_categoria)
	db.commit()
	return {'message': 'Categoría eliminada'}


@router.delete('/api/admin/users/{cliente_id}')
def api_delete_user(cliente_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	db_cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
	if db_cliente is None:
		raise HTTPException(status_code=404, detail='Cliente no encontrado')

	db.delete(db_cliente)
	db.commit()
	return {'message': 'Cliente eliminado'}


@router.put('/api/admin/products/{producto_id}')
async def api_update_product(producto_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	data = json.loads(await request.body())

	db_producto = db.query(ProductoDAO).filter(ProductoDAO.id_producto == producto_id).first()
	if db_producto is None:
		raise HTTPException(status_code=404, detail='Producto no encontrado')

	for key, value in data.items():
		if hasattr(db_producto, key):
			setattr(db_producto, key, value)

	db.commit()
	db.refresh(db_producto)
	return {
		'id_producto': db_producto.id_producto,
		'nombre': db_producto.nombre,
		'descripcion': db_producto.descripcion,
		'precio': float(db_producto.precio),
		'stock': db_producto.stock,
		'id_categoria': db_producto.id_categoria,
		'imagen': db_producto.imagen,
	}


@router.put('/api/admin/categories/{categoria_id}')
async def api_update_category(categoria_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	data = json.loads(await request.body())

	db_categoria = db.query(CategoriaDAO).filter(CategoriaDAO.id_categoria == categoria_id).first()
	if db_categoria is None:
		raise HTTPException(status_code=404, detail='Categoría no encontrada')

	for key, value in data.items():
		if hasattr(db_categoria, key):
			setattr(db_categoria, key, value)

	db.commit()
	db.refresh(db_categoria)
	return {
		'id_categoria': db_categoria.id_categoria,
		'nombre': db_categoria.nombre,
		'descripcion': db_categoria.descripcion,
	}


@router.put('/api/admin/users/{cliente_id}')
async def api_update_user(cliente_id: int, request: Request, db: Session = Depends(get_db)):
	require_admin_auth(request)
	data = json.loads(await request.body())

	db_cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
	if db_cliente is None:
		raise HTTPException(status_code=404, detail='Cliente no encontrado')

	# Verificar si el correo ya existe en otro usuario
	if 'correo' in data and data['correo'] != db_cliente.correo:
		existing = db.query(ClienteDAO).filter(ClienteDAO.correo == data['correo']).first()
		if existing:
			raise HTTPException(status_code=400, detail='El correo ya está registrado')

	for key, value in data.items():
		if hasattr(db_cliente, key):
			setattr(db_cliente, key, value)

	db.commit()
	db.refresh(db_cliente)
	return {
		'id_cliente': db_cliente.id_cliente,
		'nombre': db_cliente.nombre,
		'apellido': db_cliente.apellido,
		'correo': db_cliente.correo,
		'telefono': db_cliente.telefono,
		'direccion': db_cliente.direccion,
		'ciudad': db_cliente.ciudad,
		'pais': db_cliente.pais,
	}
