"""Cálculo completo del riesgo, de principio a fin, sin ventanas.

La función principal es calcular_riesgo(datos): recibe un diccionario
con los datos de entrada y devuelve otro con todos los resultados.
"""

from calculate_risk.areas import calcular_A_d, calcular_N_D, calcular_A_m, calcular_N_M
from calculate_risk.lineas import (
    calcular_A_l_aerea,
    calcular_A_i_aerea,
    calcular_A_l_subterranea,
    calcular_A_i_subterranea,
    calcular_N_L,
    calcular_N_I,
    calcular_delta_N,
)
from calculate_risk.probabilidades import (
    calcular_P_B,
    calcular_P_SPD_y_P_EB,
    calcular_K_MS,
    calcular_P_MS,
    calcular_P_Z,
)
from calculate_risk.perdidas import calcular_L_A, calcular_L_B
from calculate_risk.riesgos import calcular_componente, calcular_X


def calcular_riesgo(datos):
    """Calcula los riesgos R1, R2, R3 y R4 con todos sus componentes.

    datos: diccionario con los datos de entrada (dimensiones, DDT,
           factores elegidos en la pantalla, etc.). No se modifica.
    Devuelve un diccionario nuevo con los datos de entrada más
    todos los resultados intermedios y finales.
    """
    v = dict(datos)  # copia, para no modificar el diccionario original
    _eventos_estructura(v)
    _eventos_lineas(v)
    _riesgo_1(v)
    _riesgo_2(v)
    _riesgo_3(v)
    _riesgo_4(v)
    return v


def _eventos_estructura(v):
    """Secciones 3.1 y 3.2: rayos sobre la estructura y cerca de ella."""
    v["N_g"] = v["DDT"]
    v["A_d"] = calcular_A_d(v["L"], v["W"], v["H"], v["H_P"])
    v["N_D"] = calcular_N_D(v["N_g"], v["A_d"], v["C_d"])
    v["A_m"] = calcular_A_m(v["L"], v["W"])
    v["N_M"] = calcular_N_M(v["N_g"], v["A_m"])


def _eventos_lineas(v):
    """Secciones 4 y 5: rayos sobre las líneas de servicio y cerca de ellas.

    C_I es el factor de instalación de la Tabla A.2 (aérea = 1,
    subterránea = 0,5); con esta edición de la norma, el área colectora
    ya no depende de si la línea es aérea o subterránea, solo C_I.
    """
    v["L_1"] = 1000
    v["L_2"] = 1000
    v["n_ohp"] = 1 if v["pl"] == 1 else 0
    v["n_ugp"] = 1 if v["pl"] == 2 else 0

    C_I_aerea = 1.0
    C_I_subterranea = 0.5

    # 4.1 y 4.2: líneas aéreas
    v["A_c1"] = calcular_A_l_aerea(v["L_1"])
    v["N_L1p"] = calcular_N_L(v["N_g"], v["A_c1"], C_I_aerea, v["C_e"], v["C_t0"])
    v["N_L1"] = calcular_N_L(v["N_g"], v["A_c1"], C_I_aerea, v["C_e"], v["C_t1"])
    v["A_l1"] = calcular_A_i_aerea(v["L_1"])
    v["N_I1p"] = calcular_N_I(v["N_g"], v["A_l1"], C_I_aerea, v["C_e"], v["C_t0"])
    v["N_I1"] = calcular_N_I(v["N_g"], v["A_l1"], C_I_aerea, v["C_e"], v["C_t1"])

    # 5.1 y 5.2: líneas subterráneas
    v["L_c2"] = v["L_2"]
    v["A_c2"] = calcular_A_l_subterranea(v["L_c2"])
    v["N_L2p"] = calcular_N_L(v["N_g"], v["A_c2"], C_I_subterranea, v["C_e"], v["C_t0"])
    v["N_L2"] = calcular_N_L(v["N_g"], v["A_c2"], C_I_subterranea, v["C_e"], v["C_t2"])
    v["A_l2"] = calcular_A_i_subterranea(v["L_c2"])
    v["N_I2p"] = calcular_N_I(v["N_g"], v["A_l2"], C_I_subterranea, v["C_e"], v["C_t0"])
    v["N_I2"] = calcular_N_I(v["N_g"], v["A_l2"], C_I_subterranea, v["C_e"], v["C_t2"])


