"""
Áreas de recolección (Anexo A, NTC 4552-2:2023).
"""

import math
from calculate_risk.norma import tablas


def area_estructura_completa(L: float, W: float, H: float, H_p: float = 0.0) -> float:
    """A_D de una estructura, considerando un posible saliente en el techo:
    el mayor entre el área con la altura de la estructura (ec. A.2) y el
    área del saliente (ec. A.3)."""
    a_base = tablas.area_equivalente_estructura(L, W, H)
    if H_p <= 0:
        return a_base
    return max(a_base, tablas.area_equivalente_protrusion(H_p))



def area_descargas_cercanas(L: float, W: float) -> float:
    """A_M: área de recolección de descargas cerca de la estructura (ec. A.7)."""
    return 2 * 500 * (L + W) + math.pi * 500 ** 2


def area_linea_descargas_directas(L_L: float) -> float:
    """A_L: área de recolección de descargas directas en una línea (ec. A.9)."""
    return 40 * L_L


def area_linea_descargas_cercanas(L_L: float) -> float:
    """A_I: área de recolección de descargas cercanas a una línea (ec. A.11)."""
    return 4000 * L_L