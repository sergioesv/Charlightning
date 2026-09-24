"""
Tablas y valores normativos de NTC 4552-2:2023.

Este módulo contiene únicamente datos normativos.
No realiza cálculos ni depende de la interfaz gráfica.
"""


# ============================================================
# RIESGO TOLERABLE - TABLA A.1
# ============================================================

RT = {
    "L1": 1e-5,
    "L2": 1e-3,
    "L3": 1e-4,
    "L4": 1e-3,
}


# ============================================================
# ANEXO A - DENSIDAD DE DESCARGAS A TIERRA
# ============================================================

def area_equivalente_estructura(L: float, W: float, H: float) -> float:
    """
    Área equivalente de captación de una estructura.

    Parámetros
    ----------
    L : float
        Longitud de la estructura [m].
    W : float
        Ancho de la estructura [m].
    H : float
        Altura de la estructura [m].

    Retorna
    -------
    float
        Área equivalente AD [m²].

    Corresponde a la ecuación A.2 de NTC 4552-2:2023.
    """
    import math

    return L * W + 6 * H * (L + W) + 9 * math.pi * H**2


def area_equivalente_minima() -> float:
    """
    Área mínima equivalente de captación.

    Corresponde a ADmin = π · (3H)² cuando se considera
    la condición de protrusión del objeto.

    Esta función se deja separada porque la aplicación de
    max(ADmin, A'D) depende de la geometría del caso.
    """
    raise NotImplementedError(
        "La altura H es necesaria para calcular ADmin."
    )


def area_equivalente_protrusion(H: float) -> float:
    """
    Área equivalente asociada a una estructura con protrusión.

    A'D = π · (3H)²

    Parámetros
    ----------
    H : float
        Altura de la estructura [m].

    Retorna
    -------
    float
        Área equivalente A'D [m²].
    """
    import math

    return math.pi * (3 * H) ** 2