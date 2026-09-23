from pytest import approx

from calculate_risk.perdidas import calcular_L_A, calcular_L_B
from calculate_risk.riesgos import calcular_componente, calcular_X


def test_L_A():
    # 0,01 · 10⁻⁴ = 10⁻⁶
    assert calcular_L_A(r_a=0.01, L_t=1e-4) == approx(1e-6)


def test_L_B():
    # 1 · 5 · 0,01 · 0,05 = 0,0025
    assert calcular_L_B(r=1, h_z=5, r_f=0.01, L_f=0.05) == approx(0.0025)


def test_componente():
    # 0,0115 · 1 · 10⁻⁶ = 1,15 · 10⁻⁸
    assert calcular_componente(N=0.0115, P=1, L=1e-6) == approx(1.15e-8)


def test_X_suma_todas_las_lineas():
    # 1 · 0,1 · 0,5 + 2 · 0,2 · 1 = 0,05 + 0,4 = 0,45
    lineas = [
        (1, 0.1, 0.5),
        (2, 0.2, 1),
    ]
    assert calcular_X(lineas) == approx(0.45)


def test_X_sin_lineas_es_cero():
    # Si n = 0 para todas, no hay eventos por las líneas
    assert calcular_X([(0, 0.1, 1), (0, 0.2, 1)]) == 0