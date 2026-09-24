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
    # Distancia fija de 500 m (Anexo A.7): 2·500·30 + π·500² = 815398,16 m²
    assert calcular_A_m(L=20, W=10) == approx(815398.163, rel=1e-6)


def test_N_M():
    # 10 · 815398,16 · 10⁻⁶ = 8,154 impactos/año. Ya no se resta A_d·C_d.
    assert calcular_N_M(N_g=10, A_m=815398.163) == approx(8.153982, rel=1e-6)