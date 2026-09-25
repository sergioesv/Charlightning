"""
Datos de entrada tal como los entrega la pantalla vieja (el diccionario VAR).

Viven aqui, y no dentro de un archivo de pruebas, porque los usan tanto las
pruebas del motor viejo como las del adaptador (Paso 36c) -- y el motor viejo
se retira en el Paso 37.
"""


# Edificio de ejemplo: 20 x 10 x 6 m, zona suburbana, DDT = 10,
# SPCR con E = 0,9, DPS solo en la entrada de servicios,
# una línea eléctrica aérea, 1 servicio aéreo y 1 subterráneo apantallado.
EDIFICIO_EJEMPLO = {
    "L": 20, "W": 10, "H": 6, "H_P": 6,
    "DDT": 10, "C_d": 0.5, "C_e": 0.5,
    "r_f": 0.01, "Ks1": 1, "Ks2": 1, "Ks3": 1, "Ks4": 1, "P_A": 1,
    "pl": 1, "P_LD0": 1, "C_t0": 1, "n_oh": 1, "n_ug": 1,
    "P_LD1": 1, "P_LD2": 0.4,
    "h_1": 2, "L_f1": 0.02, "L_o1": 0.001,
    "L_f2": 0.01, "L_o2": 0.001, "L_f3": 0.1,
    "h4": 1, "L_f4": 0.2, "L_o4": 0.001, "L_t4": 0.01,
    "E": 0.9, "r": 0.5, "SP": 1,
    "P_TU": 1, "C_LD": 1, "C_LI": 1, "P_LI": 1,
    "h_a1": 0, "C_t1": 1,
    "h_a2": 0, "C_t2": 1, "R_a": 0.01, "L_t1": 1e-4,
}


CASA_RURAL = {
    "L": 15, "W": 20, "H": 6, "H_P": 6,
    "DDT": 4, "C_d": 1, "C_e": 1,
    "r_f": 1e-3,
    "Ks1": 1, "Ks2": 1, "Ks3": 0.2, "Ks4": 1,
    "P_A": 1,

    # Línea eléctrica: subterránea
    "pl": 2,
    "P_LD0": 1,
    "C_t0": 1,

    # Una línea adicional aérea de telecomunicaciones
    "n_oh": 1,
    "n_ug": 0,
    "P_LD1": 1,
    "P_LD2": 1,

    # Pérdidas L1
    "h_1": 1,
    "L_f1": 0.1,
    "L_o1": 0,

    # R2-R4 no son relevantes para esta prueba
    "L_f2": 0,
    "L_o2": 0,
    "L_f3": 0,

    "h4": 1,
    "L_f4": 0,
    "L_o4": 0,
    "L_t4": 0,

    # Sin SPCR
    "E": 0,
    "r": 1,

    # Sin DPS
    "SP": 0,

    # Protección de líneas
    "P_TU": 1,
    "C_LD": 1,
    "C_LI": 1,
    "P_LI": 0.3,

    # Casa rural: suelo linóleo, rt = 1e-5
    "R_a": 1e-5,
    "L_t1": 1e-2,

    "h_a1": 0,
    "C_t1": 1,
    "h_a2": 0,
    "C_t2": 1,
}