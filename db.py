# db.py
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # <- NUEVO

# 1. Cargar variables de entorno desde .env
load_dotenv()

# 2. Construir la URL de conexión a Clever Cloud
CLEVER_DB = (
    f"postgresql+asyncpg://{os.getenv('POSTGRESQL_ADDON_USER')}:"
    f"{os.getenv('POSTGRESQL_ADDON_PASSWORD')}@"
    f"{os.getenv('POSTGRESQL_ADDON_HOST')}:"
    f"{os.getenv('POSTGRESQL_ADDON_PORT')}/"
    f"{os.getenv('POSTGRESQL_ADDON_DB')}"
)

# 3. Crear el engine asíncrono, sin pool persistente
engine: AsyncEngine = create_async_engine(
    CLEVER_DB,
    echo=True,
    future=True,
    poolclass=NullPool,   # <- aquí la clave
)

# 4. Crear el sessionmaker para AsyncSession
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# 5. Función para crear tablas al inicio de la app
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# 6. Dependencia para obtener una sesión por request
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
