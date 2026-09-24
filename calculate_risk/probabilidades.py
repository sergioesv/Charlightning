"""Probabilidades de daño (P) para cada componente del riesgo."""


def calcular_P_B(E):
    """Probabilidad de daño físico por impacto directo a la estructura.

    E: eficiencia del sistema de protección contra rayos (0 = sin SPCR).
    Tabla B.2: sin SPCR = 1; nivel IV = 0,2; III = 0,1; II = 0,05; I = 0,02.
    Con E = 1 − P_B, esos mismos valores corresponden a E = 0; 0,8; 0,9; 0,95; 0,98.
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
    Tablas B.3 (P_DPS) y B.7 (P_EB): NPR III-IV = 0,05; NPR II = 0,02; NPR I = 0,01.
    Corregido: la franja NPR III-IV daba 0,03 en vez de 0,05.
    """
    if P_B > 0.3:
        valor_segun_nivel = 1
    elif P_B > 0.06:
        valor_segun_nivel = 0.05
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


def calcular_P_MS(K_MS):
    """Probabilidad de falla de equipos por impactos cerca de la estructura.

    P_MS = (K_S1·K_S2·K_S3·K_S4)², con un máximo de 1 (Anexo B, ecuación B.4).
    Corregido: antes se buscaba K_MS en una tabla de escalones sin
    referencia clara a la norma; ahora se usa la fórmula directa.
    """
    return min(1.0, K_MS ** 2)