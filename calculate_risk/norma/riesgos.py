"""
Componentes de riesgo R_X y riesgos totales R1-R4 (numeral 6, NTC 4552-2:2023).

NOTA: la ecuación (6) impresa dice R_A = N_A x P_B x L_A, pero la Tabla 6
(resumen) confirma R_A = N_D x P_A x L_A -- errata ya documentada, se usa
la versión de la Tabla 6.
"""


def r_a(N_D: float, P_A: float, L_A: float) -> float:
    """R_A: lesiones a seres vivos por descarga directa en la estructura (ec. 6)."""
    return N_D * P_A * L_A


def r_b(N_D: float, P_B: float, L_B: float) -> float:
    """R_B: daño físico por descarga directa en la estructura (ec. 7)."""
    return N_D * P_B * L_B


def r_c(N_D: float, P_C: float, L_C: float) -> float:
    """R_C: falla de sistemas internos por descarga directa en la estructura (ec. 8)."""
    return N_D * P_C * L_C


def r_m(N_M: float, P_M: float, L_M: float) -> float:
    """R_M: falla de sistemas internos por descarga cerca de la estructura (ec. 9)."""
    return N_M * P_M * L_M


def r_u(N_L: float, N_DJ: float, P_U: float, L_U: float) -> float:
    """R_U: lesiones por descarga en una línea entrante (ec. 10)."""
    return (N_L + N_DJ) * P_U * L_U


def r_v(N_L: float, N_DJ: float, P_V: float, L_V: float) -> float:
    """R_V: daño físico por descarga en una línea entrante (ec. 11)."""
    return (N_L + N_DJ) * P_V * L_V


def r_w(N_L: float, N_DJ: float, P_W: float, L_W: float) -> float:
    """R_W: falla de sistemas internos por descarga en una línea entrante (ec. 12)."""
    return (N_L + N_DJ) * P_W * L_W


def r_z(N_I: float, P_Z: float, L_Z: float) -> float:
    """R_Z: falla de sistemas internos por descarga cerca de una línea (ec. 13)."""
    return N_I * P_Z * L_Z


def r1(r_a_: float, r_b_: float, r_c_: float, r_m_: float, r_u_: float, r_v_: float, r_w_: float, r_z_: float) -> float:
    """R1: riesgo de pérdida de vidas humanas -- suma de los 8 componentes."""
    return r_a_ + r_b_ + r_c_ + r_m_ + r_u_ + r_v_ + r_w_ + r_z_


def r2(r_b_: float, r_c_: float, r_m_: float, r_v_: float, r_w_: float, r_z_: float) -> float:
    """R2: riesgo de pérdida de servicio público -- sin R_A ni R_U."""
    return r_b_ + r_c_ + r_m_ + r_v_ + r_w_ + r_z_


def r3(r_b_: float, r_v_: float) -> float:
    """R3: riesgo de pérdida de patrimonio cultural -- solo daño físico."""
    return r_b_ + r_v_


def r4(r_a_: float, r_b_: float, r_c_: float, r_m_: float, r_u_: float, r_v_: float, r_w_: float, r_z_: float) -> float:
    """R4: riesgo de pérdida económica -- suma de los 8 componentes."""
    return r_a_ + r_b_ + r_c_ + r_m_ + r_u_ + r_v_ + r_w_ + r_z_