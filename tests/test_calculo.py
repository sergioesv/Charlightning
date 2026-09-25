from pytest import approx

from calculate_risk.calculo import calcular_riesgo
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO



def test_casa_rural_sin_proteccion():
    r = calcular_riesgo(CASA_RURAL)

    # Norma: R1 ≈ 2,51 × 10^-5
    assert r["R_1"] == approx(2.51e-5, rel=0.01)


def test_casa_rural_SPCR_IV_DPS_entrada():
    datos = dict(CASA_RURAL)
    datos["E"] = 0.8
    datos["SP"] = 1

    r = calcular_riesgo(datos)

    # Norma: R1 ≈ 0,141 × 10^-5 = 1,41 × 10^-6
    assert r["R_1"] == approx(1.41e-6, rel=0.01)


def test_P_TU_no_cambia_RV():
    datos = dict(CASA_RURAL)

    r_base = calcular_riesgo(datos)

    datos["P_TU"] = 0
    r_sin_PTU = calcular_riesgo(datos)

    # PV no depende de PTU.
    assert r_sin_PTU["R_V1"] == approx(r_base["R_V1"])

    # PU sí depende de PTU.
    assert r_sin_PTU["R_U1"] < r_base["R_U1"]


def test_no_modifica_los_datos_de_entrada():
    datos = dict(EDIFICIO_EJEMPLO)
    calcular_riesgo(datos)
    assert datos == EDIFICIO_EJEMPLO


def test_edificio_ejemplo_resultados():
    # Valores de referencia generados por el propio programa (no por la norma),
    # sirven para detectar cambios accidentales; la validación contra la norma
    # está en tests/test_validacion_norma.py (Anexo E.2, casa rural).
    # Actualizados tras corregir A_m, N_M, y las áreas/frecuencias de líneas
    # (A_l, A_i, N_L, N_I), tras combinar las probabilidades P_M, P_U y P_W
    # por producto en vez de mínimo, y tras calcular P_Z con su propia
    # fórmula (P_DPS * P_LI * C_LI) en vez de reutilizar P_W, según
    # IEC 62305-2:2010 / NTC 4552-2:2023.
    r = calcular_riesgo(EDIFICIO_EJEMPLO)
    assert r["A_d"] == approx(2297.876, rel=1e-6)
    assert r["N_D"] == approx(0.01148938, rel=1e-6)
    assert r["N_M"] == approx(8.153982, rel=1e-6)
    assert r["R_1"] == approx(5.811013e-2, rel=1e-6)
    assert r["R_2"] == approx(5.810663e-2, rel=1e-6)
    assert r["R_3"] == approx(1.157447e-5, rel=1e-6)
    assert r["R_4"] == approx(5.813197e-2, rel=1e-6)

def test_P_TU_C_LD_C_LI_influyen_en_el_resultado():
    # Si P_TU, C_LD y C_LI bajan (más medidas de protección en la línea),
    # R_1 debe bajar: R_U1, R_W1 y R_Z1 dependen de ellos.
    datos_protegidos = dict(EDIFICIO_EJEMPLO)
    datos_protegidos["P_TU"] = 0.01
    datos_protegidos["C_LD"] = 0
    datos_protegidos["C_LI"] = 0
    r_base = calcular_riesgo(EDIFICIO_EJEMPLO)
    r_protegido = calcular_riesgo(datos_protegidos)
    assert r_protegido["R_1"] < r_base["R_1"]