from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models import Refugio, RefugioCreate
from db import SessionDep

router = APIRouter(prefix="/refugios", tags=["refugio"])


@router.post("/", response_model=Refugio)
async def create_refugio(new_refugio: RefugioCreate, session: SessionDep):
    refugio = Refugio.model_validate(new_refugio)
    session.add(refugio)
    await session.commit()
    await session.refresh(refugio)
    return refugio


@router.get("/", response_model=list[Refugio])
async def all_refugios(session: SessionDep):
    statement = select(Refugio)
    result = await session.exec(statement)
    return result.all()


@router.get("/{refugio_id}", response_model=Refugio)
async def get_refugio(refugio_id: int, session: SessionDep):
    refugio_db = await session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    return refugio_db
