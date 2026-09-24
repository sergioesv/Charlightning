"""Validación contra el caso de referencia de la norma (Anexo E.2, "casa rural").

A diferencia de los demás archivos de prueba, que verifican que el código no
cambie sin querer, estas pruebas comparan contra los valores que trae la
propia norma IEC 62305-2:2010 / NTC 4552-2:2023 para su ejemplo resuelto:
una casa rural de 15 x 20 x 6 m, con una línea de potencia subterránea y
una línea de telecomunicación aérea, N_g = 4 rayos/km²/año.
"""
from pytest import approx

from calculate_risk.areas import calcular_A_d, calcular_N_D, calcular_A_m, calcular_N_M
from calculate_risk.lineas import (
    calcular_A_l_aerea,
    calcular_A_i_aerea,
    calcular_A_l_subterranea,
    calcular_A_i_subterranea,
    calcular_N_L,
    calcular_N_I,
)

N_G = 4.0
L, W, H = 15.0, 20.0, 6.0
L_L = 1000.0  # longitud de línea desconocida -> 1000 m por defecto


def test_estructura_casa_rural():
    A_D = calcular_A_d(L=L, W=W, H=H, H_p=H)
    assert A_D == approx(2.578e3, rel=0.001)
    assert calcular_N_D(N_g=N_G, A_d=A_D, C_d=1.0) == approx(1.03e-2, rel=0.01)


def test_cerca_de_la_estructura_casa_rural():
    A_M = calcular_A_m(L=L, W=W)
    assert A_M == approx(8.204e5, rel=0.001)
    assert calcular_N_M(N_g=N_G, A_m=A_M) == approx(3.282, rel=0.001)


def test_linea_potencia_subterranea_casa_rural():
    # Subterránea (C_I=0,5), rural (C_E=1), baja tensión (C_T=1)
    A_L = calcular_A_l_subterranea(L_c=L_L)
    A_I = calcular_A_i_subterranea(L_c=L_L)
    assert calcular_N_L(N_g=N_G, A_l=A_L, C_I=0.5, C_E=1.0, C_T=1.0) == approx(8.00e-2, rel=0.01)
    assert calcular_N_I(N_g=N_G, A_i=A_I, C_I=0.5, C_E=1.0, C_T=1.0) == approx(8.00, rel=0.01)


def test_linea_telecom_aerea_casa_rural():
    # Aérea (C_I=1), rural (C_E=1)
    A_L = calcular_A_l_aerea(L_c=L_L)
    A_I = calcular_A_i_aerea(L_c=L_L)
    assert calcular_N_L(N_g=N_G, A_l=A_L, C_I=1.0, C_E=1.0, C_T=1.0) == approx(1.60e-1, rel=0.01)
    assert calcular_N_I(N_g=N_G, A_i=A_I, C_I=1.0, C_E=1.0, C_T=1.0) == approx(16.0, rel=0.01)