def _riesgo_1(v):
    """Sección 6: pérdida de vidas humanas (R1)."""
    # 6.1 R_A: tensiones de paso y contacto
    v["L_a1"] = calcular_L_A(v["R_a"], v["L_t1"])
    v["R_A1"] = calcular_componente(v["N_D"], v["P_A"], v["L_a1"])

    # 6.2 R_B: daño físico
    v["L_B1"] = calcular_L_B(v["r"], v["h_1"], v["r_f"], v["L_f1"])
    v["P_B1"] = calcular_P_B(v["E"])
    v["R_B1"] = calcular_componente(v["N_D"], v["P_B1"], v["L_B1"])

    # 6.3 protección contra sobretensiones
    v["P_SPD"], v["P_EB"] = calcular_P_SPD_y_P_EB(v["P_B1"], v["SP"])

    # 6.4 R_C: falla de equipos por impacto directo
    v["P_C1"] = v["P_SPD"]
    v["L_C1"] = v["L_o1"]
    v["R_C1"] = calcular_componente(v["N_D"], v["P_C1"], v["L_C1"])

    # 6.5 R_M: falla de equipos por impactos cercanos
    v["K_MS1"] = calcular_K_MS(v["Ks1"], v["Ks2"], v["Ks3"], v["Ks4"])
    v["P_MS1"] = calcular_P_MS(v["K_MS1"])
    v["P_M1"] = v["P_SPD"] * v["P_MS1"]
    v["L_M1"] = v["L_o1"]
    v["R_M1"] = calcular_componente(v["N_M"], v["P_M1"], v["L_M1"])

    # 6.6 R_U: lesiones por impactos directos a las líneas
    # P_U = P_TU * P_EB * P_LD * C_LD (ecuación B.8). P_TU (Tabla B.6,
    # medidas contra tensión de contacto) y C_LD (Tabla B.4, apantallamiento/
    # puesta a tierra de la línea) se dejan en 1 (el caso más desfavorable:
    # sin medidas adicionales) porque la pantalla aún no pide esos datos.
    # PENDIENTE: agregar P_TU y C_LD como opciones de la pantalla.
    P_TU = 1
    C_LD = 1
    v["P_U1p"] = P_TU * v["P_EB"] * v["P_LD0"] * C_LD
    v["P_U1oh"] = P_TU * v["P_EB"] * v["P_LD1"] * C_LD
    v["P_U1ug"] = P_TU * v["P_EB"] * v["P_LD2"] * C_LD
    v["X_U1"] = calcular_X([
        (v["n_ohp"], v["N_L1p"], v["P_U1p"]),
        (v["n_oh"], v["N_L1"], v["P_U1oh"]),
        (v["n_ugp"], v["N_L2p"], v["P_U1p"]),
        (v["n_ug"], v["N_L2"], v["P_U1ug"]),
    ])
    v["L_U1"] = calcular_L_A(v["R_a"], v["L_t1"])
    v["R_U1"] = v["X_U1"] * v["L_U1"]

    # 6.7 R_V: daño físico por impactos directos a las líneas
    v["X_V1"] = v["X_U1"]
    v["L_V1"] = v["L_B1"]
    v["R_V1"] = v["X_V1"] * v["L_V1"]

    # 6.8 R_W: falla de equipos por impactos directos a las líneas
    v["P_W1p"] = v["P_SPD"] * v["P_LD0"] * C_LD
    v["P_W1oh"] = v["P_SPD"] * v["P_LD1"] * C_LD
    v["P_W1ug"] = v["P_SPD"] * v["P_LD2"] * C_LD
    v["X_W1"] = calcular_X([
        (v["n_ohp"], v["N_L1p"], v["P_W1p"]),
        (v["n_oh"], v["N_L1"], v["P_W1oh"]),
        (v["n_ugp"], v["N_L2p"], v["P_W1p"]),
        (v["n_ug"], v["N_L2"], v["P_W1ug"]),
    ])
    v["L_W1"] = v["L_o1"]
    v["R_W1"] = v["X_W1"] * v["L_W1"]

    # 6.9 R_Z: falla de equipos por impactos cerca de las líneas
    # P_Z = P_DPS * P_LI * C_LI (ecuación B.11). P_LI (Tabla B.9, según la
    # tensión soportada de los equipos) y C_LI (Tabla B.4) se dejan en 1
    # (caso más desfavorable) porque la pantalla aún no pide esos datos.
    # Corregido: antes R_Z reutilizaba por aproximación los valores de
    # P_W (Tabla B.8, para corriente directa en la línea), que no es la
    # tabla que corresponde a este componente (impacto cerca de la línea).
    # PENDIENTE: agregar P_LI y C_LI como opciones de la pantalla.
    P_LI = 1
    C_LI = 1
    v["P_Z1"] = calcular_P_Z(v["P_SPD"], P_LI, C_LI)
    v["DELTA_N_1p"] = calcular_delta_N(v["N_I1p"], v["N_L1p"])
    v["DELTA_N_1"] = calcular_delta_N(v["N_I1"], v["N_L1"])
    v["DELTA_N_2p"] = calcular_delta_N(v["N_I2p"], v["N_L2p"])
    v["DELTA_N_2"] = calcular_delta_N(v["N_I2"], v["N_L2"])
    v["X_Z1"] = calcular_X([
        (v["n_ohp"], v["DELTA_N_1p"], v["P_Z1"]),
        (v["n_oh"], v["DELTA_N_1"], v["P_Z1"]),
        (v["n_ugp"], v["DELTA_N_2p"], v["P_Z1"]),
        (v["n_ug"], v["DELTA_N_2"], v["P_Z1"]),
    ])
    v["L_Z1"] = v["L_o1"]
    v["R_Z1"] = v["X_Z1"] * v["L_Z1"]

    # 6.10 totales
    v["R_d1"] = v["R_A1"] + v["R_B1"] + v["R_C1"]
    v["R_i1"] = v["R_M1"] + v["R_U1"] + v["R_V1"] + v["R_W1"] + v["R_Z1"]
    v["R_1"] = v["R_d1"] + v["R_i1"]
    # Riesgo agrupado por tipo de daño: S = lesiones, F = físico, o = equipos
    v["R_S1"] = v["R_A1"] + v["R_U1"]
    v["R_F1"] = v["R_B1"] + v["R_V1"]
    v["R_o1"] = v["R_C1"] + v["R_M1"] + v["R_W1"] + v["R_Z1"]


