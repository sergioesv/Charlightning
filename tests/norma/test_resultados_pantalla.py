"""
Paso 37b: resultados_pantalla() entrega las mismas llaves que hoy produce
calculate_risk.calculo.calcular_riesgo, pero calculadas con el motor nuevo.

Es el contrato que necesita la pantalla (mostrar_resultados) y el informe PDF.
Cuando esta prueba esta en verde, se puede cambiar la llamada en
ventanas/principal_guiado.py y retirar el motor viejo (Pasos 37c y 37d).
"""
from pytest import approx

from calculate_risk.calculo import calcular_riesgo
from calculate_risk.norma.adaptador import resultados_pantalla
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO

# Lo que lee mostrar_resultados() en la pantalla.
LLAVES_PANTALLA = ["A_d"] + [f"R_{g}{t}" for g in ("d", "i") for t in (1, 2, 3, 4)] \
    + [f"R_{t}" for t in (1, 2, 3, 4)]

# Lo que lee ademas el informe PDF.
LLAVES_INFORME = [
    "A_m", "A_c1", "A_c2", "A_l2", "N_D", "N_M", "N_L1", "N_L2", "N_I2",
] + [f"R_{c}{t}" for c in ("A", "B", "C", "M", "U", "V", "W", "Z") for t in (1, 2, 3, 4)]


def test_estan_todas_las_llaves_que_usan_la_pantalla_y_el_informe():
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    faltan = [k for k in LLAVES_PANTALLA + LLAVES_INFORME if k not in r]
    assert faltan == []


def test_areas_y_frecuencias_identicas_al_motor_viejo():
    for datos in (CASA_RURAL, EDIFICIO_EJEMPLO):
        viejo = calcular_riesgo(datos)
        nuevo = resultados_pantalla(datos)

        for llave in ("A_d", "A_m", "N_D", "N_M", "A_c1", "A_c2", "A_l2",
                      "N_L1", "N_L2", "N_I2"):
            assert nuevo[llave] == approx(viejo[llave], rel=1e-9), llave


def test_casa_rural_da_los_mismos_riesgos_que_el_motor_viejo():
    viejo = calcular_riesgo(CASA_RURAL)
    nuevo = resultados_pantalla(CASA_RURAL)

    for tipo in (1, 2, 3, 4):
        assert nuevo[f"R_{tipo}"] == approx(viejo[f"R_{tipo}"], rel=1e-9)
    assert nuevo["R_1"] == approx(2.51e-5, rel=0.01)      # Anexo E.2 de la norma


def test_grupos_directo_e_indirecto_suman_el_total():
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    for tipo in (1, 2, 3, 4):
        assert r[f"R_d{tipo}"] + r[f"R_i{tipo}"] == approx(r[f"R_{tipo}"])


def test_trae_el_riesgo_tolerable_de_cada_tipo():
    # La pantalla hoy tiene R_T4 fijo en 1,00E-3; ahora el valor real viaja
    # en los resultados y se puede enganchar cuando se quiera.
    r = resultados_pantalla(EDIFICIO_EJEMPLO)

    assert r["R_T1"] == 1e-5
    assert r["R_T2"] == 1e-3
    assert r["R_T3"] == 1e-4
    assert r["R_T4"] == 1e-3