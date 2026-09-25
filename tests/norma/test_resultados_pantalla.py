"""
resultados_pantalla() entrega las llaves que leen la pantalla
(mostrar_resultados) y el informe PDF, calculadas con el motor nuevo.

Los valores de las areas y frecuencias quedaron congelados en el Paso 37d, al
retirar el motor viejo; hasta ese momento se comprobaban comparandolos contra
calculate_risk.calculo.calcular_riesgo, y salian identicos en los dos casos.
"""
from pytest import approx

from calculate_risk.norma.adaptador import resultados_pantalla
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO

# Lo que lee mostrar_resultados() en la pantalla.
LLAVES_PANTALLA = ["A_d"] + [f"R_{g}{t}" for g in ("d", "i") for t in (1, 2, 3, 4)] \
    + [f"R_{t}" for t in (1, 2, 3, 4)]

# Lo que lee ademas el informe PDF.
LLAVES_INFORME = [
    "A_m", "A_c1", "A_c2", "A_l2", "N_D", "N_M", "N_L1", "N_L2", "N_I2",
] + [f"R_{c}{t}" for c in ("A", "B", "C", "M", "U", "V", "W", "Z") for t in (1, 2, 3, 4)]

# Areas y frecuencias del EDIFICIO_EJEMPLO (20 x 10 x 6 m, H_P=6, DDT=10).
INTERMEDIOS_EDIFICIO = {
    "A_d": 2297.8760197630927,
    "A_m": 815398.1633974483,
    "N_D": 0.011489380098815463,
    "N_M": 8.153981633974482,
    "A_c1": 40000.0,
    "A_c2": 40000.0,
    "A_l1": 4000000.0,
    "A_l2": 4000000.0,
    "N_L1": 0.2,
    "N_L2": 0.1,
    "N_I1": 20.0,
    "N_I2": 10.0,
}


def test_estan_todas_las_llaves_que_usan_la_pantalla_y_el_informe():
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    faltan = [k for k in LLAVES_PANTALLA + LLAVES_INFORME if k not in r]
    assert faltan == []


def test_areas_y_frecuencias_del_edificio_ejemplo():
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    for llave, esperado in INTERMEDIOS_EDIFICIO.items():
        assert r[llave] == approx(esperado, rel=1e-9), llave


def test_casa_rural_coincide_con_la_norma():
    r = resultados_pantalla(CASA_RURAL)

    assert r["R_1"] == approx(2.51e-5, rel=0.01)      # Anexo E.2 de la norma
    # En este caso L_f2, L_f3, L_f4, L_o* y L_t4 valen 0, asi que R2-R4 son 0.
    assert r["R_2"] == 0 and r["R_3"] == 0 and r["R_4"] == 0


def test_grupos_directo_e_indirecto_suman_el_total():
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    for tipo in (1, 2, 3, 4):
        assert r[f"R_d{tipo}"] + r[f"R_i{tipo}"] == approx(r[f"R_{tipo}"])


def test_trae_el_riesgo_tolerable_de_cada_tipo():
    # Estos cuatro valores son los que la pantalla muestra en la columna del
    # riesgo tolerable (Paso 41c). 
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    assert r["R_T1"] == 1e-5
    assert r["R_T2"] == 1e-3
    assert r["R_T3"] == 1e-4
    assert r["R_T4"] == 1e-3