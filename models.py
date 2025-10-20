import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


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


class MascotaBase(SQLModel):
    nombre: str
    especie: Kind
    raza: str | None = None
    edad: int
    sexo: str
    estado: bool = True


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
    refugio: "Refugio" = Relationship(back_populates="mascotas")
    historial: list["HistorialCuidado"] = Relationship(back_populates="mascota")
    adopciones: list["Adopcion"] = Relationship(back_populates="mascota")


class Adopcion(AdopcionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mascota_id: int = Field(foreign_key="mascota.id")
    refugio_id: int = Field(foreign_key="refugio.id")
    mascota: "Mascota" = Relationship(back_populates="adopciones")
    refugio: "Refugio" = Relationship(back_populates="adopciones")


class HistorialCuidado(HistorialCuidadoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mascota_id: int = Field(foreign_key="mascota.id")
    mascota: "Mascota" = Relationship(back_populates="historial")


# ---------- CREATE / UPDATE MODELS ----------
class RefugioCreate(RefugioBase):
    pass


class MascotaCreate(MascotaBase):
    refugio_id: int


class MascotaUpdate(MascotaBase):
    pass


class AdopcionCreate(AdopcionBase):
    mascota_id: int
    refugio_id: int


class HistorialCuidadoCreate(HistorialCuidadoBase):
    mascota_id: int
