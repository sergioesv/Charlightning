from pytest import approx

from calculate_risk.probabilidades import calcular_P_B, calcular_P_SPD_y_P_EB


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