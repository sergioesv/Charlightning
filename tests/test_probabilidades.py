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
    # SP = 2: los dos bajan según el nivel del SPCR
    assert calcular_P_SPD_y_P_EB(P_B=0.1, SP=2) == (0.03, 0.03)
    assert calcular_P_SPD_y_P_EB(P_B=0.05, SP=2) == (0.02, 0.02)
    assert calcular_P_SPD_y_P_EB(P_B=0.02, SP=2) == (0.01, 0.01)


def test_K_MS():
    # 0,2 · 1 · 0,1 · 1 = 0,02
    assert calcular_K_MS(K_S1=0.2, K_S2=1, K_S3=0.1, K_S4=1) == approx(0.02)


def test_P_MS_valores_de_la_tabla():
    assert calcular_P_MS(0.01) == 0.0001    # menor que el primer límite
    assert calcular_P_MS(0.013) == 0.0001   # justo en el límite
    assert calcular_P_MS(0.02) == 0.01      # entre 0,016 y 0,021
    assert calcular_P_MS(0.1) == 0.9        # entre 0,07 y 0,15


def test_P_MS_fuera_de_la_tabla():
    # Sin apantallamiento (K_MS = 1) la probabilidad es 1
    assert calcular_P_MS(1) == 1