# mascota.py
import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlmodel import select

from db import SessionDep
from models import Mascota, MascotaCreate, MascotaUpdate, Refugio, Kind
from supa.supabase import upload_to_bucket


router = APIRouter(prefix="/mascotas", tags=["mascotas"])


# -----------------------------
# Crear mascota (JSON)
# -----------------------------
@router.post(
    "/",
    response_model=Mascota,
    status_code=201,
    summary="Crear una mascota (JSON)",
)
async def create_mascota(new_mascota: MascotaCreate, session: SessionDep):
    refugio = await session.get(Refugio, new_mascota.refugio_id)
    if not refugio:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    mascota = Mascota.model_validate(new_mascota)
    session.add(mascota)
    await session.commit()
    await session.refresh(mascota)
    return mascota


# -----------------------------
# Listar mascotas con filtros
# -----------------------------
@router.get(
    "/",
    response_model=List[Mascota],
    summary="Listar mascotas",
)
async def list_mascotas(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    refugio_id: int | None = Query(None, description="Filtrar por refugio"),
    especie: Kind | None = Query(None, description="Filtrar por especie"),
    solo_activas: bool = Query(True, description="Si True, solo mascotas activas"),
    solo_con_foto: bool = Query(False, description="Si True, solo mascotas con foto"),
):
    stmt = select(Mascota)

    if refugio_id is not None:
        stmt = stmt.where(Mascota.refugio_id == refugio_id)
    if especie is not None:
        stmt = stmt.where(Mascota.especie == especie)
    if solo_activas:
        stmt = stmt.where(Mascota.estado == True)
    if solo_con_foto:
        stmt = stmt.where(Mascota.foto_url.is_not(None))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.exec(stmt)
    return result.all()


# -----------------------------
# Obtener una mascota por ID
# -----------------------------
@router.get(
    "/{mascota_id}",
    response_model=Mascota,
    summary="Obtener una mascota por ID",
)
async def get_mascota(mascota_id: int, session: SessionDep):
    mascota = await session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota


# -----------------------------
# Actualizar mascota (JSON)
# -----------------------------
@router.put(
    "/{mascota_id}",
    response_model=Mascota,
    summary="Actualizar una mascota",
)
async def update_mascota(
    mascota_id: int,
    mascota_update: MascotaUpdate,
    session: SessionDep,
):
    mascota_db = await session.get(Mascota, mascota_id)
    if not mascota_db:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    data = mascota_update.model_dump(exclude_unset=True)
    if data:
        # no tenemos campo updated_at en modelo, pero aquí podrías añadirlo si lo creas
        pass

    for key, value in data.items():
        setattr(mascota_db, key, value)

    session.add(mascota_db)
    await session.commit()
    await session.refresh(mascota_db)
    return mascota_db


# -----------------------------
# Inactivar mascota (soft delete)
# -----------------------------
@router.delete(
    "/{mascota_id}",
    response_model=Mascota,
    summary="Inactivar mascota (soft delete)",
)
async def delete_mascota(mascota_id: int, session: SessionDep):
    mascota = await session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    mascota.estado = False
    session.add(mascota)
    await session.commit()
    await session.refresh(mascota)
    return mascota


# -----------------------------
# Subir imagen de una mascota
# -----------------------------
@router.post(
    "/{mascota_id}/imagen",
    summary="Subir/actualizar imagen de una mascota",
)
async def upload_mascota_image(
    mascota_id: int,
    file: UploadFile = File(...),
    session: SessionDep = None,
):
    mascota = await session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    # Subir archivo a Supabase
    try:
        foto_url = await upload_to_bucket(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error subiendo imagen: {e}")

    # Guardar URL en la BD
    mascota.foto_url = foto_url
    session.add(mascota)
    await session.commit()
    await session.refresh(mascota)

    return {
        "mensaje": "Imagen de mascota subida/actualizada correctamente",
        "mascota_id": mascota_id,
        "foto_url": foto_url,
    }
