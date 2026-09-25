"""
Pérdidas L_X en una estructura (Anexo C, NTC 4552-2:2023).
"""


# ---------- L1: pérdida de vidas humanas ----------

def l_a1(rt: float, LT: float, nz: float, nt: float, tz: float) -> float:
    """L_A = L_U: pérdida por tensión de paso/contacto, D1 (ec. C.1 = C.2)."""
    return rt * LT * (nz / nt) * (tz / 8760)


def l_b1(rp: float, rf: float, hz: float, LF: float, nz: float, nt: float, tz: float) -> float:
    """L_B = L_V: daño físico, D2 (ec. C.3)."""
    return rp * rf * hz * LF * (nz / nt) * (tz / 8760)


def l_c1(LO: float, nz: float, nt: float, tz: float) -> float:
    """L_C = L_M = L_W = L_Z: falla de sistemas internos, D3 (ec. C.4)."""
    return LO * (nz / nt) * (tz / 8760)


# ---------- L2: pérdida de servicio público ----------

def l_b2(rp: float, rf: float, LF: float, nz: float, nt: float) -> float:
    """L_B = L_V: daño físico, D2 (ec. C.7)."""
    return rp * rf * LF * (nz / nt)


def l_c2(LO: float, nz: float, nt: float) -> float:
    """L_C = L_M = L_W = L_Z: falla de sistemas internos, D3 (ec. C.8)."""
    return LO * (nz / nt)


# ---------- L3: pérdida de patrimonio cultural ----------

def l_b3(rp: float, rf: float, LF: float, cz: float, ct: float) -> float:
    """L_B = L_V: daño físico, D2 (ec. C.9). Única componente de L3."""
    return rp * rf * LF * (cz / ct)


# ---------- L4: pérdida económica ----------

def l_a4(rt: float, LT: float, ca: float, ct: float) -> float:
    """L_A = L_U: pérdida por tensión de paso/contacto en animales, D1 (ec. C.10 = C.11)."""
    return rt * LT * (ca / ct)


def l_b4(rp: float, rf: float, LF: float, ca: float, cb: float, cc: float, cs: float, ct: float) -> float:
    """L_B = L_V: daño físico, D2 (ec. C.12)."""
    return rp * rf * LF * ((ca + cb + cc + cs) / ct)


def l_c4(LO: float, cs: float, ct: float) -> float:
    """L_C = L_M = L_W = L_Z: falla de sistemas internos, D3 (ec. C.13)."""
    return LO * (cs / ct)


# ---------- Pérdidas adicionales por daño al medioambiente exterior ----------

def l_ft(LF: float, LFE: float, ce: float, ct: float) -> float:
    """L_FT = L_F + L_E, con L_E = L_FE × ce/ct (ec. C.14, C.15)."""
    LE = LFE * (ce / ct)
    return LF + LE