from pytest import approx

from calculate_risk.calculo import calcular_riesgo

# Edificio de ejemplo: 20 x 10 x 6 m, zona suburbana, DDT = 10,
# SPCR con E = 0,9, DPS solo en la entrada de servicios,
# una línea eléctrica aérea, 1 servicio aéreo y 1 subterráneo apantallado.
EDIFICIO_EJEMPLO = {
    "L": 20, "W": 10, "H": 6, "H_P": 6,
    "DDT": 10, "C_d": 0.5, "C_e": 0.5, "D_m": 250,
    "r_f": 0.01, "Ks1": 1, "Ks2": 1, "Ks3": 1, "Ks4": 1, "P_A": 1,
    "pl": 1, "P_LD0": 1, "C_t0": 1, "n_oh": 1, "n_ug": 1,
    "P_LD1": 1, "P_LD2": 0.4,
    "h_1": 2, "L_f1": 0.02, "L_o1": 0.001,
    "L_f2": 0.01, "L_o2": 0.001, "L_f3": 0.1,
    "h4": 1, "L_f4": 0.2, "L_o4": 0.001, "L_t4": 0.01,
    "E": 0.9, "r": 0.5, "SP": 1,
    "H_c1": 6, "h_a1": 0, "D_L1": 500, "C_t1": 1,
    "h_a2": 0, "P_2": 500, "C_t2": 1, "R_a": 0.01, "L_t1": 1e-4,
}


def test_no_modifica_los_datos_de_entrada():
    datos = dict(EDIFICIO_EJEMPLO)
    calcular_riesgo(datos)
    assert datos == EDIFICIO_EJEMPLO


def test_edificio_ejemplo_resultados():
    # Valores de referencia generados por el propio programa (no por la norma),
    # sirven para detectar cambios accidentales; la validación contra la norma
    # está en tests/test_validacion_norma.py (Anexo E.2, casa rural).
    # Actualizados tras corregir A_m, N_M, y las áreas/frecuencias de líneas
    # (A_l, A_i, N_L, N_I), y tras combinar las probabilidades P_M, P_U y P_W
    # por producto en vez de mínimo, según IEC 62305-2:2010 / NTC 4552-2:2023.
    r = calcular_riesgo(EDIFICIO_EJEMPLO)
    assert r["A_d"] == approx(2297.876, rel=1e-6)
    assert r["N_D"] == approx(0.01148938, rel=1e-6)
    assert r["N_M"] == approx(8.153982, rel=1e-6)
    assert r["R_1"] == approx(5.217013e-2, rel=1e-6)
    assert r["R_2"] == approx(5.216663e-2, rel=1e-6)
    assert r["R_3"] == approx(1.157447e-5, rel=1e-6)
    assert r["R_4"] == approx(5.219197e-2, rel=1e-6)