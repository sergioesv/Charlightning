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
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response

from web import servicio
from web.contacto import Buzon, MensajeInvalido
from web.contador import Contador, ruta_por_omision
from web.estaticos import EstaticosVersionados
from web.limite import Limite
from web.verificaciones import ID_VALIDO, desde_entorno

MAX_BYTES = 200_000                  # un caso real pesa unos pocos kB
CARPETA_ESTATICA = Path(__file__).resolve().parent / "estatico"
VERSION = "0.1.0"
COMMIT = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")[:7]

app = FastAPI(title="Charlightning", version=VERSION, docs_url="/api/docs",
              redoc_url=None, openapi_url="/api/openapi.json")
app.add_middleware(GZipMiddleware, minimum_size=800)

# Cuánto puede guardar el navegador cada cosa. Los CSS y JS se piden siempre con su
# versión (?v=...), que cambia con cada despliegue: esos se guardan un año sin volver a
# preguntar. Las páginas se piden siempre de nuevo, y así traen la versión al día.
CACHE_VERSIONADO = "public, max-age=31536000, immutable"
CACHE_PAGINAS = "no-cache"


@app.middleware("http")
async def _cache(request: Request, siguiente):
    respuesta = await siguiente(request)
    ruta = request.url.path
    if "cache-control" in respuesta.headers:
        return respuesta
    if ruta.endswith((".css", ".js", ".png", ".ico", ".svg")):
        versionado = "v" in request.query_params
        respuesta.headers["Cache-Control"] = CACHE_VERSIONADO if versionado else CACHE_PAGINAS
    elif ruta in ("/api/esquema", "/api/validacion") or ruta.startswith("/api/ejemplos"):
        respuesta.headers["Cache-Control"] = "public, max-age=3600"
    elif ruta.startswith("/api/"):
        respuesta.headers["Cache-Control"] = "no-store"
    else:
        respuesta.headers["Cache-Control"] = CACHE_PAGINAS
    return respuesta
    if ruta.endswith((".css", ".js", ".png", ".ico", ".svg")):
        respuesta.headers["Cache-Control"] = CACHE_ESTATICOS
    elif ruta in ("/api/esquema", "/api/validacion") or ruta.startswith("/api/ejemplos"):
        respuesta.headers["Cache-Control"] = "public, max-age=3600"
    elif ruta.startswith("/api/"):
        respuesta.headers["Cache-Control"] = "no-store"
    else:
        respuesta.headers["Cache-Control"] = CACHE_PAGINAS
    return respuesta

contador = Contador(ruta_por_omision())
buzon = Buzon.desde_entorno(ruta_por_omision().parent)
verificaciones = desde_entorno(ruta_por_omision().parent)

# Al arrancar se anota cuánto hay guardado: sirve para saber que el volumen sigue ahí.
_mensajes = ruta_por_omision().parent / "mensajes.jsonl"
print(f"Charlightning: {contador.leer()} visitas guardadas en {contador.ruta}; "
      f"{sum(1 for _ in _mensajes.open(encoding='utf-8')) if _mensajes.exists() else 0} mensajes de contacto",
      flush=True)
_ESQUEMA = servicio.esquema()      # no cambia mientras el servicio está arriba

limite_calculo = Limite(maximo=int(os.environ.get("LIMITE_CALCULOS", 120)), segundos=60)
limite_informe = Limite(maximo=int(os.environ.get("LIMITE_INFORMES", 5)), segundos=60)
limite_contacto = Limite(maximo=3, segundos=600)

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
            return servicio.informe_pdf(datos["caso"], proyecto, buscar_medidas=medidas,
                                        verificaciones=verificaciones)

    contenido, avisos, registro = await run_in_threadpool(hacer)
    cabeceras = {"Content-Disposition": 'attachment; filename="Memoria de calculo.pdf"',
                 "X-Avisos": str(len(avisos))}
    if registro is not None:
        cabeceras["X-Registro"] = registro.id
    return Response(contenido, media_type="application/pdf", headers=cabeceras)


