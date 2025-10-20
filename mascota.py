from fastapi import APIRouter, HTTPException
from models import Mascota, MascotaCreate, MascotaUpdate, Refugio
from db import SessionDep

router = APIRouter(prefix="/mascotas", tags=["mascota"])

@router.post("/", response_model=Mascota)
async def create_mascota(new_mascota: MascotaCreate, session: SessionDep):
    refugio = session.get(Refugio, new_mascota.refugio_id)
    if not refugio:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    mascota = Mascota.model_validate(new_mascota)
    session.add(mascota)
    session.commit()
    session.refresh(mascota)
    return mascota

@router.get("/", response_model=list[Mascota])
async def all_mascotas(session: SessionDep):
    return session.query(Mascota).all()

@router.get("/{mascota_id}", response_model=Mascota)
async def get_mascota(mascota_id: int, session: SessionDep):
    mascota = session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota

@router.put("/{mascota_id}", response_model=Mascota)
async def update_mascota(mascota_id: int, mascota_update: MascotaUpdate, session: SessionDep):
    mascota = session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    for key, value in mascota_update.dict(exclude_unset=True).items():
        setattr(mascota, key, value)
    session.add(mascota)
    session.commit()
    session.refresh(mascota)
    return mascota

@router.delete("/{mascota_id}", response_model=Mascota)
async def delete_mascota(mascota_id: int, session: SessionDep):
    mascota = session.get(Mascota, mascota_id)
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    mascota.estado = False
    session.add(mascota)
    session.commit()
    session.refresh(mascota)
    return mascota
