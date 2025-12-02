# models.py
import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


# ---------- ENUM ----------

class Kind(str, Enum):
    Dog = "Dog"
    Cat = "Cat"
    Rabbit = "Rabbit"
    Bird = "Bird"


# ---------- BASE MODELS ----------

class RefugioBase(SQLModel):
    nombre: str
    ubicacion: str
    activo: bool = True
    foto_url: str | None = Field(default=None, description="Foto del refugio (URL en Supabase)")


class MascotaBase(SQLModel):
    nombre: str
    especie: Kind
    raza: str | None = None
    edad: int
    sexo: str
    estado: bool = True
    foto_url: str | None = Field(default=None, description="Foto de la mascota (URL en Supabase)")


class AdopcionBase(SQLModel):
    adoptante: str
    fecha_adopcion: datetime.date


class HistorialCuidadoBase(SQLModel):
    tipo_evento: str
    costo: float
    fecha: datetime.date = Field(default_factory=lambda: datetime.date.today())


# ---------- TABLE MODELS ----------

class Refugio(RefugioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    mascotas: list["Mascota"] = Relationship(back_populates="refugio")
    adopciones: list["Adopcion"] = Relationship(back_populates="refugio")


class Mascota(MascotaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    refugio_id: int = Field(foreign_key="refugio.id")

    refugio: Refugio = Relationship(back_populates="mascotas")
    historial: list["HistorialCuidado"] = Relationship(back_populates="mascota")
    adopciones: list["Adopcion"] = Relationship(back_populates="mascota")


class Adopcion(AdopcionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mascota_id: int = Field(foreign_key="mascota.id")
    refugio_id: int = Field(foreign_key="refugio.id")

    mascota: Mascota = Relationship(back_populates="adopciones")
    refugio: Refugio = Relationship(back_populates="adopciones")


class HistorialCuidado(HistorialCuidadoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mascota_id: int = Field(foreign_key="mascota.id")

    mascota: Mascota = Relationship(back_populates="historial")


# ---------- MODELOS DE ENTRADA / ACTUALIZACIÓN ----------

class RefugioCreate(RefugioBase):
    """Datos para crear un refugio."""
    pass


class RefugioUpdate(SQLModel):
    nombre: str | None = None
    ubicacion: str | None = None
    activo: bool | None = None
    foto_url: str | None = None


class MascotaCreate(MascotaBase):
    """Datos para crear una mascota."""
    refugio_id: int


class MascotaUpdate(SQLModel):
    """Campos opcionales para actualizar una mascota."""
    nombre: str | None = None
    especie: Kind | None = None
    raza: str | None = None
    edad: int | None = None
    sexo: str | None = None
    estado: bool | None = None
    foto_url: str | None = None
    refugio_id: int | None = None


class AdopcionCreate(AdopcionBase):
    mascota_id: int
    refugio_id: int


class HistorialCuidadoCreate(HistorialCuidadoBase):
    mascota_id: int
