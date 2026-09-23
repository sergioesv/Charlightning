from pytest import approx 

from calculate_risk.areas import calcular_A_d, calcular_N_D, calcular_A_m, calcular_N_M


def test_A_d_estructura_sin_protuberancia():
    # 20 x 10 m y 6 m de alto: 200 + 1080 + 1017,88 = 2297,88 m²
    assert calcular_A_d(L=20, W=10, H=6, H_p=6) == approx(2297.876, rel=1e-6)


def test_A_d_con_protuberancia_mas_alta():
    # Si la protuberancia (15 m) es más alta: 9·π·15² = 6361,73 m²
    assert calcular_A_d(L=20, W=10, H=6, H_p=15) == approx(6361.725, rel=1e-6)


def test_N_D():
    # 10 rayos/km²/año · 2297,88 m² · 0,5 · 10⁻⁶ = 0,01149 impactos/año
    assert calcular_N_D(N_g=10, A_d=2297.876, C_d=0.5) == approx(0.01148938, rel=1e-6)


def test_A_m():
    # 2·20·250 + 2·10·250 + π·250² = 10000 + 5000 + 196349,54 = 211349,54 m²
    assert calcular_A_m(L=20, W=10, D_m=250) == approx(211349.54, rel=1e-6)


def test_N_M():
    # 10 · (211349,54 − 2297,88·0,5) · 10⁻⁶ = 2,102 impactos/año
    assert calcular_N_M(N_g=10, A_m=211349.54, A_d=2297.876, C_d=0.5) == approx(2.102006, rel=1e-6)


def test_N_M_nunca_es_negativo():
    # Si el área directa es mayor que A_m, el resultado debe ser 0
    assert calcular_N_M(N_g=10, A_m=100, A_d=1000, C_d=1) == 0