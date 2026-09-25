"""
Validacion de areas y frecuencias contra el caso resuelto de la norma
(Anexo E.2, "casa rural"): 15 x 20 x 6 m, una linea de potencia subterranea
y una de telecomunicacion aerea, N_G = 4 rayos/km2/ano.

A diferencia de las demas pruebas, que fijan que el codigo no cambie sin
querer, estas comparan contra los valores que imprime la propia norma
(Tabla E.7). Vienen de tests/test_validacion_norma.py, que se escribio para
el motor viejo; en el Paso 37e se portaron a calculate_risk/norma/ al retirarlo.
"""
from pytest import approx

from calculate_risk.norma import areas, frecuencias

N_G = 4.0
L, W, H = 15.0, 20.0, 6.0
L_L = 1000.0  # longitud de linea desconocida -> 1000 m por defecto


def test_estructura_casa_rural():
    A_D = areas.area_estructura_completa(L, W, H, H_p=H)
    assert A_D == approx(2.578e3, rel=0.001)
    assert frecuencias.n_d(N_G, A_D, cd=1.0) == approx(1.03e-2, rel=0.01)


def test_cerca_de_la_estructura_casa_rural():
    A_M = areas.area_descargas_cercanas(L, W)
    assert A_M == approx(8.204e5, rel=0.001)
    assert frecuencias.n_m(N_G, L, W) == approx(3.282, rel=0.001)


def test_linea_potencia_subterranea_casa_rural():
    # Subterranea (C_I=0,5), rural (C_E=1), baja tension (C_T=1)
    assert areas.area_linea_descargas_directas(L_L) == approx(4.0e4)
    assert areas.area_linea_descargas_cercanas(L_L) == approx(4.0e6)
    assert frecuencias.n_l(N_G, L_L, ci=0.5, ce=1.0, ct=1.0) == approx(8.00e-2, rel=0.01)
    assert frecuencias.n_i(N_G, L_L, ci=0.5, ce=1.0, ct=1.0) == approx(8.00, rel=0.01)


def test_linea_telecom_aerea_casa_rural():
    # Aerea (C_I=1), rural (C_E=1)
    assert frecuencias.n_l(N_G, L_L, ci=1.0, ce=1.0, ct=1.0) == approx(1.60e-1, rel=0.01)
    assert frecuencias.n_i(N_G, L_L, ci=1.0, ce=1.0, ct=1.0) == approx(16.0, rel=0.01)