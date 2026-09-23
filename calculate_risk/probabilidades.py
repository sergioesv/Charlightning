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


def calcular_K_MS(K_S1, K_S2, K_S3, K_S4):
    """Factor de apantallamiento total para impactos cercanos.

    K_S1: apantallamiento de la estructura.
    K_S2: apantallamiento de las zonas internas.
    K_S3: tipo de cableado interno.
    K_S4: tensión soportada de los equipos.
    """
    return K_S1 * K_S2 * K_S3 * K_S4


# Tabla de P_MS: cada fila es (límite superior de K_MS, valor de P_MS).
# Se recorre de arriba a abajo y se toma la primera fila que cumpla.
TABLA_P_MS = [
    (0.013, 0.0001),
    (0.014, 0.001),
    (0.015, 0.003),
    (0.016, 0.005),
    (0.021, 0.01),
    (0.035, 0.1),
    (0.07, 0.5),
    (0.15, 0.9),
]


def calcular_P_MS(K_MS):
    """Probabilidad de falla de equipos por impactos cerca de la estructura.

    Busca K_MS en TABLA_P_MS. Si K_MS es mayor que todos los límites, vale 1.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    for limite, P_MS in TABLA_P_MS:
        if K_MS <= limite:
            return P_MS
    return 1.0