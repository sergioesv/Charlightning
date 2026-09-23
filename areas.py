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