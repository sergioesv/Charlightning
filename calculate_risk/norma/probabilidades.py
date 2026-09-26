"""
Probabilidades de daño P_X (Anexo B, NTC 4552-2:2023).
"""


def p_a(p_ta: float, p_b: float) -> float:
    """P_A: lesiones a seres vivos por descarga en la estructura (ec. B.1)."""
    return p_ta * p_b


def p_c(p_dps: float, c_ld: float) -> float:
    """P_C: falla de sistemas internos por descarga en la estructura (ec. B.2)."""
    return p_dps * c_ld


FACTOR_MALLA = 0.12   # ec. (B.5) y (B.6): K_S = 0,12 x w_m


def k_s1(w_m1: float) -> float:
    """K_S1: eficacia del blindaje en el límite de zona 0/1 (ec. B.5, tope 1)."""
    return min(FACTOR_MALLA * w_m1, 1)


def k_s2(w_m2: float) -> float:
    """K_S2: eficacia del blindaje en el límite de zona X/Y (ec. B.6, tope 1)."""
    return min(FACTOR_MALLA * w_m2, 1)


def w_m_desde_k_s(k_s: float) -> float:
    """El ancho de malla que da ese K_S: inversa de las ec. (B.5) y (B.6).

    Hace falta para volver a llenar la pantalla desde un caso guardado, que
    guarda K_S y no el ancho de la malla."""
    return k_s / FACTOR_MALLA


def k_s4(u_w: float) -> float:
    """K_S4: capacidad del sistema de soportar impulsos de tensión (ec. B.7, tope 1)."""
    return min(1 / u_w, 1)


def p_ms(k_s1_: float, k_s2_: float, k_s3: float, k_s4_: float) -> float:
    """P_MS: falla por descarga cerca de la estructura, con SPCI (ec. B.4, tope 1)."""
    return min((k_s1_ * k_s2_ * k_s3 * k_s4_) ** 2, 1)


def p_m(p_dps: float, p_ms_: float) -> float:
    """P_M: falla de sistemas internos por descarga cerca (ec. B.3)."""
    return p_dps * p_ms_


def p_u(p_tu: float, p_eb: float, p_ld: float, c_ld: float) -> float:
    """P_U: lesiones por descarga en una línea entrante (ec. B.8)."""
    return p_tu * p_eb * p_ld * c_ld


def p_v(p_eb: float, p_ld: float, c_ld: float) -> float:
    """P_V: daño físico por descarga en una línea (ec. B.9)."""
    return p_eb * p_ld * c_ld


def p_w(p_dps: float, p_ld: float, c_ld: float) -> float:
    """P_W: falla de sistemas internos por descarga en una línea (ec. B.10)."""
    return p_dps * p_ld * c_ld


def p_z(p_dps: float, p_li: float, c_li: float) -> float:
    """P_Z: falla de sistemas internos por descarga cerca de una línea (ec. B.11)."""
    return p_dps * p_li * c_li


def combinar(probabilidades) -> float:
    """Combina varias probabilidades de sistemas internos en una zona:
    P = 1 - producto(1 - P_i) (ec. 14, 15)."""
    ps = list(probabilidades)
    if not ps:
        return 0.0
    resultado = 1.0
    for p in ps:
        resultado *= (1.0 - p)
    return 1.0 - resultado


