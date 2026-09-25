"""
Análisis costo-beneficio de las pérdidas (Anexo D, NTC 4552-2:2023).
"""


def c_lz(r4z: float, ct: float) -> float:
    """C_LZ: costo de las pérdidas en una zona, sin protección (ec. D.1)."""
    return r4z * ct


def c_l(r4: float, ct: float) -> float:
    """C_L: costo total de las pérdidas en la estructura, sin protección (ec. D.2)."""
    return r4 * ct


def c_rlz(r4z_prima: float, ct: float) -> float:
    """C_RLZ: costo de pérdidas residuales en una zona, con protección (ec. D.3)."""
    return r4z_prima * ct


def c_rl(r4_prima: float, ct: float) -> float:
    """C_RL: costo total de pérdidas residuales, con protección (ec. D.4)."""
    return r4_prima * ct


def c_pm(cp: float, i: float, a: float, m: float) -> float:
    """C_PM: costo anual de las medidas de protección (ec. D.5)."""
    return cp * (i + a + m)


def s_m(c_l_: float, c_pm_: float, c_rl_: float) -> float:
    """S_M: ahorro anual; la protección se justifica si S_M > 0 (ec. D.6)."""
    return c_l_ - (c_pm_ + c_rl_)