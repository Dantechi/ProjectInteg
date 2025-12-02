# adopcion.py
from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from db import SessionDep
from models import Adopcion, AdopcionCreate, Mascota, Refugio

router = APIRouter(prefix="/adopciones", tags=["adopciones"])


@router.post(
    "/",
    response_model=Adopcion,
    status_code=201,
    summary="Registrar una adopción",
)
async def create_adopcion(new_adopcion: AdopcionCreate, session: SessionDep):
    mascota = await session.get(Mascota, new_adopcion.mascota_id)
    refugio = await session.get(Refugio, new_adopcion.refugio_id)

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    if not refugio:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    if not mascota.estado:
        raise HTTPException(status_code=400, detail="La mascota ya no está disponible para adopción")

    adopcion = Adopcion.model_validate(new_adopcion)
    session.add(adopcion)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="La mascota ya tiene una adopción registrada")

    await session.refresh(adopcion)

    # marcar mascota como no disponible
    mascota.estado = False
    session.add(mascota)
    await session.commit()
    await session.refresh(mascota)

    return adopcion


@router.get(
    "/",
    response_model=List[Adopcion],
    summary="Listar adopciones con filtros",
)
async def list_adopciones(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    anio: int | None = Query(None, description="Filtrar por año"),
    refugio_id: int | None = Query(None, description="Filtrar por refugio"),
    mascota_id: int | None = Query(None, description="Filtrar por mascota"),
):
    stmt = select(Adopcion)

    if anio is not None:
        stmt = stmt.where(
            Adopcion.fecha_adopcion.between(f"{anio}-01-01", f"{anio}-12-31")
        )

    if refugio_id is not None:
        stmt = stmt.where(Adopcion.refugio_id == refugio_id)

    if mascota_id is not None:
        stmt = stmt.where(Adopcion.mascota_id == mascota_id)

    stmt = stmt.offset(skip).limit(limit)
    result = await session.exec(stmt)
    return result.all()
