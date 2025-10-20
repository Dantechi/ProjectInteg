from fastapi import APIRouter, HTTPException
from models import Adopcion, AdopcionCreate, Mascota, Refugio
from db import SessionDep

router = APIRouter(prefix="/adopciones", tags=["adopcion"])

@router.post("/", response_model=Adopcion)
async def create_adopcion(new_adopcion: AdopcionCreate, session: SessionDep):
    mascota = session.get(Mascota, new_adopcion.mascota_id)
    refugio = session.get(Refugio, new_adopcion.refugio_id)
    if not mascota or not refugio:
        raise HTTPException(status_code=404, detail="Mascota o Refugio no encontrado")
    adopcion = Adopcion.model_validate(new_adopcion)
    session.add(adopcion)
    session.commit()
    session.refresh(adopcion)
    return adopcion

@router.get("/", response_model=list[Adopcion])
async def all_adopciones(session: SessionDep):
    return session.query(Adopcion).all()

@router.get("/por-anio/{anio}", response_model=list[Adopcion])
async def adopciones_por_anio(anio: int, session: SessionDep):
    return session.query(Adopcion).filter(Adopcion.fecha_adopcion.like(f"{anio}-%")).all()
