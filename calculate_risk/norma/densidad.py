"""
Paso 35: densidad de descargas a tierra N_G a partir de latitud/longitud,
usando la climatología LIS/OTD de la NASA (archivos/lis_vhrfc_1998_2013_v01.2.nc).

N_G = FRD (descargas/km²/año) del punto de grilla más cercano x 0,25: cerca de la
cuarta parte de los destellos son nube-tierra (Rakov, V. A., 2016, Fundamentals of
Lightning, Cambridge University Press). Antes se usaba 0,227; 0,25 es más conservador.

A diferencia del programa viejo, aquí lat=0 y lon=0 son coordenadas válidas
(ecuador / meridiano de Greenwich): el bug viejo usaba `if float(lat):`, que
en Python es Falso cuando lat=0, así que esas coordenadas nunca se calculaban.
"""
import math
from dataclasses import dataclass
from pathlib import Path

from netCDF4 import Dataset
from calculate_risk.norma.modelo import Emplazamiento

FACTOR_LIS_A_NG = 0.25

RUTA_POR_DEFECTO = str(
    Path(__file__).resolve().parent.parent.parent / "archivos" / "lis_vhrfc_1998_2013_v01.2.nc"
)


def n_g_desde_lat_lon(lat: float, lon: float, ruta_nc: str = RUTA_POR_DEFECTO) -> float:
    """N_G [descargas/km²/año] en el punto de la grilla NASA más cercano a (lat, lon)."""
    with Dataset(ruta_nc, "r") as data:
        lat_grid = data.variables["Latitude"][:]
        lon_grid = data.variables["Longitude"][:]
        frd = data.variables["VHRFC_LIS_FRD"][:]

        i_lat = ((lat_grid - lat) ** 2).argmin()
        i_lon = ((lon_grid - lon) ** 2).argmin()

        return float(frd[i_lat, i_lon]) * FACTOR_LIS_A_NG


# ---------------------------------------------------------------------------
# Paso 58a: la ficha del dato. N_G nunca viaja solo: viaja con su procedencia.
# ---------------------------------------------------------------------------

LIMITE_DE_LATITUD = 38.0     # el sensor cubre de -37,95 a +37,95 (celdas de 0,1 grados)
RADIO_TERRESTRE_KM = 6371.0


class FueraDeCobertura(ValueError):
    """El punto queda fuera de la zona que observa el sensor LIS (+-38 grados)."""


@dataclass(frozen=True)
class FichaNG:
    """N_G y todo lo que hace falta para poder defenderlo."""
    lat: float                # sitio pedido
    lon: float
    celda_lat: float          # centro de la celda de la grilla que se usó
    celda_lon: float
    distancia_km: float       # del sitio al centro de la celda
    destellos_totales: float  # FRD de la NASA [destellos/km2/año]
    fraccion_nube_tierra: float
    N_G: float                # destellos_totales x fraccion_nube_tierra
    horas_observadas: float   # viewtime: cuánto miró el sensor esa celda
    celda_en_cero: bool
    producto: str
    plataforma: str
    institucion: str
    version: str
    procesamiento: str

    @property
    def relacion_ic_cg(self) -> float:
        """Z = destellos intranube por cada destello a tierra, con f = 1/(1+Z)."""
        return 1.0 / self.fraccion_nube_tierra - 1.0


