"""
Paso 35: densidad de descargas a tierra N_G a partir de latitud/longitud,
usando la climatología LIS/OTD de la NASA (archivos/lis_vhrfc_1998_2013_v01.2.nc).

N_G = FRD (descargas/km²/año) del punto de grilla más cercano x 0,227 -- el
mismo factor que ya usaba el programa viejo (calculo_ddt_plot/ventana_calculo_ddt.py).

A diferencia del programa viejo, aquí lat=0 y lon=0 son coordenadas válidas
(ecuador / meridiano de Greenwich): el bug viejo usaba `if float(lat):`, que
en Python es Falso cuando lat=0, así que esas coordenadas nunca se calculaban.
"""
from pathlib import Path

from netCDF4 import Dataset

FACTOR_LIS_A_NG = 0.227

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