@app.get("/api/verificar/{id_}")
async def verificar(id_: str, request: Request):
    """Lo que quedó registrado de una memoria: el QR del PDF lleva aquí."""
    _revisar_limite(limite_calculo, request)
    id_ = id_.strip().upper()
    if not ID_VALIDO.match(id_):
        raise HTTPException(400, "Un código de memoria se ve así: CHL-2026-7F3A9C.")
    try:
        registro = await run_in_threadpool(verificaciones.buscar, id_)
    except Exception as error:
        raise HTTPException(503, "No se pudo consultar el registro; intente en un momento.") from error
    if registro is None:
        raise HTTPException(404, "No hay ninguna memoria registrada con ese código.")
    return {"id": registro.id, "created_at": registro.created_at,
            "coordinates": registro.coordinates, "risk_r1": registro.risk_r1,
            "verdict": registro.verdict, "data_hash": registro.data_hash,
            "huella": registro.impreso().huella, "engine_version": registro.engine_version}


@app.get("/api/esquema")
def esquema():
    """Las listas de las tablas de la norma, para los formularios."""
    return _ESQUEMA


@app.post("/api/abrir")
async def abrir(request: Request):
    """Un caso guardado (cualquiera de los dos formatos) -> listo para los formularios."""
    _revisar_limite(limite_calculo, request)
    datos = await _leer_json(request)
    return await run_in_threadpool(servicio.abrir, datos)


@app.post("/api/desglose")
async def desglose(request: Request, tipo: int = Query(..., ge=1, le=4)):
    """«¿De dónde viene el riesgo?» para un riesgo del caso."""
    _revisar_limite(limite_calculo, request)
    datos = await _leer_json(request)
    return await run_in_threadpool(servicio.desglose, datos, tipo)


@app.get("/api/visitas")
def visitas():
    """El número que muestra el contador de la página."""
    return {"visitas": contador.leer()}


@app.post("/api/visitas")
def visita_nueva(request: Request):
    """Una visita más (la página la manda una vez por sesión del navegador)."""
    _revisar_limite(limite_calculo, request)
    return {"visitas": contador.sumar()}


@app.post("/api/contacto")
async def contacto(request: Request):
    """El formulario de contacto. El correo de destino solo lo conoce el servidor."""
    datos = await _leer_json(request)
    # Campo trampa: una persona no lo ve; un robot lo llena. Se le contesta igual.
    if isinstance(datos, dict) and str(datos.get("sitio_web", "")).strip():
        return {"enviado": True}
    _revisar_limite(limite_contacto, request)
    try:
        enviado = await run_in_threadpool(buzon.recibir, datos)
    except MensajeInvalido as error:
        raise HTTPException(422, str(error)) from error
    return {"enviado": enviado}


@app.get("/api/ejemplos")
def ejemplos():
    return servicio.ejemplos()


@app.get("/api/ejemplos/{nombre}")
def ejemplo(nombre: str):
    try:
        return servicio.ejemplo(nombre)
    except KeyError:
        raise HTTPException(404, "No existe ese ejemplo.") from None


@app.get("/api/ejemplos/{nombre}/abierto")
def ejemplo_abierto(nombre: str):
    """El ejemplo ya listo para los formularios: un viaje en vez de dos."""
    try:
        return servicio.abrir(servicio.ejemplo(nombre))
    except KeyError:
        raise HTTPException(404, "No existe ese ejemplo.") from None


@app.get("/api/validacion")
def validacion():
    return servicio.validacion()


# Las páginas (index.html, calculadora.html, ...) van al final para no tapar /api.
estaticos = EstaticosVersionados(directory=CARPETA_ESTATICA, html=True)


@app.get("/verify")
@app.get("/verify/{id_}")
async def pagina_de_verificacion(request: Request, id_: str = ""):
    """La página a la que lleva el QR; el código se lee de la dirección en el navegador."""
    return await estaticos.get_response("verify.html", request.scope)


app.mount("/", estaticos, name="estatico")
