"""Probabilidades de daño (P) para cada componente del riesgo."""


def calcular_P_B(E):
    """Probabilidad de daño físico por impacto directo a la estructura.

    E: eficiencia del sistema de protección contra rayos (0 = sin SPCR).
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    return 1 - E


def calcular_P_SPD_y_P_EB(P_B, SP):
    """Probabilidades asociadas a la protección contra sobretensiones.

    P_B: probabilidad de daño físico (depende del nivel del SPCR).
    SP: medidas contra sobretensiones
        0 = ninguna, 1 = DPS solo en la entrada de servicios,
        2 = sistema de DPS coordinados (NTC 4552-4).
    El nivel de los DPS se toma igual al nivel del SPCR (según P_B).
    Devuelve dos valores: (P_SPD, P_EB).
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    if P_B > 0.3:
        valor_segun_nivel = 1
    elif P_B > 0.06:
        valor_segun_nivel = 0.03
    elif P_B > 0.03:
        valor_segun_nivel = 0.02
    else:
        valor_segun_nivel = 0.01

    P_EB = 1 if SP == 0 else valor_segun_nivel
    P_SPD = 1 if SP < 2 else valor_segun_nivel
    return P_SPD, P_EB