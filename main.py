# main.py
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, extract
import datetime

import refugio
import mascota
import historial
import adopcion

from db import create_tables, SessionDep
from models import Refugio, Mascota, Adopcion, HistorialCuidado, AdopcionCreate, HistorialCuidadoCreate


templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en Clever Cloud si no existen
    await create_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Adopciones API",
    version="1.0.0",
    description="API para gestionar refugios, mascotas, historiales de cuidado y adopciones.",
)

# Archivos estáticos (CSS, imágenes locales, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers de API (JSON)
app.include_router(refugio.router)
app.include_router(mascota.router)
app.include_router(historial.router)
app.include_router(adopcion.router)


# -------------------------------------------------------------------
# RUTAS WEB (HTML) - VISTAS CON JINJA2
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["web"])
async def home(request: Request):
    """
    Página de inicio web.
    """
    context = {
        "request": request,
        "app_name": "Refugios & Adopciones",
        "subtitle": "Gestión de refugios, mascotas, cuidados y adopciones",
        "active_page": "home",
    }
    return templates.TemplateResponse("home.html", context)


@app.get("/web/refugios", response_class=HTMLResponse, tags=["web"])
async def refugios_web(request: Request, session: SessionDep):
    """
    Vista web: listado de refugios.
    """
    result = await session.execute(select(Refugio))
    refugios = result.scalars().all()

    context = {
        "request": request,
        "refugios": refugios,
        "active_page": "refugios",
    }
    return templates.TemplateResponse("refugios_list.html", context)


@app.get("/web/mascotas", response_class=HTMLResponse, tags=["web"])
async def mascotas_web(
    request: Request,
    session: SessionDep,
    refugio_id: Optional[int] = None,
):
    """
    Vista web: listado de mascotas. Puede filtrarse opcionalmente por refugio.
    """
    stmt = (
        select(Mascota)
        .options(selectinload(Mascota.refugio))
        .order_by(Mascota.id)
    )

    if refugio_id is not None:
        stmt = stmt.where(Mascota.refugio_id == refugio_id)

    result = await session.execute(stmt)
    mascotas = result.scalars().all()
    refugio_result = await session.execute(select(Refugio).order_by(Refugio.nombre))
    refugios = refugio_result.scalars().all()

    context = {
        "request": request,
        "mascotas": mascotas,
        "refugio_id": refugio_id,
        "refugios": refugios,
        "active_page": "mascotas",
    }
    return templates.TemplateResponse("mascotas.html", context)


@app.get("/web/historial", response_class=HTMLResponse, tags=["web"])
async def historial_web(request: Request, session: SessionDep):
    """
    Vista web: historial de cuidados (listado simple).
    """
    stmt = (
        select(HistorialCuidado, Mascota.nombre, Refugio.nombre)
        .join(Mascota, HistorialCuidado.mascota_id == Mascota.id)
        .join(Refugio, Mascota.refugio_id == Refugio.id)
        .order_by(HistorialCuidado.fecha.desc())
        .limit(50)
    )
    result = await session.execute(stmt)
    rows = result.all()

    registros = [
        {
            "id": hc.id,
            "mascota_id": hc.mascota_id,
            "fecha": hc.fecha,
            "tipo_evento": hc.tipo_evento,
            "costo": hc.costo,
            "mascota": mascota_nombre,
            "refugio": refugio_nombre,
        }
        for hc, mascota_nombre, refugio_nombre in rows
    ]

    masc_result = await session.execute(select(Mascota).order_by(Mascota.nombre))
    mascotas = masc_result.scalars().all()

    context = {
        "request": request,
        "historial": registros,
        "mascotas": mascotas,
        "ok": request.query_params.get("ok"),
        "error": request.query_params.get("error"),
        "active_page": "historial",
    }
    return templates.TemplateResponse("historial.html", context)


@app.get("/web/adopciones", response_class=HTMLResponse, tags=["web"])
async def adopciones_web(request: Request, session: SessionDep):
    """
    Vista web: listado de adopciones (simple).
    """
    stmt = (
        select(Adopcion, Mascota.nombre, Refugio.nombre)
        .join(Mascota, Adopcion.mascota_id == Mascota.id)
        .join(Refugio, Adopcion.refugio_id == Refugio.id)
        .order_by(Adopcion.fecha_adopcion.desc())
        .limit(50)
    )
    result = await session.execute(stmt)
    rows = result.all()

    adopciones = [
        {
            "id": ad.id,
            "fecha_adopcion": ad.fecha_adopcion,
            "adoptante": ad.adoptante,
            "mascota": mascota_nombre,
            "refugio": refugio_nombre,
        }
        for ad, mascota_nombre, refugio_nombre in rows
    ]

    context = {
        "request": request,
        "adopciones": adopciones,
        "active_page": "adopciones",
        "ok": request.query_params.get("ok"),
        "error": request.query_params.get("error"),
    }
    return templates.TemplateResponse("adopciones.html", context)


