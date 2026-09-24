from pytest import approx

from calculate_risk.lineas import (
    calcular_A_l_aerea,
    calcular_A_i_aerea,
    calcular_N_L,
    calcular_N_I,
    calcular_A_l_subterranea,
    calcular_A_i_subterranea,
    calcular_delta_N,
)


def test_A_l_aerea():
    # A_L = 40 · L_c: 40 · 1000 = 40 000 m²
    assert calcular_A_l_aerea(L_c=1000) == approx(40_000)


def test_A_i_aerea():
    # A_I = 4000 · L_c: 4000 · 1000 = 4 000 000 m²
    assert calcular_A_i_aerea(L_c=1000) == approx(4_000_000)


def test_A_l_subterranea_igual_a_la_aerea():
    # En esta edición de la norma, A_L no depende de si la línea es
    # aérea o subterránea (la diferencia está en C_I, no en el área).
    assert calcular_A_l_subterranea(L_c=1000) == calcular_A_l_aerea(L_c=1000)


def test_A_i_subterranea_igual_a_la_aerea():
    assert calcular_A_i_subterranea(L_c=1000) == calcular_A_i_aerea(L_c=1000)


def test_N_L_aerea():
    # C_I = 1 (aérea), C_E = 0,5, C_T = 1: 10 · 40000 · 1 · 0,5 · 1 · 10⁻⁶ = 0,2
    assert calcular_N_L(N_g=10, A_l=40_000, C_I=1.0, C_E=0.5, C_T=1.0) == approx(0.2)


def test_N_L_subterranea_es_la_mitad_de_la_aerea():
    # C_I = 0,5 (subterránea): mismos demás factores -> la mitad
    aerea = calcular_N_L(N_g=10, A_l=40_000, C_I=1.0, C_E=0.5, C_T=1.0)
    subterranea = calcular_N_L(N_g=10, A_l=40_000, C_I=0.5, C_E=0.5, C_T=1.0)
    assert subterranea == approx(aerea / 2)


def test_N_I_con_transformador():
    # C_I = 1, C_E = 0,5, C_T = 0,2 (con transformador): 10·4e6·1·0,5·0,2·10⁻⁶ = 4,0
    assert calcular_N_I(N_g=10, A_i=4_000_000, C_I=1.0, C_E=0.5, C_T=0.2) == approx(4.0)


def test_delta_N():
    assert calcular_delta_N(N_I=1.0, N_L=0.2) == approx(0.8)


def test_delta_N_nunca_es_negativo():
    assert calcular_delta_N(N_I=0.1, N_L=0.2) == 0