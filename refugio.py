from fastapi import APIRouter, HTTPException
from models import Refugio, RefugioCreate
from db import SessionDep

router = APIRouter(prefix="/refugios", tags=["refugio"])

@router.post("/", response_model=Refugio)
async def create_refugio(new_refugio: RefugioCreate, session: SessionDep):
    refugio = Refugio.model_validate(new_refugio)
    session.add(refugio)
    session.commit()
    session.refresh(refugio)
    return refugio


@router.get("/", response_model=list[Refugio])
async def all_refugios(session: SessionDep):
    return session.query(Refugio).all()


@router.get("/{refugio_id}", response_model=Refugio)
async def get_refugio(refugio_id: int, session: SessionDep):
    refugio_db = session.get(Refugio, refugio_id)
    if not refugio_db:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    return refugio_db
