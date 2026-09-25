"""
Paso 35: N_G desde latitud/longitud (climatología NASA LIS/OTD).

Requiere netCDF4 y archivos/lis_vhrfc_1998_2013_v01.2.nc (ya en el repo).
"""
from pytest import approx

from calculate_risk.norma.densidad import n_g_desde_lat_lon


def test_medellin_coincide_con_el_valor_que_ya_usaba_el_programa_viejo():
    # Comentario original en ventana_calculo_ddt.py: 10,32396 flashes/km^2/year
    # para (6.251, -75.563); N_G = 10,32396 x 0,227 = 2,3435...
    n_g = n_g_desde_lat_lon(lat=6.251, lon=-75.563)
    assert n_g == approx(2.3435, rel=1e-3)


def test_lat_lon_cero_es_una_coordenada_valida():
    # Bug del programa viejo: `if float(lat):` es Falso cuando lat=0, asi que
    # el ecuador/meridiano de Greenwich nunca se calculaba. Aqui si debe dar
    # un N_G real (no cero, no una excepcion).
    n_g = n_g_desde_lat_lon(lat=0.0, lon=0.0)
    assert n_g == approx(0.4654, rel=1e-3)
    assert n_g > 0