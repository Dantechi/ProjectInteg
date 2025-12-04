# refugio.py
from typing import List

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlmodel import select

from db import SessionDep
from models import Refugio, RefugioCreate, RefugioUpdate, Mascota
from supa.supabase import upload_to_bucket


router = APIRouter(prefix="/refugios", tags=["refugios"])


@router.post(
    "/",
    response_model=Refugio,
    status_code=201,
    summary="Crear un refugio",
)
async def create_refugio(new_refugio: RefugioCreate, session: SessionDep):
    refugio = Refugio.model_validate(new_refugio)
    session.add(refugio)
    await session.commit()
    await session.refresh(refugio)
    return refugio


@router.get(
    "/",
    response_model=List[Refugio],
    summary="Listar refugios",
)
async def list_refugios(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    solo_activos: bool = Query(True, description="Si True, solo refugios activos"),
):
    try:
        stmt = select(Refugio)
        if solo_activos:
            stmt = stmt.where(Refugio.activo == True)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception:
        # No exponemos detalles sensibles, solo indicamos que hubo un fallo.
        raise HTTPException(status_code=500, detail="Error al obtener refugios")


@router.get(
    "/{refugio_id}",
    response_model=Refugio,
    summary="Obtener un refugio por ID",
)
async def get_refugio(refugio_id: int, session: SessionDep):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    return refugio_db


@router.put(
    "/{refugio_id}",
    response_model=Refugio,
    summary="Actualizar un refugio",
)
async def update_refugio(
    refugio_id: int,
    refugio_data: RefugioUpdate,
    session: SessionDep,
):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    update_data = refugio_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(refugio_db, key, value)

    session.add(refugio_db)
    await session.commit()
    await session.refresh(refugio_db)
    return refugio_db


@router.delete(
    "/{refugio_id}",
    response_model=Refugio,
    summary="Desactivar (soft delete) un refugio",
)
async def delete_refugio(refugio_id: int, session: SessionDep):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    refugio_db.activo = False
    session.add(refugio_db)
    await session.commit()
    await session.refresh(refugio_db)
    return refugio_db


# -----------------------------
# Listar mascotas de un refugio
# -----------------------------
@router.get(
    "/{refugio_id}/mascotas",
    response_model=List[Mascota],
    summary="Listar mascotas de un refugio",
)
async def list_mascotas_refugio(
    refugio_id: int,
    session: SessionDep,
):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    stmt = select(Mascota).where(Mascota.refugio_id == refugio_id)
    result = await session.execute(stmt)
    return result.scalars().all()


# -----------------------------
# Subir imagen de un refugio
# -----------------------------
@router.post(
    "/{refugio_id}/imagen",
    summary="Subir/actualizar imagen de un refugio",
)
async def upload_refugio_image(
    refugio_id: int,
    file: UploadFile = File(...),
    session: SessionDep = None,
):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    # Subir archivo a Supabase
    try:
        foto_url = await upload_to_bucket(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error subiendo imagen: {e}")

    refugio_db.foto_url = foto_url
    session.add(refugio_db)
    await session.commit()
    await session.refresh(refugio_db)

    return {
        "mensaje": "Imagen de refugio subida/actualizada correctamente",
        "refugio_id": refugio_id,
        "foto_url": foto_url,
    }
