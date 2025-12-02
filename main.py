# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import create_tables
import refugio, mascota, historial, adopcion


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar la app
    await create_tables()
    yield
    # Aquí podrías cerrar recursos si fuera necesario al apagar la app


app = FastAPI(
    lifespan=lifespan,
    title="Adopciones API",
    version="1.0.0",
)

app.include_router(refugio.router)
app.include_router(mascota.router)
app.include_router(historial.router)
app.include_router(historial.router)
app.include_router(adopcion.router)


@app.get("/")
async def root():
    return {"message": "API de Adopciones y Cuidado de Mascotas funcionando correctamente 🐾"}
