from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated

db_name = "adopciones.sqlite3"
db_url = f"sqlite:///{db_name}"

engine = create_engine(db_url, echo=False)

def create_tables(app: FastAPI):
    print("🔧 Creando tablas (si no existen)...")
    SQLModel.metadata.create_all(engine)
    yield

def get_session() -> Session:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
