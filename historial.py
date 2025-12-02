# historial.py
from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from db import SessionDep
from models import HistorialCuidado, HistorialCuidadoCreate, Mascota

router = APIRouter(prefix="/historial", tags=["historial"])


@router.post(
    "/",
    response_model=HistorialCuidado,
    status_code=201,
    summary="Registrar un evento de cuidado",
)
async def create_historial(new_historial: HistorialCuidadoCreate, session: SessionDep):
    mascota = await session.get(Mascota, new_historial.mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    historial = HistorialCuidado.model_validate(new_historial)
    session.add(historial)
    await session.commit()
    await session.refresh(historial)
    return historial


@router.get(
    "/mascota/{mascota_id}",
    response_model=List[HistorialCuidado],
    summary="Ver historial de una mascota",
)
async def historial_by_mascota(
    mascota_id: int,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = (
        select(HistorialCuidado)
        .where(HistorialCuidado.mascota_id == mascota_id)
        .order_by(HistorialCuidado.fecha.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(stmt)
    return result.all()


@router.get(
    "/mascota/{mascota_id}/costo-total",
    summary="Ver costo total de cuidado de una mascota",
)
async def costo_total_mascota(mascota_id: int, session: SessionDep):
    mascota = await session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    stmt = select(HistorialCuidado).where(HistorialCuidado.mascota_id == mascota_id)
    result = await session.exec(stmt)
    eventos = result.all()
    total = sum(e.costo for e in eventos)

    return {
        "mascota_id": mascota_id,
        "mascota_nombre": mascota.nombre,
        "total_eventos": len(eventos),
        "costo_total": total,
    }
