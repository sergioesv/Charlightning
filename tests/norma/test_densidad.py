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


# ---------------------------------------------------------------------------
# Paso 58a: la ficha del dato (N_G con su procedencia)
# ---------------------------------------------------------------------------
import pytest

from calculate_risk.norma import densidad


def test_la_ficha_de_popayan_trae_los_valores_verificados_en_el_archivo():
    f = densidad.ficha_desde_lat_lon(2.44, -76.61)
    assert (f.celda_lat, f.celda_lon) == approx((2.45, -76.65), abs=1e-6)
    assert f.distancia_km == approx(4.6, abs=0.1)
    assert f.destellos_totales == approx(11.64, abs=0.01)
    assert f.N_G == approx(2.64, abs=0.01)
    assert f.horas_observadas == approx(158.0, abs=0.1)
    assert f.relacion_ic_cg == approx(3.4, abs=0.05)


def test_la_ficha_lee_los_metadatos_del_archivo_y_no_del_codigo():
    f = densidad.ficha_desde_lat_lon(2.44, -76.61)
    assert "VHRFC" in f.producto
    assert "Tropical Rainfall" in f.plataforma
    assert "NASA" in f.institucion
    assert f.version == "1.0"


def test_la_ficha_da_el_mismo_n_g_que_la_funcion_de_siempre():
    assert densidad.ficha_desde_lat_lon(6.251, -75.563).N_G == approx(
        n_g_desde_lat_lon(6.251, -75.563))


def test_la_fraccion_nube_tierra_se_puede_cambiar():
    base = densidad.ficha_desde_lat_lon(2.44, -76.61)
    otra = densidad.ficha_desde_lat_lon(2.44, -76.61, fraccion_nube_tierra=0.3)
    assert otra.N_G == approx(base.destellos_totales * 0.3)
    assert otra.fraccion_nube_tierra == 0.3


@pytest.mark.parametrize("fraccion", [0.0, -0.1, 1.5])
def test_una_fraccion_imposible_se_rechaza(fraccion):
    with pytest.raises(ValueError):
        densidad.ficha_desde_lat_lon(2.44, -76.61, fraccion_nube_tierra=fraccion)


@pytest.mark.parametrize("lat", [45.0, -60.0, 38.5])
def test_fuera_de_la_cobertura_lo_dice_y_no_inventa_un_numero(lat):
    with pytest.raises(densidad.FueraDeCobertura):
        densidad.ficha_desde_lat_lon(lat, 10.0)


def test_una_celda_en_cero_lo_avisa_en_vez_de_callar():
    f = densidad.ficha_desde_lat_lon(0.0, -30.0)     # Atlántico ecuatorial
    assert f.celda_en_cero is True
    assert f.N_G == 0.0


def test_una_celda_con_rayos_no_es_celda_en_cero():
    assert densidad.ficha_desde_lat_lon(2.44, -76.61).celda_en_cero is False


def test_la_longitud_se_normaliza():
    a = densidad.ficha_desde_lat_lon(2.44, -76.61)
    b = densidad.ficha_desde_lat_lon(2.44, 283.39)
    assert a.N_G == approx(b.N_G)