@app.get("/web/dashboards", response_class=HTMLResponse, tags=["web"])
async def dashboards_web(request: Request, session: SessionDep):
    # A) Mascotas por refugio
    q_ref = (
        select(Refugio.nombre, func.count(Mascota.id))
        .join(Mascota, Mascota.refugio_id == Refugio.id, isouter=True)
        .group_by(Refugio.nombre)
        .order_by(Refugio.nombre)
    )
    res_ref = await session.execute(q_ref)
    data_mascotas_por_refugio = [
        {"refugio": r[0] or "Sin nombre", "total": int(r[1] or 0)}
        for r in res_ref.all()
    ]

    # B) Adopciones por mes (ultimos 5 anos)
    now = datetime.datetime.utcnow()
    start = (now.replace(day=1) - datetime.timedelta(days=365 * 5)).replace(day=1)
    q_adop = (
        select(
            extract("year", Adopcion.fecha_adopcion).label("y"),
            extract("month", Adopcion.fecha_adopcion).label("m"),
            func.count(Adopcion.id),
        )
        .where(Adopcion.fecha_adopcion >= start.date())
        .group_by("y", "m")
        .order_by("y", "m")
    )
    res_adop = await session.execute(q_adop)
    raw = res_adop.all()

    # Normalizar a 60 meses (5 anos)
    months = []
    current = start
    for _ in range(60):
        label = f"{current.year:04d}-{current.month:02d}"
        months.append(label)
        # avanzar 1 mes
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    totals_map = {f"{int(y):04d}-{int(m):02d}": int(c or 0) for y, m, c in raw}
    data_adopciones_por_mes = [
        {"label": label, "total": totals_map.get(label, 0)} for label in months
    ]

    context = {
        "request": request,
        "data_mascotas_por_refugio": data_mascotas_por_refugio,
        "data_adopciones_por_mes": data_adopciones_por_mes,
        "active_page": "dashboards",
    }
    return templates.TemplateResponse("dashboards.html", context)


@app.post("/web/adopciones/crear", tags=["web"])
async def crear_adopcion_web(request: Request, session: SessionDep):
    form = await request.form()
    try:
        mascota_id = int(form.get("mascota_id", ""))
        refugio_id = int(form.get("refugio_id", ""))
        adoptante = form.get("adoptante", "").strip()
        fecha_adopcion = form.get("fecha_adopcion", "").strip()
        if not adoptante or not fecha_adopcion:
            raise HTTPException(status_code=400, detail="Adoptante y fecha son obligatorios")
        payload = AdopcionCreate(
            mascota_id=mascota_id,
            refugio_id=refugio_id,
            adoptante=adoptante,
            fecha_adopcion=fecha_adopcion,
        )
        await adopcion.create_adopcion(payload, session)
        target = request.url_for("adopciones_web")
        return RedirectResponse(f"{target}?ok=1", status_code=303)
    except HTTPException as exc:
        target = request.url_for("adopciones_web")
        return RedirectResponse(f"{target}?error={exc.detail}", status_code=303)


@app.post("/web/historial/registrar", tags=["web"])
async def registrar_historial_web(request: Request, session: SessionDep):
    form = await request.form()
    try:
        mascota_id = int(form.get("mascota_id", ""))
        tipo_evento = (form.get("tipo_evento") or "").strip()
        costo = float(form.get("costo", "0"))
        fecha = form.get("fecha") or None
        if not tipo_evento:
            raise HTTPException(status_code=400, detail="El tipo de evento es obligatorio")
        payload = HistorialCuidadoCreate(
            mascota_id=mascota_id,
            tipo_evento=tipo_evento,
            costo=costo,
            fecha=fecha,
        )
        await historial.create_historial(payload, session)
        target = request.url_for("historial_web")
        return RedirectResponse(f"{target}?ok=1", status_code=303)
    except HTTPException as exc:
        target = request.url_for("historial_web")
        return RedirectResponse(f"{target}?error={exc.detail}", status_code=303)


@app.get("/web/historial/mascota/{mascota_id}", response_class=HTMLResponse, tags=["web"])
async def historial_por_mascota_web(request: Request, mascota_id: int, session: SessionDep):
    stmt = (
        select(HistorialCuidado, Mascota.nombre, Refugio.nombre)
        .join(Mascota, HistorialCuidado.mascota_id == Mascota.id)
        .join(Refugio, Mascota.refugio_id == Refugio.id)
        .where(HistorialCuidado.mascota_id == mascota_id)
        .order_by(HistorialCuidado.fecha.desc())
    )
    result = await session.execute(stmt)
    rows = result.all()

    eventos = [
        {
            "id": hc.id,
            "fecha": hc.fecha,
            "tipo_evento": hc.tipo_evento,
            "costo": hc.costo,
            "mascota": mascota_nombre,
            "refugio": refugio_nombre,
        }
        for hc, mascota_nombre, refugio_nombre in rows
    ]

    costo_total = await session.execute(
        select(HistorialCuidado).where(HistorialCuidado.mascota_id == mascota_id)
    )
    eventos_raw = costo_total.scalars().all()
    total = sum(e.costo for e in eventos_raw)

    context = {
        "request": request,
        "eventos": eventos,
        "total": total,
        "mascota_id": mascota_id,
        "active_page": "historial",
    }
    return templates.TemplateResponse("historial_detalle.html", context)


# Manejador de errores (HTML) sencillo
from fastapi import HTTPException


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
        status_code=exc.status_code,
    )
