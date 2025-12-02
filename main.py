# main.py
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlmodel import select

import refugio
import mascota
import historial
import adopcion

from db import create_tables, SessionDep
from models import Refugio, Mascota


templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en Clever Cloud si no existen
    await create_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Adopciones API",
    version="1.0.0",
    description="API para gestionar refugios, mascotas, historiales de cuidado y adopciones.",
)

# Archivos estáticos (CSS, imágenes locales, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers de API (JSON)
app.include_router(refugio.router)
app.include_router(mascota.router)
app.include_router(historial.router)
app.include_router(adopcion.router)


# -------------------------------------------------------------------
# RUTAS WEB (HTML) - VISTAS CON JINJA2
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["web"])
async def home(request: Request):
    """
    Página de inicio web.
    """
    context = {
        "request": request,
        "app_name": "Refugios & Adopciones",
        "subtitle": "Gestión de refugios, mascotas, cuidados y adopciones",
        "active_page": "home",
    }
    return templates.TemplateResponse("home.html", context)


@app.get("/web/refugios", response_class=HTMLResponse, tags=["web"])
async def refugios_web(request: Request, session: SessionDep):
    """
    Vista web: listado de refugios.
    """
    result = await session.exec(select(Refugio))
    refugios = result.all()

    context = {
        "request": request,
        "refugios": refugios,
        "active_page": "refugios",
    }
    return templates.TemplateResponse("refugios_list.html", context)


@app.get("/web/mascotas", response_class=HTMLResponse, tags=["web"])
async def mascotas_web(
    request: Request,
    session: SessionDep,
    refugio_id: Optional[int] = None,
):
    """
    Vista web: listado de mascotas. Puede filtrarse opcionalmente por refugio.
    """
    stmt = select(Mascota)

    if refugio_id is not None:
        stmt = stmt.where(Mascota.refugio_id == refugio_id)

    result = await session.exec(stmt)
    mascotas = result.all()

    context = {
        "request": request,
        "mascotas": mascotas,
        "refugio_id": refugio_id,
        "active_page": "mascotas",
    }
    return templates.TemplateResponse("mascotas_list.html", context)


# Manejador de errores (HTML) sencillo
from fastapi import HTTPException


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
        status_code=exc.status_code,
    )
