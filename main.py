import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
# from controller import root_router

app = FastAPI(
    title="Tiendo",
    description="Basic international virtual store",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if getattr(sys, 'frozen', False):
    BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath("."))
else:
    BASE_PATH = os.path.abspath(".")

static_path = os.path.join(BASE_PATH, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates_path = os.path.join(BASE_PATH, "templates")
templates = Jinja2Templates(directory=templates_path)

# app.include_router(si)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/user", response_class=HTMLResponse)
def read_user(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

@app.get("/cart", response_class=HTMLResponse)
def read_cart(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})

@app.get("/product", response_class=HTMLResponse)
def read_product(request: Request):
    return templates.TemplateResponse("product.html", {"request": request})

@app.get("/login-template")
def login_template(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register-template")
def register_template(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
