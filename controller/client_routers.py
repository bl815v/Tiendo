"""Define API routes for the Tiendo application using FastAPI's APIRouter.

It provides endpoints for serving static files, rendering HTML templates, and basic health checks.

Routes:
    - /health: Returns the health status of the API.
    - /: Renders the index page.
    - /user: Renders the user page.
    - /cart: Renders the shopping cart page.
    - /product: Renders the product page.
    - /login-template: Renders the login page.
    - /register-template: Renders the registration page.

Static files and templates are served from configurable directories, supporting both frozen and
non-frozen execution environments.

Dependencies:
    - FastAPI
    - Starlette
    - Jinja2
    - model (custom DAOs for application data access)

"""

import os
import sys

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from model import (
	CarritoDAO,
	CategoriaDAO,
	ClienteDAO,
	DetalleCarritoDAO,
	DetallePedidoDAO,
	EnvioDAO,
	PagoDAO,
	PedidoDAO,
	ProductoDAO,
)

router = APIRouter()

if getattr(sys, 'frozen', False):
	BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath('.'))
else:
	BASE_PATH = os.path.abspath('.')

templates_path = os.path.join(BASE_PATH, 'templates')
templates = Jinja2Templates(directory=templates_path)


@router.get('/health')
def health_check():
	"""Check the health status of the Tiendo API.

	Returns:
	    dict: A dictionary containing:
	        - status (str): The health status of the API ('healthy')
	        - message (str): A descriptive message indicating the API is running

	"""
	return {'status': 'healthy', 'message': 'Tiendo API is running'}


@router.get('/', response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
	"""Handle the root endpoint request and return the index page.

	Args:
	    request: The incoming HTTP request object.

	Returns:
	    HTMLResponse: A template response containing the rendered index.html page.

	"""
	return templates.TemplateResponse('index.html', {'request': request})


@router.get('/user', response_class=HTMLResponse)
def read_user(request: Request):
	"""Render and return the user template with the request context.

	Args:
	    request (Request): The incoming HTTP request object used to provide context to the template.

	Returns:
	    TemplateResponse: A template response containing the rendered 'user.html' template.

	"""
	return templates.TemplateResponse('user.html', {'request': request})


@router.get('/cart', response_class=HTMLResponse)
def read_cart(request: Request):
	"""Render the shopping cart page.

	Args:
	    request (Request): The incoming HTTP request object.

	Returns:
	    TemplateResponse: The rendered 'cart.html' template with the request context.

	"""
	return templates.TemplateResponse('cart.html', {'request': request})


@router.get('/product', response_class=HTMLResponse)
def read_product(request: Request):
	"""Render the 'product.html' template in response to a request.

	Args:
	    request (Request): The incoming HTTP request object.

	Returns:
	    TemplateResponse: The rendered HTML response for the product page.

	"""
	return templates.TemplateResponse('product.html', {'request': request})


@router.get('/login-template', response_class=HTMLResponse)
def login_template(request: Request):
	"""Render the login page using the specified template.

	Args:
	    request (Request): The incoming HTTP request object.

	Returns:
	    TemplateResponse: The rendered 'login.html' template with the request context.

	"""
	return templates.TemplateResponse('login.html', {'request': request})


@router.get('/register-template', response_class=HTMLResponse)
def register_template(request: Request):
	"""Render the 'register.html' template in response to a request.

	Args:
	    request (Request): The incoming HTTP request object.

	Returns:
	    TemplateResponse: The rendered HTML template response.

	"""
	return templates.TemplateResponse('register.html', {'request': request})
