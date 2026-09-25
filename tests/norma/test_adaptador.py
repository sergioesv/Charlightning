"""
Paso 36c: el adaptador pantalla -> modelo nuevo.

Toma los mismos diccionarios que ya usa tests/test_calculo.py (los datos tal
como salen de la pantalla vieja) y los pasa por el motor nuevo.

Dos comprobaciones:
  1. CASA_RURAL da EXACTAMENTE lo mismo en los dos motores, y ese valor es el
     2,51e-5 publicado en el Anexo E.2 de la norma.
  2. En el EDIFICIO_EJEMPLO los dos motores coinciden componente por
     componente, salvo en los dos sitios donde el calculo viejo tiene erratas
     ya documentadas (H13 y H15). Esta prueba fija esas dos diferencias para
     que no se nos olviden ni cambien sin darnos cuenta.
"""
from pytest import approx

from calculate_risk.norma import riesgos
from calculate_risk.norma.adaptador import caso_desde_pantalla
from calculate_risk.calculo import calcular_riesgo
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO


def _con_motor_nuevo(datos, tipo=1):
    c = caso_desde_pantalla(datos, tipo=tipo)
    return riesgos.evaluar(c["estructura"], c["lineas"], c["zonas"], c["N_G"], tipos=(tipo,))[tipo]


def test_estructura_del_caso_traducido():
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)

    assert c["N_G"] == CASA_RURAL["DDT"]
    assert c["estructura"].L == 15 and c["estructura"].W == 20
    assert len(c["zonas"]) == 1                      # la pantalla solo tiene una
    # pl=2 (potencia subterranea) + n_oh=1 (un servicio aereo) + n_ug=0
    assert [ln.nombre for ln in c["lineas"]] == ["potencia_subterranea", "servicio_aereo"]
    assert c["lineas"][0].C_I == 0.5 and c["lineas"][1].C_I == 1.0


def test_casa_rural_da_lo_mismo_en_los_dos_motores_y_coincide_con_la_norma():
    viejo = calcular_riesgo(CASA_RURAL)["R_1"]
    nuevo = _con_motor_nuevo(CASA_RURAL)["total"]

    assert nuevo == approx(viejo, rel=1e-9)
    assert nuevo == approx(2.51e-5, rel=0.01)        # Anexo E.2 de la norma


def test_edificio_ejemplo_coincide_salvo_las_dos_erratas_conocidas():
    viejo = calcular_riesgo(EDIFICIO_EJEMPLO)
    nuevo = _con_motor_nuevo(EDIFICIO_EJEMPLO)

    # Estos seis componentes son identicos en los dos motores.
    assert nuevo["R_B"] == approx(viejo["R_B1"], rel=1e-9)
    assert nuevo["R_C"] == approx(viejo["R_C1"], rel=1e-9)
    assert nuevo["R_M"] == approx(viejo["R_M1"], rel=1e-9)
    assert nuevo["R_U"] == approx(viejo["R_U1"], rel=1e-9)
    assert nuevo["R_V"] == approx(viejo["R_V1"], rel=1e-9)
    assert nuevo["R_W"] == approx(viejo["R_W1"], rel=1e-9)

    # H13: el calculo viejo usa P_A de la pantalla tal cual; la ec. (B.1) es
    # P_A = P_TA x P_B. Con E=0,9 -> P_B=0,1, asi que el viejo sale 10x alto.
    assert nuevo["R_A"] == approx(viejo["R_A1"] * 0.1, rel=1e-9)

    # H15: el calculo viejo usa dN = N_I - N_L; la ec. (13) usa N_I.
    # A_I/(A_I - A_L) = 4000/(4000 - 40) = 1,0101...
    assert nuevo["R_Z"] == approx(viejo["R_Z1"] * (4000 / 3960), rel=1e-9)


def test_los_cuatro_tipos_de_riesgo_se_pueden_traducir():
    for tipo in (1, 2, 3, 4):
        r = _con_motor_nuevo(EDIFICIO_EJEMPLO, tipo=tipo)
        assert r["total"] > 0
        assert r["R_T"] > 0