def _distancia_km(lat1, lon1, lat2, lon2) -> float:
    """Círculo máximo (haversine)."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((f2 - f1) / 2) ** 2
         + math.cos(f1) * math.cos(f2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * RADIO_TERRESTRE_KM * math.asin(math.sqrt(a))


def ficha_desde_lat_lon(lat: float, lon: float, fraccion_nube_tierra: float = FACTOR_LIS_A_NG,
                        ruta_nc: str = RUTA_POR_DEFECTO) -> FichaNG:
    """Busca la celda más cercana y devuelve N_G con su procedencia.

    Lanza FueraDeCobertura si |lat| > 38 y ValueError si la fracción no está en (0, 1].
    Una celda en cero NO lanza nada: la ficha lo dice (`celda_en_cero`) y quien la use
    decide si avisa; un riesgo cero en silencio es el error del programa viejo.
    """
    if not (0.0 < fraccion_nube_tierra <= 1.0):
        raise ValueError("La fracción nube-tierra tiene que estar entre 0 (sin incluir) y 1.")
    if not (-90.0 <= lat <= 90.0 and -360.0 <= lon <= 360.0):
        raise ValueError("Latitud o longitud fuera de rango.")
    if abs(lat) > LIMITE_DE_LATITUD:
        raise FueraDeCobertura(
            f"La latitud {lat:g} queda fuera de la cobertura del sensor LIS "
            f"(±{LIMITE_DE_LATITUD:g}°). Hay que declarar N_G con su fuente.")
    lon = (lon + 180.0) % 360.0 - 180.0

    with Dataset(ruta_nc, "r") as data:
        lat_grid = data.variables["Latitude"][:]
        lon_grid = data.variables["Longitude"][:]
        i_lat = int(((lat_grid - lat) ** 2).argmin())
        i_lon = int(((lon_grid - lon) ** 2).argmin())
        frd = float(data.variables["VHRFC_LIS_FRD"][i_lat, i_lon])
        segundos = float(data.variables["VHRFC_LIS_VT"][i_lat, i_lon])
        c_lat, c_lon = float(lat_grid[i_lat]), float(lon_grid[i_lon])
        atributos = {k: str(data.getncattr(k)) for k in data.ncattrs()}

    return FichaNG(
        lat=lat, lon=lon, celda_lat=c_lat, celda_lon=c_lon,
        distancia_km=_distancia_km(lat, lon, c_lat, c_lon),
        destellos_totales=frd, fraccion_nube_tierra=fraccion_nube_tierra,
        N_G=frd * fraccion_nube_tierra, horas_observadas=segundos / 3600.0,
        celda_en_cero=frd == 0.0,
        producto=atributos.get("Title", ""), plataforma=atributos.get("Source", ""),
        institucion=atributos.get("Institutions", ""), version=atributos.get("Version", ""),
        procesamiento=atributos.get("history", ""),
    )

# ---------------------------------------------------------------------------
# Paso 58b: el emplazamiento de un caso (coordenadas o declarado)
# ---------------------------------------------------------------------------

MODOS = ("coordenadas", "declarado")


class EmplazamientoInvalido(ValueError):
    """Al emplazamiento le falta algo: coordenadas, o la fuente de un N_G declarado."""


def ficha_de(emplazamiento: Emplazamiento, ruta_nc: str = RUTA_POR_DEFECTO) -> FichaNG:
    """La ficha del dato para un emplazamiento por coordenadas."""
    if emplazamiento.modo != "coordenadas":
        raise EmplazamientoInvalido("Solo un emplazamiento por coordenadas tiene ficha del dato.")
    if emplazamiento.lat is None or emplazamiento.lon is None:
        raise EmplazamientoInvalido("Faltan la latitud y la longitud.")
    return ficha_desde_lat_lon(emplazamiento.lat, emplazamiento.lon,
                               emplazamiento.fraccion_nube_tierra, ruta_nc)


def validar(emplazamiento: Emplazamiento):
    """Lanza EmplazamientoInvalido si el emplazamiento no se sostiene."""
    if emplazamiento.modo not in MODOS:
        raise EmplazamientoInvalido(f"Modo desconocido: {emplazamiento.modo!r}.")
    if emplazamiento.modo == "declarado" and not emplazamiento.fuente.strip():
        raise EmplazamientoInvalido(
            "Un N_G declarado necesita su fuente (red de detección, mapa oficial, norma...).")
    if emplazamiento.modo == "coordenadas" and (
            emplazamiento.lat is None or emplazamiento.lon is None):
        raise EmplazamientoInvalido("Faltan la latitud y la longitud.")


def concuerda(emplazamiento: Emplazamiento, N_G: float, ruta_nc: str = RUTA_POR_DEFECTO) -> bool:
    """¿El N_G guardado es el que dan hoy las coordenadas? Un declarado siempre concuerda.

    Sirve para no calcular con un N_G que ya no corresponde a lo que el informe
    va a decir de dónde salió (coordenadas editadas a mano en el archivo, por ejemplo).
    """
    if emplazamiento.modo != "coordenadas":
        return True
    return abs(ficha_de(emplazamiento, ruta_nc).N_G - N_G) <= 1e-6 * max(1.0, abs(N_G))