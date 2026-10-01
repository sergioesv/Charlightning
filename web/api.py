"""
La página web de Charlightning: la API y las páginas estáticas en un solo servicio.

Arranque (local o en Railway):
    uvicorn web.api:app --host 0.0.0.0 --port 8000

Las rutas solo traducen HTTP <-> servicio.py; los números salen de calculate_risk/.
"""
import json
import os
import threading
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")      # el servidor no tiene pantalla

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from web import servicio
from web.limite import Limite

MAX_BYTES = 200_000                  # un caso real pesa unos pocos kB
CARPETA_ESTATICA = Path(__file__).resolve().parent / "estatico"
VERSION = "0.1.0"
COMMIT = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")[:7]

app = FastAPI(title="Charlightning", version=VERSION, docs_url="/api/docs",
              redoc_url=None, openapi_url="/api/openapi.json")

limite_calculo = Limite(maximo=int(os.environ.get("LIMITE_CALCULOS", 30)), segundos=60)
limite_informe = Limite(maximo=int(os.environ.get("LIMITE_INFORMES", 5)), segundos=60)

# matplotlib (pyplot) no se lleva bien con dos hilos dibujando a la vez.
_un_informe_a_la_vez = threading.Lock()


def _cliente(request: Request) -> str:
    """La IP de quien llama. Detrás del proxy de Railway viene en las cabeceras."""
    real = request.headers.get("x-real-ip")
    if real:
        return real.strip()
    reenviada = request.headers.get("x-forwarded-for")
    if reenviada:
        return reenviada.split(",")[-1].strip()
    return request.client.host if request.client else "desconocido"


def _revisar_limite(limite: Limite, request: Request):
    if not limite.permitir(_cliente(request)):
        raise HTTPException(429, "Demasiadas peticiones seguidas; espere un minuto.")


async def _leer_json(request: Request) -> dict:
    cuerpo = await request.body()
    if len(cuerpo) > MAX_BYTES:
        raise HTTPException(413, "El caso es demasiado grande.")
    try:
        return json.loads(cuerpo)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HTTPException(400, f"El cuerpo no es JSON válido: {error}") from error


@app.exception_handler(servicio.CasoInvalido)
async def _caso_invalido(_request: Request, error: servicio.CasoInvalido):
    return JSONResponse(status_code=422, content={"detail": str(error)})


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.get("/api/salud")
def salud():
    return {"estado": "ok", "version": VERSION, "commit": COMMIT}


@app.post("/api/evaluar")
async def evaluar(request: Request):
    """El JSON de un caso (mismo formato que casos/*.json) -> R1..R4 y avisos."""
    _revisar_limite(limite_calculo, request)
    datos = await _leer_json(request)
    return await run_in_threadpool(servicio.evaluar, datos)


@app.get("/api/ng")
def n_g(request: Request,
        lat: float = Query(..., ge=-90, le=90),
        lon: float = Query(..., ge=-360, le=360),
        fraccion: float = Query(None, gt=0, le=1)):
    """N_G en unas coordenadas, desde la climatología LIS/OTD de la NASA."""
    _revisar_limite(limite_calculo, request)
    return servicio.densidad_en(lat, lon, fraccion)


@app.post("/api/informe")
async def informe(request: Request, medidas: bool = True):
    """{"caso": {...}, "proyecto": {...}} -> la memoria de cálculo en PDF."""
    _revisar_limite(limite_informe, request)
    datos = await _leer_json(request)
    if not isinstance(datos, dict) or not isinstance(datos.get("caso"), dict):
        raise HTTPException(400, "Se espera {\"caso\": {...}, \"proyecto\": {...}}.")
    proyecto = datos.get("proyecto") if isinstance(datos.get("proyecto"), dict) else {}

    def hacer():
        with _un_informe_a_la_vez:
            return servicio.informe_pdf(datos["caso"], proyecto, buscar_medidas=medidas)

    contenido, avisos = await run_in_threadpool(hacer)
    return Response(contenido, media_type="application/pdf", headers={
        "Content-Disposition": 'attachment; filename="Memoria de calculo.pdf"',
        "X-Avisos": str(len(avisos)),
    })


@app.get("/api/ejemplos")
def ejemplos():
    return servicio.ejemplos()


@app.get("/api/ejemplos/{nombre}")
def ejemplo(nombre: str):
    try:
        return servicio.ejemplo(nombre)
    except KeyError:
        raise HTTPException(404, "No existe ese ejemplo.") from None


@app.get("/api/validacion")
def validacion():
    return servicio.validacion()


# Las páginas (index.html, calculadora.html, ...) van al final para no tapar /api.
app.mount("/", StaticFiles(directory=CARPETA_ESTATICA, html=True), name="estatico")
