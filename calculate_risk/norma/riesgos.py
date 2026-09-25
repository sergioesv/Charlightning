"""
Componentes de riesgo R_X y riesgos totales R1-R4 (numeral 6, NTC 4552-2:2023).

NOTA: la ecuación (6) impresa dice R_A = N_A x P_B x L_A, pero la Tabla 6
(resumen) confirma R_A = N_D x P_A x L_A -- errata ya documentada, se usa
la versión de la Tabla 6.
"""


from calculate_risk.norma import areas, frecuencias, perdidas, probabilidades, tablas


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




# ============================================================
# Orquestación: recorrer un Caso completo (zonas y líneas)
# ============================================================

COMPONENTES = ("R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z")


def componentes_aplicables(tipo: int, estructura) -> set:
    """Componentes que intervienen en el riesgo indicado (numeral 4.3)."""
    if tipo == 1:
        base = {"R_A", "R_B", "R_U", "R_V"}
        if estructura.riesgo_explosion_o_vital:
            base |= {"R_C", "R_M", "R_W", "R_Z"}
        return base
    if tipo == 2:
        return {"R_B", "R_C", "R_M", "R_V", "R_W", "R_Z"}
    if tipo == 3:
        return {"R_B", "R_V"}
    if tipo == 4:
        base = {"R_B", "R_C", "R_M", "R_V", "R_W", "R_Z"}
        if estructura.hay_animales:
            base |= {"R_A", "R_U"}
        return base
    raise ValueError("El tipo de riesgo debe ser 1, 2, 3 o 4")


def _perdidas_zona(zona, tipo: int, n_t: float, c_t: float) -> tuple:
    """L_A, L_B, L_C de la zona según el tipo de pérdida (1-4)."""
    if tipo == 1:
        L_A = perdidas.l_a1(zona.r_t, zona.L_T, zona.n_z, n_t, zona.t_z)
        L_B = perdidas.l_b1(zona.r_p, zona.r_f, zona.h_z, zona.L_F, zona.n_z, n_t, zona.t_z)
        L_C = perdidas.l_c1(zona.L_O, zona.n_z, n_t, zona.t_z)
    elif tipo == 2:
        L_A = 0.0
        L_B = perdidas.l_b2(zona.r_p, zona.r_f, zona.L_F, zona.n_z, n_t)
        L_C = perdidas.l_c2(zona.L_O, zona.n_z, n_t)
    elif tipo == 3:
        L_A = 0.0
        L_B = perdidas.l_b3(zona.r_p, zona.r_f, zona.L_F, zona.c_z, c_t)
        L_C = 0.0
    elif tipo == 4:
        L_A = perdidas.l_a4(zona.r_t, zona.L_T, zona.c_a, c_t)
        L_B = perdidas.l_b4(zona.r_p, zona.r_f, zona.L_F, zona.c_a, zona.c_b, zona.c_c, zona.c_s, c_t)
        L_C = perdidas.l_c4(zona.L_O, zona.c_s, c_t)
    else:
        raise ValueError("El tipo de pérdida debe ser 1, 2, 3 o 4")
    return L_A, L_B, L_C


def evaluar_zona(zona, estructura, lineas, N_G: float, tipo: int) -> dict:
    """Calcula los componentes de riesgo de una zona para un tipo de pérdida (1-4)."""
    A_D = areas.area_estructura_completa(estructura.L, estructura.W, estructura.H, estructura.H_p)
    N_D = frecuencias.n_d(N_G, A_D, estructura.C_D)
    N_M = frecuencias.n_m(N_G, estructura.L, estructura.W)

    L_A, L_B, L_C = _perdidas_zona(zona, tipo, estructura.n_t, estructura.c_t)
    L_U, L_V, L_M, L_W, L_Z = L_A, L_B, L_C, L_C, L_C

    C_LD_por_linea = {ln.nombre: ln.C_LD for ln in lineas}

    P_A = probabilidades.p_a(zona.P_TA, zona.P_B)
    P_B = zona.P_B
    P_C = probabilidades.combinar(
        probabilidades.p_c(si.P_DPS, C_LD_por_linea.get(si.linea, 1.0))
        for si in zona.sistemas_internos
    )
    P_M = probabilidades.combinar(
        probabilidades.p_m(
            si.P_DPS,
            probabilidades.p_ms(zona.K_S1, zona.K_S2, si.K_S3, probabilidades.k_s4(si.U_W)),
        )
        for si in zona.sistemas_internos
    )

    aplica = componentes_aplicables(tipo, estructura)
    R = {c: 0.0 for c in COMPONENTES}

    if "R_A" in aplica and not zona.exterior_sin_personas:
        R["R_A"] = r_a(N_D, P_A, L_A)
    if "R_B" in aplica:
        R["R_B"] = r_b(N_D, P_B, L_B)
    if "R_C" in aplica:
        R["R_C"] = r_c(N_D, P_C, L_C)
    if "R_M" in aplica:
        R["R_M"] = r_m(N_M, P_M, L_M)

    for ln in lineas:
        N_L = frecuencias.n_l(N_G, ln.L_L, ln.C_I, ln.C_E, ln.C_T)
        N_I = frecuencias.n_i(N_G, ln.L_L, ln.C_I, ln.C_E, ln.C_T)
        N_DJ = 0.0
        if ln.adyacente is not None:
            A_DJ = areas.area_estructura_completa(
                ln.adyacente.L, ln.adyacente.W, ln.adyacente.H, ln.adyacente.H_p
            )
            N_DJ = frecuencias.n_dj(N_G, A_DJ, ln.C_DJ, ln.C_T)

        P_DPS_list = [si.P_DPS for si in zona.sistemas_internos if si.linea == ln.nombre] or [1.0]

        P_U = probabilidades.p_u(zona.P_TU, ln.P_EB, ln.P_LD, ln.C_LD)
        P_V = probabilidades.p_v(ln.P_EB, ln.P_LD, ln.C_LD)
        P_W = probabilidades.combinar(probabilidades.p_w(p, ln.P_LD, ln.C_LD) for p in P_DPS_list)
        P_Z = probabilidades.combinar(probabilidades.p_z(p, ln.P_LI, ln.C_LI) for p in P_DPS_list)

        if "R_U" in aplica and not zona.exterior_sin_personas:
            R["R_U"] += r_u(N_L, N_DJ, P_U, L_U)
        if "R_V" in aplica:
            R["R_V"] += r_v(N_L, N_DJ, P_V, L_V)
        if "R_W" in aplica:
            R["R_W"] += r_w(N_L, N_DJ, P_W, L_W)
        if "R_Z" in aplica:
            R["R_Z"] += r_z(N_I, P_Z, L_Z)

    R["total"] = sum(R[c] for c in COMPONENTES)
    return R


def evaluar(estructura, lineas, zonas, N_G: float, tipos=(1,)) -> dict:
    """Evalúa los riesgos indicados (1-4) sumando todas las zonas de la estructura."""
    resultados = {}
    for tipo in tipos:
        por_zona = {}
        acumulado = {c: 0.0 for c in COMPONENTES}
        for zona in zonas:
            r = evaluar_zona(zona, estructura, lineas, N_G, tipo)
            por_zona[zona.nombre] = r
            for c in COMPONENTES:
                acumulado[c] += r[c]
        total = sum(acumulado.values())
        R_T = tablas.RT[f"L{tipo}"]
        resultados[tipo] = {
            **acumulado,
            "total": total,
            "R_T": R_T,
            "cumple": total <= R_T,
            "zonas": por_zona,
        }
    return resultados
