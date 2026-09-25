"""
Tablas y valores normativos de NTC 4552-2:2023.

Este módulo contiene únicamente datos normativos.
No realiza cálculos ni depende de la interfaz gráfica.
"""


# ============================================================
# RIESGO TOLERABLE - TABLA 4
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


    
# ============================================================
# TABLA A.1 - FACTOR DE LOCALIZACIÓN DE LA ESTRUCTURA CD
# ============================================================

CD = {
    "rodeada_objetos_mas_altos": 0.25,
    "rodeada_objetos_misma_altura_o_inferior": 0.5,
    "aislada": 1,
    "aislada_colina_o_monticulo": 2,
}


# ============================================================
# TABLA A.2 - FACTOR DE INSTALACIÓN DE LÍNEA CI
# ============================================================

CI = {
    "aerea": 1,
    "subterranea": 0.5,
    "subterranea_bajo_malla_puesta_a_tierra": 0.01,
}


# ============================================================
# TABLA A.3 - FACTOR TIPO DE LÍNEA CT
# ============================================================

CT = {
    "bt_datos_telecomunicacion": 1,
    "at_con_transformador": 0.2,
}


# ============================================================
# TABLA A.4 - FACTOR MEDIOAMBIENTAL DE LA LÍNEA CE
# ============================================================

CE = {
    "rural": 1,
    "suburbano": 0.5,
    "urbano": 0.1,
    "urbano_edificios_altos": 0.01,
}



# ============================================================
# TABLA B.1 - PROBABILIDAD PTA (medidas contra tensión de paso/contacto)
# ============================================================

PTA = {
    "sin_medidas": 1,
    "avisos_de_peligro": 0.1,
    "aislamiento_electrico": 0.01,
    "equipotencializacion_terreno": 0.01,
    "restricciones_fisicas_o_armadura_bajada": 0,
}


# ============================================================
# TABLA B.2 - PROBABILIDAD PB (daño físico según SPCR)
# ============================================================

PB = {
    "sin_spcr": 1,
    "spcr_nivel_IV": 0.2,
    "spcr_nivel_III": 0.1,
    "spcr_nivel_II": 0.05,
    "spcr_nivel_I": 0.02,
    "captador_nivel_I_con_armadura_continua": 0.01,
    "techo_metalico_o_captacion_completa_con_armadura": 0.001,
}


# ============================================================
# TABLA B.3 - PROBABILIDAD PDPS (según NPR del sistema de DPS)
# ============================================================

PDPS = {
    "sin_dps_coordinado": 1,
    "npr_III_IV": 0.05,
    "npr_II": 0.02,
    "npr_I": 0.01,
}


# ============================================================
# TABLA B.6 - PROBABILIDAD PTU (medidas contra tensión de contacto por línea)
# ============================================================

PTU = {
    "sin_medidas": 1,
    "avisos": 0.1,
    "aislamiento_electrico": 0.01,
    "restricciones_fisicas": 0,
}


# ============================================================
# TABLA B.7 - PROBABILIDAD PEB (equipotencialidad según NPR del DPS)
# ============================================================

PEB = {
    "sin_dps": 1,
    "npr_III_IV": 0.05,
    "npr_II": 0.02,
    "npr_I": 0.01,
}


# ============================================================
# TABLA B.4 - FACTORES CLD Y CLI (blindaje, puesta a tierra, aislamiento)
# ============================================================

CLD_CLI = {
    "aerea_sin_blindaje": {"CLD": 1, "CLI": 1},
    "enterrada_sin_blindaje": {"CLD": 1, "CLI": 1},
    "potencia_multi_puesta_a_tierra_neutro": {"CLD": 1, "CLI": 0.2},
    "subterranea_blindada_sin_conectar_barra": {"CLD": 1, "CLI": 0.3},
    "aerea_apantallada_sin_conectar_barra": {"CLD": 1, "CLI": 0.1},
    "subterranea_apantallada_conectada_barra": {"CLD": 1, "CLI": 0},
    "aerea_apantallada_conectada_barra": {"CLD": 1, "CLI": 0},
    "cable_en_conducto_metalico_conectado_barra": {"CLD": 0, "CLI": 0},
    "sin_conexion_lineas_externas": {"CLD": 0, "CLI": 0},
    "interfaz_aislamiento_IEC62305_4": {"CLD": 0, "CLI": 0},
}


# ============================================================
# TABLA B.5 - FACTOR KS3 (características del cableado interno)
# ============================================================

KS3 = {
    "sin_blindar_sin_precauciones": 1,
    "sin_blindar_precauciones_bucles_grandes": 0.2,
    "sin_blindar_precauciones_bucles": 0.01,
    "con_blindaje_o_conducto_metalico": 0.0001,
}


# ============================================================
# TABLA B.9 - PROBABILIDAD PLI (según Uw del equipamiento)
# ============================================================

PLI = {
    "potencia": {1: 1, 1.5: 0.6, 2.5: 0.3, 4: 0.16, 6: 0.1},
    "telecomunicacion": {1: 1, 1.5: 0.5, 2.5: 0.2, 4: 0.08, 6: 0.04},
}



# ============================================================
# TABLA B.8 - PROBABILIDAD PLD (según Rs del blindaje y Uw del equipamiento)
# NOTA: la norma imprime "10 Ω/km < Rs ≤ 5 Ω/km" en la fila media, errata
# confirmada (rango imposible); se usa "1 Ω/km < Rs ≤ 5 Ω/km".
# ============================================================

PLD = {
    "sin_conectar_barra_equipotencial": {1: 1, 1.5: 1, 2.5: 1, 4: 1, 6: 1},
    "conectada_barra_equipotencial": {
        "5_a_20_ohm_km": {1: 1, 1.5: 1, 2.5: 0.95, 4: 0.9, 6: 0.8},
        "1_a_5_ohm_km": {1: 0.9, 1.5: 0.8, 2.5: 0.6, 4: 0.3, 6: 0.1},
        "hasta_1_ohm_km": {1: 0.6, 1.5: 0.4, 2.5: 0.2, 4: 0.04, 6: 0.02},
    },
}