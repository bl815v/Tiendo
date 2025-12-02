import sys
import os
import time
import secrets
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

if getattr(sys, "frozen", False):
    BASE_PATH = getattr(sys, "_MEIPASS", os.path.abspath("."))
else:
    BASE_PATH = os.path.abspath(".")

templates_path = os.path.join(BASE_PATH, "templates")
templates = Jinja2Templates(directory=templates_path)

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

admin_sessions = {}


def require_admin_auth(request: Request):
    session_id = request.cookies.get("admin_session")

    if not session_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No autenticado")

    session_data = admin_sessions.get(session_id)
    if not session_data:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Sesión inválida")

    if time.time() - session_data.get("created_at", 0) > 3600:
        del admin_sessions[session_id]
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Sesión expirada")

    return session_data


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.post("/admin/login")
async def admin_login_post(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    if not ADMIN_USER or not ADMIN_PASS:
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Error de configuración del servidor"},
        )

    if username == ADMIN_USER and password == ADMIN_PASS:
        session_id = secrets.token_urlsafe(32)
        admin_sessions[session_id] = {
            "username": username,
            "created_at": time.time(),
            "ip": request.client.host if request.client else "unknown",
        }

        response = RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
        response.set_cookie(
            key="admin_session",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600,
        )
        return response

    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Usuario o contraseña incorrectos"},
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_index(request: Request):
    try:
        session_data = require_admin_auth(request)
    except HTTPException:
        return RedirectResponse(url="admin/login", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        "admin_index.html",
        {"request": request, "username": session_data.get("username", "Admin")},
    )


@router.get("/admin/check-session")
def check_session(request: Request):
    try:
        session_data = require_admin_auth(request)
        return JSONResponse({"status": "ok", "username": session_data.get("username")})
    except HTTPException:
        return JSONResponse(
            {"status": "error", "message": "Sesión inválida"}, status_code=401
        )


@router.post("/admin/logout")
async def admin_logout(request: Request):
    session_id = request.cookies.get("admin_session")

    if session_id in admin_sessions:
        del admin_sessions[session_id]

    response = RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    response.delete_cookie(key="admin_session")
    return response


@router.get("/admin/products", response_class=HTMLResponse)
def admin_products(request: Request):
    require_admin_auth(request)
    return templates.TemplateResponse("admin_products.html", {"request": request})
