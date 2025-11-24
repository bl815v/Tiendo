import sys
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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

static_path = os.path.join(BASE_PATH, "view")

app.mount("/view", StaticFiles(directory=static_path), name="view")

# app.include_router(si)

@app.get("/")
def read_root() -> FileResponse:
    return FileResponse(os.path.join(static_path, "index.html"))
