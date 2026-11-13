"""Composition root: arma la app, crea tablas y sirve el frontend."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.infrastructure.db import create_tables, sembrar_demostracion
from backend.infrastructure.security import BcryptHasher
from backend.infrastructure.web import router

create_tables()
# Datos de ejemplo la primera vez: quien reciba el enlace ve un sistema EN USO,
# con números de verdad en el resumen, en vez de una pantalla en blanco.
sembrar_demostracion(BcryptHasher())

app = FastAPI(title="MVP")
app.include_router(router)

_FRONT = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(_FRONT)), name="static")


@app.get("/")
def index():
    return FileResponse(str(_FRONT / "index.html"))


# La PWA exige que el manifest y el service worker se sirvan desde la RAÍZ:
# el alcance de un service worker es la carpeta desde la que se sirve, y desde
# /static no podría controlar la página.
@app.get("/manifest.json")
def manifest():
    return FileResponse(str(_FRONT / "manifest.json"), media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(str(_FRONT / "sw.js"), media_type="text/javascript")