def _riesgo_2(v):
    """Sección 7: pérdida de servicio público esencial (R2)."""
    v["L_B2"] = calcular_L_B(v["r"], 1, v["r_f"], v["L_f2"])
    v["R_B2"] = calcular_componente(v["N_D"], v["P_B1"], v["L_B2"])
    v["R_C2"] = calcular_componente(v["N_D"], v["P_C1"], v["L_o2"])
    v["R_M2"] = calcular_componente(v["N_M"], v["P_M1"], v["L_o2"])
    v["R_V2"] = v["X_V1"] * v["L_B2"]
    v["R_W2"] = v["X_W1"] * v["L_o2"]
    v["R_Z2"] = v["X_Z1"] * v["L_o2"]
    v["R_d2"] = v["R_B2"] + v["R_C2"]
    v["R_i2"] = v["R_M2"] + v["R_V2"] + v["R_W2"] + v["R_Z2"]
    v["R_2"] = v["R_d2"] + v["R_i2"]
    v["R_F2"] = v["R_B2"] + v["R_V2"]
    v["R_o2"] = v["R_C2"] + v["R_M2"] + v["R_W2"] + v["R_Z2"]


def _riesgo_3(v):
    """Sección 8: pérdida de patrimonio cultural (R3)."""
    v["L_B3"] = calcular_L_B(v["r"], 1, v["r_f"], v["L_f3"])
    v["R_B3"] = calcular_componente(v["N_D"], v["P_B1"], v["L_B3"])
    v["R_V3"] = v["X_V1"] * v["L_B3"]
    v["R_d3"] = v["R_B3"]
    v["R_i3"] = v["R_V3"]
    v["R_3"] = v["R_d3"] + v["R_i3"]
    v["R_F3"] = v["R_B3"] + v["R_V3"]
    v["R_o3"] = 0


def _riesgo_4(v):
    """Sección 9: pérdida económica (R4)."""
    v["L_a4"] = calcular_L_A(v["R_a"], v["L_t4"])
    v["R_A4"] = calcular_componente(v["N_D"], v["P_A"], v["L_a4"])
    v["L_B4"] = calcular_L_B(v["r"], v["h4"], v["r_f"], v["L_f4"])
    v["R_B4"] = calcular_componente(v["N_D"], v["P_B1"], v["L_B4"])
    v["R_C4"] = calcular_componente(v["N_D"], v["P_C1"], v["L_o4"])
    v["R_M4"] = calcular_componente(v["N_M"], v["P_M1"], v["L_o4"])
    v["R_U4"] = v["X_U1"] * v["L_a4"]
    v["R_V4"] = v["X_V1"] * v["L_B4"]
    v["R_W4"] = v["X_W1"] * v["L_o4"]
    v["R_Z4"] = v["X_Z1"] * v["L_o4"]
    v["R_d4"] = v["R_A4"] + v["R_B4"] + v["R_C4"]
    v["R_i4"] = v["R_M4"] + v["R_U4"] + v["R_V4"] + v["R_W4"] + v["R_Z4"]
    v["R_4"] = v["R_d4"] + v["R_i4"]
    v["R_S4"] = v["R_A4"] + v["R_U4"]
    v["R_F4"] = v["R_B4"] + v["R_V4"]
    v["R_o4"] = v["R_C4"] + v["R_M4"] + v["R_W4"] + v["R_Z4"]