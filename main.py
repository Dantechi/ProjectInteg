# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from db import create_tables
import refugio
import mascota
import historial
import adopcion
import upload
import stats  # <-- NUEVO


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Adopciones API",
    version="2.0.0",
    description="API para gestión de refugios, mascotas, adopciones, historial y estadísticas.",
)

app.include_router(refugio.router)
app.include_router(mascota.router)
app.include_router(historial.router)
app.include_router(adopcion.router)
app.include_router(upload.router)
app.include_router(stats.router)


@app.get("/", tags=["healthcheck"])
async def root():
    return {"message": "API de Adopciones y Cuidado de Mascotas funcionando correctamente 🐾"}
