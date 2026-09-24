"""Áreas colectoras y número de eventos peligrosos por año."""
import math


def calcular_A_d(L, W, H, H_p):
    """Área colectora para impactos directos a la estructura, en m².

    L, W, H: largo, ancho y alto de la estructura (m).
    H_p: altura de la parte más alta que sobresale (m).
    Ecuación (6), pág. 35 de la norma usada en la versión original.
    """
    if H >= H_p:
        return L * W + 6 * H * (L + W) + 9 * math.pi * H ** 2
    return 9 * math.pi * H_p ** 2


def calcular_N_D(N_g, A_d, C_d):
    """Número de impactos directos a la estructura por año.

    N_g: densidad de descargas a tierra (rayos/km²/año).
    A_d: área colectora (m²). C_d: factor de ubicación.
    Ecuación (5), pág. 34. El 1e-6 pasa de m² a km².
    """
    return N_g * A_d * C_d * 1e-6


def calcular_A_m(L, W, D_m):
    """Área colectora para impactos cerca de la estructura, en m².

    L, W: largo y ancho de la estructura (m).
    La distancia hasta la que un rayo a tierra induce sobretensiones
    peligrosas es fija: 500 m (Anexo A.7, IEC 62305-2:2010 / NTC 4552-2:2023).
    Corregido: antes se usaba una distancia D_m = 250 m variable, que
    no corresponde a esta edición de la norma.
    """
    D = 500
    return 2 * D * (L + W) + math.pi * D ** 2


def calcular_N_M(N_g, A_m):
    """Número de impactos cerca de la estructura por año.

    Ecuación (A.6), Anexo A. Ya NO se resta A_d·C_d: en esta edición de
    la norma, N_M no descuenta los impactos directos a la estructura.
    Corregido: antes se restaba A_d·C_d (fórmula de otra edición de la norma).
    """
    return N_g * A_m * 1e-6