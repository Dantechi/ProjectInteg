# stats.py
from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter
from sqlmodel import select

from db import SessionDep
from models import Refugio, Mascota, Adopcion, HistorialCuidado, Kind

router = APIRouter(prefix="/stats", tags=["estadisticas"])


@router.get(
    "/resumen-general",
    summary="Resumen general de la plataforma",
)
async def resumen_general(session: SessionDep) -> Dict:
    # Refugios
    ref_result = await session.exec(select(Refugio))
    refugios = ref_result.all()
    total_refugios = len(refugios)

    # Mascotas
    masc_result = await session.exec(select(Mascota))
    mascotas = masc_result.all()
    total_mascotas = len(mascotas)
    mascotas_activas = sum(1 for m in mascotas if m.estado)
    mascotas_inactivas = total_mascotas - mascotas_activas

    # Adopciones
    adop_result = await session.exec(select(Adopcion))
    adopciones = adop_result.all()
    total_adopciones = len(adopciones)

    # Historial de cuidado
    hist_result = await session.exec(select(HistorialCuidado))
    eventos = hist_result.all()
    costo_total_cuidados = sum(e.costo for e in eventos)

    # Distribución de mascotas por especie
    por_especie: dict[str, int] = {}
    for m in mascotas:
        por_especie[m.especie.value] = por_especie.get(m.especie.value, 0) + 1

    return {
        "refugios": {
            "total": total_refugios,
        },
        "mascotas": {
            "total": total_mascotas,
            "activas": mascotas_activas,
            "inactivas": mascotas_inactivas,
            "por_especie": por_especie,
        },
        "adopciones": {
            "total": total_adopciones,
        },
        "cuidados": {
            "total_eventos": len(eventos),
            "costo_total": costo_total_cuidados,
        },
    }


@router.get(
    "/adopciones-por-anio",
    summary="Adopciones agrupadas por año",
)
async def adopciones_por_anio(session: SessionDep) -> List[Dict]:
    adop_result = await session.exec(select(Adopcion))
    adopciones = adop_result.all()

    conteo_por_anio: dict[int, int] = defaultdict(int)
    for a in adopciones:
        if a.fecha_adopcion:
            conteo_por_anio[a.fecha_adopcion.year] += 1

    return [
        {"anio": anio, "total_adopciones": total}
        for anio, total in sorted(conteo_por_anio.items())
    ]
