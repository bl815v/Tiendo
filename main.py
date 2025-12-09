import os
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from controller.admin_routers import router as admin_router
from controller.routers import router as api_router
from data.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
	title='Tiendo',
	description='Basic international virtual store',
	version='0.1.0',
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

if getattr(sys, 'frozen', False):
	BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath('.'))
else:
	BASE_PATH = os.path.abspath('.')

static_path = os.path.join(BASE_PATH, 'static')
app.mount('/static', StaticFiles(directory=static_path), name='static')

templates_path = os.path.join(BASE_PATH, 'templates')
templates = Jinja2Templates(directory=templates_path)

app.include_router(api_router, prefix='/api/v1')
app.include_router(admin_router)


@app.get('/health')
def health_check():
	return {'status': 'healthy', 'message': 'Tiendo API is running'}


@app.get('/', response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
	return templates.TemplateResponse('index.html', {'request': request})


@app.get('/user', response_class=HTMLResponse)
def read_user(request: Request):
	return templates.TemplateResponse('user.html', {'request': request})


@app.get('/cart', response_class=HTMLResponse)
def read_cart(request: Request):
	return templates.TemplateResponse('cart.html', {'request': request})


@app.get('/product', response_class=HTMLResponse)
def read_product(request: Request):
	return templates.TemplateResponse('product.html', {'request': request})


@app.get('/login-template', response_class=HTMLResponse)
def login_template(request: Request):
	return templates.TemplateResponse('login.html', {'request': request})


@app.get('/register-template', response_class=HTMLResponse)
def register_template(request: Request):
	return templates.TemplateResponse('register.html', {'request': request})
