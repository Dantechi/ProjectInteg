from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models import Adopcion, AdopcionCreate, Mascota, Refugio
from db import SessionDep

router = APIRouter(prefix="/adopciones", tags=["adopcion"])


@router.post("/", response_model=Adopcion)
async def create_adopcion(new_adopcion: AdopcionCreate, session: SessionDep):
    mascota = await session.get(Mascota, new_adopcion.mascota_id)
    refugio = await session.get(Refugio, new_adopcion.refugio_id)

    if not mascota or not refugio:
        raise HTTPException(status_code=404, detail="Mascota o Refugio no encontrado")

    adopcion = Adopcion.model_validate(new_adopcion)
    session.add(adopcion)
    await session.commit()
    await session.refresh(adopcion)
    return adopcion


@router.get("/", response_model=list[Adopcion])
async def all_adopciones(session: SessionDep):
    statement = select(Adopcion)
    result = await session.exec(statement)
    return result.all()


@router.get("/por-anio/{anio}", response_model=list[Adopcion])
async def adopciones_por_anio(anio: int, session: SessionDep):
    # filtrar por año usando LIKE sobre la fecha_adopcion
    statement = select(Adopcion).where(
        Adopcion.fecha_adopcion.like(f"{anio}-%")
    )
    result = await session.exec(statement)
    return result.all()
