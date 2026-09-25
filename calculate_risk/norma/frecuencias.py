"""
Número medio anual de eventos peligrosos N (Anexo A, NTC 4552-2:2023).
"""

from calculate_risk.norma import areas


def n_d(N_G: float, A_D: float, cd: float) -> float:
    """N_D: descargas directas en la estructura (ec. A.4)."""
    return N_G * A_D * cd * 1e-6


def n_dj(N_G: float, A_DJ: float, cdj: float, ct: float) -> float:
    """N_DJ: descargas directas en una estructura adyacente (ec. A.5)."""
    return N_G * A_DJ * cdj * ct * 1e-6


def n_m(N_G: float, L: float, W: float) -> float:
    """N_M: descargas cerca de la estructura (ec. A.6)."""
    return N_G * areas.area_descargas_cercanas(L, W) * 1e-6


def n_l(N_G: float, L_L: float, ci: float, ce: float, ct: float) -> float:
    """N_L: descargas directas en una línea (ec. A.8)."""
    return N_G * areas.area_linea_descargas_directas(L_L) * ci * ce * ct * 1e-6


def n_i(N_G: float, L_L: float, ci: float, ce: float, ct: float) -> float:
    """N_I: descargas cerca de una línea (ec. A.10)."""
    return N_G * areas.area_linea_descargas_cercanas(L_L) * ci * ce * ct * 1e-6