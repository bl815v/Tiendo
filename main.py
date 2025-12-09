"""Main entry point for the Tiendo application.

This module initializes the FastAPI app, sets up middleware, includes routers for API, admin, and
client functionalities, and creates database tables using SQLAlchemy ORM.

Attributes:
    app (FastAPI): The FastAPI application instance.

Routers:
    /api/v1: API endpoints for core functionalities.
    /admin: Administrative endpoints.
    /client: Client-facing endpoints.

Middleware:
    CORSMiddleware: Enables Cross-Origin Resource Sharing for all origins, methods, and headers.

Database:
    Base.metadata.create_all(bind=engine): Creates all tables defined in SQLAlchemy models.

Usage:
    Run this module to start the Tiendo web application.

"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from controller.admin_routers import router as admin_router
from controller.api_routers import router as api_router
from controller.client_routers import router as client_router
from data.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
	title='Tiendo',
	description='Basic international virtual store',
	version='0.1.0',
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
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

app.include_router(api_router, prefix='/api/v1')
app.include_router(admin_router)
app.include_router(client_router)
