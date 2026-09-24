from pytest import approx

from calculate_risk.probabilidades import (
    calcular_P_B,
    calcular_P_SPD_y_P_EB,
    calcular_K_MS,
    calcular_P_MS,
)


def test_P_B():
    # Con un SPCR de eficiencia 0,9 queda un 10 % de probabilidad de daño
    assert calcular_P_B(E=0.9) == approx(0.1)


def test_P_B_sin_proteccion():
    assert calcular_P_B(E=0) == 1


def test_sin_medidas_contra_sobretensiones():
    # SP = 0: P_SPD = 1 y P_EB = 1
    assert calcular_P_SPD_y_P_EB(P_B=1, SP=0) == (1, 1)


def test_dps_solo_en_entrada_de_servicios():
    # SP = 1: P_EB baja según el nivel, pero P_SPD sigue en 1
    assert calcular_P_SPD_y_P_EB(P_B=0.05, SP=1) == (1, 0.02)


def test_dps_coordinados_segun_nivel_del_spcr():
    # SP = 2: los dos bajan según el nivel del SPCR (Tablas B.3 y B.7)
    assert calcular_P_SPD_y_P_EB(P_B=0.2, SP=2) == (0.05, 0.05)   # NPR IV
    assert calcular_P_SPD_y_P_EB(P_B=0.1, SP=2) == (0.05, 0.05)   # NPR III
    assert calcular_P_SPD_y_P_EB(P_B=0.05, SP=2) == (0.02, 0.02)  # NPR II
    assert calcular_P_SPD_y_P_EB(P_B=0.02, SP=2) == (0.01, 0.01)  # NPR I


def test_K_MS():
    # 0,2 · 1 · 0,1 · 1 = 0,02
    assert calcular_K_MS(K_S1=0.2, K_S2=1, K_S3=0.1, K_S4=1) == approx(0.02)


def test_P_MS_es_el_cuadrado_de_K_MS():
    # Ecuación B.4: P_MS = (K_S1*K_S2*K_S3*K_S4)^2 = K_MS^2
    assert calcular_P_MS(0.1) == approx(0.01)
    assert calcular_P_MS(0.5) == approx(0.25)


def test_P_MS_nunca_pasa_de_1():
    # Sin apantallamiento (K_MS = 1) o mayor, la probabilidad queda en 1
    assert calcular_P_MS(1) == 1
    assert calcular_P_MS(2) == 1