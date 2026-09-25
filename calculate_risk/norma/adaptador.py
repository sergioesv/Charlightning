"""
Paso 36c: traduce el diccionario de la pantalla vieja (VAR) a los objetos del
modelo nuevo, para poder calcular con `calculate_risk.norma` sin cambiar la GUI.

La pantalla vieja tiene limitaciones que el modelo nuevo no tiene (una sola
zona, L_L fijo en 1000 m, un solo juego de DPS, un solo P_LI para todas las
líneas). El adaptador las traduce de la forma más fiel posible y deja por
fuera lo que la pantalla simplemente no pregunta.

Diferencias conocidas frente a `calculate_risk.calculo.calcular_riesgo`:
  - R_Z: el cálculo viejo usa ΔN = N_I − N_L; la norma usa N_I (errata H15).
  - L4: el cálculo viejo multiplica L_B4 por h4; la ec. (C.12) no lleva h_z.
  - P_C: el cálculo viejo usa P_DPS solo; la ec. (B.2) es P_DPS × C_LD.
"""
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona

LONGITUD_LINEA_PANTALLA = 1000.0   # la pantalla no pregunta L_L (limitación H16)

C_I_AEREA = 1.0
C_I_SUBTERRANEA = 0.5


def _p_dps_y_p_eb(P_B: float, SP: float):
    """Igual que calculate_risk.probabilidades.calcular_P_SPD_y_P_EB, pero sin
    importar el módulo viejo: SP=0 sin medidas, SP=1 DPS solo en la entrada,
    SP=2 DPS coordinados (ambos bajan al NPR que corresponda a P_B)."""
    if SP == 0:
        return 1.0, 1.0
    npr = {0.2: 0.05, 0.1: 0.05, 0.05: 0.02, 0.02: 0.01}.get(P_B, 0.05)
    if SP == 1:
        return 1.0, npr
    return npr, npr


def _lineas(datos: dict, P_EB: float) -> list:
    """Las cuatro líneas posibles de la pantalla, repetidas según su cantidad."""
    comun = dict(
        L_L=LONGITUD_LINEA_PANTALLA,
        C_E=datos["C_e"],
        C_LD=datos["C_LD"],
        C_LI=datos["C_LI"],
        P_LI=datos["P_LI"],
        P_EB=P_EB,
    )

    plantillas = [
        # (cuántas, nombre, C_I, C_T, P_LD)
        (1 if datos["pl"] == 1 else 0, "potencia_aerea", C_I_AEREA, datos["C_t0"], datos["P_LD0"]),
        (1 if datos["pl"] == 2 else 0, "potencia_subterranea", C_I_SUBTERRANEA, datos["C_t0"], datos["P_LD0"]),
        (datos["n_oh"], "servicio_aereo", C_I_AEREA, datos["C_t1"], datos["P_LD1"]),
        (datos["n_ug"], "servicio_subterraneo", C_I_SUBTERRANEA, datos["C_t2"], datos["P_LD2"]),
    ]

    lineas = []
    for cuantas, nombre, C_I, C_T, P_LD in plantillas:
        for i in range(int(cuantas)):
            sufijo = "" if cuantas == 1 else f"_{i + 1}"
            lineas.append(Linea(nombre + sufijo, C_I=C_I, C_T=C_T, P_LD=P_LD, **comun))
    return lineas


def _zona(datos: dict, tipo: int, P_B: float, P_DPS: float) -> Zona:
    """La única zona de la pantalla, con las pérdidas del tipo de riesgo pedido."""
    if datos["Ks4"] <= 0:
        raise ValueError("Ks4 debe ser mayor que 0 (K_S4 = 1/U_W)")

    comun = dict(
        P_TA=datos["P_A"],
        P_TU=datos["P_TU"],
        P_B=P_B,
        K_S1=datos["Ks1"],
        K_S2=datos["Ks2"],
        sistemas_internos=[
            SistemaInterno(
                "sistemas_internos",
                linea="",                      # un solo juego de DPS para todo
                K_S3=datos["Ks3"],
                U_W=1 / datos["Ks4"],          # K_S4 = 1/U_W
                P_DPS=P_DPS,
            )
        ],
        r_p=datos["r"],
        r_f=datos["r_f"],
        n_z=1.0,
        t_z=8760.0,
    )

    if tipo == 1:
        return Zona("pantalla", r_t=datos["R_a"], h_z=datos["h_1"],
                    L_T=datos["L_t1"], L_F=datos["L_f1"], L_O=datos["L_o1"], **comun)
    if tipo == 2:
        return Zona("pantalla", L_F=datos["L_f2"], L_O=datos["L_o2"], **comun)
    if tipo == 3:
        # c_z/c_t = 1: la pantalla no pregunta el valor del patrimonio.
        return Zona("pantalla", L_F=datos["L_f3"], c_z=1.0, **comun)
    if tipo == 4:
        # h4 NO se usa: la ec. (C.12) no lleva h_z (el cálculo viejo sí lo mete).
        return Zona("pantalla", r_t=datos["R_a"],
                    L_T=datos["L_t4"], L_F=datos["L_f4"], L_O=datos["L_o4"],
                    razones_l4_unitarias=True, **comun)
    raise ValueError("El tipo de riesgo debe ser 1, 2, 3 o 4")


def caso_desde_pantalla(datos: dict, tipo: int = 1) -> dict:
    """Traduce el diccionario de la pantalla a lo que espera riesgos.evaluar:
    {"estructura": ..., "lineas": [...], "zonas": [...], "N_G": ..., "tipos": (tipo,)}."""
    P_B = 1 - datos["E"]
    P_DPS, P_EB = _p_dps_y_p_eb(P_B, datos["SP"])

    estructura = Estructura(
        L=datos["L"], W=datos["W"], H=datos["H"], H_p=datos["H_P"],
        C_D=datos["C_d"],
        n_t=1.0, c_t=1.0,
        riesgo_explosion_o_vital=datos["L_o1"] > 0,
        hay_animales=datos["L_t4"] > 0,
    )

    return {
        "estructura": estructura,
        "lineas": _lineas(datos, P_EB),
        "zonas": [_zona(datos, tipo, P_B, P_DPS)],
        "N_G": datos["DDT"],
        "tipos": (tipo,),
    }