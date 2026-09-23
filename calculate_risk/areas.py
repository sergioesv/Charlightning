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
    D_m: distancia (m) hasta la que un rayo a tierra induce
         sobretensiones peligrosas. La versión original usa 250 m.
    PENDIENTE: verificar con IEC 62305-2:2024. Una versión anterior
    de este código sumaba también el término L·W.
    """
    return 2 * L * D_m + 2 * W * D_m + math.pi * D_m ** 2


def calcular_N_M(N_g, A_m, A_d, C_d):
    """Número de impactos cerca de la estructura por año.

    Se resta A_d·C_d para no contar los impactos directos.
    Si el resultado fuera negativo, se toma 0.
    Ecuación (8), pág. 37.
    PENDIENTE: en IEC 62305-2:2024, N_SG reemplaza a N_g.
    """
    return max(0.0, N_g * (A_m - A_d * C_d) * 1e-6)