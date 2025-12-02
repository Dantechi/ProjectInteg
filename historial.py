from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models import HistorialCuidado, HistorialCuidadoCreate, Mascota
from db import SessionDep

router = APIRouter(prefix="/historial", tags=["historial"])


@router.post("/", response_model=HistorialCuidado)
async def create_historial(new_historial: HistorialCuidadoCreate, session: SessionDep):
    mascota = await session.get(Mascota, new_historial.mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    historial = HistorialCuidado.model_validate(new_historial)
    session.add(historial)
    await session.commit()
    await session.refresh(historial)
    return historial


@router.get("/mascota/{mascota_id}", response_model=list[HistorialCuidado])
async def historial_by_mascota(mascota_id: int, session: SessionDep):
    statement = select(HistorialCuidado).where(HistorialCuidado.mascota_id == mascota_id)
    result = await session.exec(statement)
    return result.all()
