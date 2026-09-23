from pytest import approx

from calculate_risk.lineas import (
    calcular_A_l_aerea,
    calcular_A_i_aerea,
    calcular_N_L,
    calcular_N_I,
    calcular_A_l_subterranea,
    calcular_A_i_subterranea,
)


def test_A_l_aerea():
    # Longitud útil: 1000 − 3·6 − 3·0 = 982 m → 6 · 6 · 982 = 35352 m²
    assert calcular_A_l_aerea(L_c=1000, H=6, H_a=0, H_c=6) == approx(35352)


def test_A_l_aerea_linea_muy_corta_da_cero():
    # 10 − 3·6 = −8 m → no queda longitud útil
    assert calcular_A_l_aerea(L_c=10, H=6, H_a=0, H_c=6) == 0


def test_A_i_aerea():
    # 2 · 500 · 1000 = 1.000.000 m²
    assert calcular_A_i_aerea(L_c=1000, D_L=500) == approx(1_000_000)


def test_N_L():
    # 10 · 35352 · 1 · 0,5 · 10⁻⁶ = 0,17676 impactos/año
    assert calcular_N_L(N_g=10, A_l=35352, C_t=1, C_d=0.5) == approx(0.17676)


def test_N_I_con_transformador():
    # 10 · 1.000.000 · 0,2 · 0,5 · 10⁻⁶ = 1,0 impactos/año
    assert calcular_N_I(N_g=10, A_i=1_000_000, C_t=0.2, C_e=0.5) == approx(1.0)


def test_A_l_subterranea():
    # Longitud útil: 1000 − 3·(0 + 6) = 982 m → 982 · √500 = 21958,19 m²
    assert calcular_A_l_subterranea(L_c=1000, H=6, H_a=0, rho=500) == approx(21958.19, rel=1e-6)


def test_A_i_subterranea():
    # 25 · 1000 · √500 = 559016,99 m²
    assert calcular_A_i_subterranea(L_c=1000, rho=500) == approx(559016.99, rel=1e-6)


def test_raiz_cuadrada_no_se_redondea():
    # Error corregido: antes se usaba math.isqrt, que daba √500 = 22 en vez de 22,36
    assert calcular_A_i_subterranea(L_c=1, rho=500) != 25 * 22