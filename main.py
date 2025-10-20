from fastapi import FastAPI
from db import create_tables
import refugio, mascota, historial, adopcion

app = FastAPI(lifespan=create_tables, title="Adopciones API", version="1.0.0")

app.include_router(refugio.router)
app.include_router(mascota.router)
app.include_router(historial.router)
app.include_router(adopcion.router)

@app.get("/")
async def root():
    return {"message": "API de Adopciones y Cuidado de Mascotas funcionando correctamente 🐾"}
