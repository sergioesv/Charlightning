"""
Paso 36c: el adaptador pantalla -> modelo nuevo.

Toma los diccionarios de tests/datos_pantalla.py (los datos tal como salen de
la pantalla) y los pasa por el motor nuevo.

Los valores esperados del EDIFICIO_EJEMPLO quedaron congelados en el Paso 37d,
cuando se retiro el motor viejo. Antes de eso, esta prueba comparaba los dos
motores: coincidian en 6 de los 8 componentes, y las dos diferencias eran
erratas ya documentadas del calculo viejo:
  - R_A: el viejo usaba el P_A de la pantalla tal cual; la ec. (B.1) es
    P_A = P_TA x P_B. Con E=0,9 -> P_B=0,1, el viejo salia 10x alto (H13).
  - R_Z: el viejo usaba dN = N_I - N_L; la ec. (13) usa N_I, o sea un factor
    A_I/(A_I - A_L) = 4000/3960 = 1,0101... (H15).
La CASA_RURAL si daba EXACTAMENTE lo mismo en los dos motores, y sigue
comprobandose contra el 2,51e-5 publicado en el Anexo E.2 de la norma.
"""
from pytest import approx

from calculate_risk.norma import riesgos
from calculate_risk.norma.adaptador import caso_desde_pantalla
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO

# R1 del EDIFICIO_EJEMPLO, componente por componente (Paso 37d).
EDIFICIO_R1 = {
    "R_A": 1.1489380098815463e-09,
    "R_B": 2.2978760197630923e-07,
    "R_C": 1.1489380098815464e-05,
    "R_M": 0.008153981633974482,
    "R_U": 2.2000000000000005e-08,
    "R_V": 4.400000000000001e-06,
    "R_W": 0.00043999999999999996,
    "R_Z": 0.05,
}

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


def test_casa_rural_desde_la_pantalla_coincide_con_la_norma():
    r1 = _con_motor_nuevo(CASA_RURAL)

    assert r1["total"] == approx(2.51e-5, rel=0.01)  # Anexo E.2 de la norma
    assert r1["total"] == approx(2.5056181558313145e-05, rel=1e-9)


def test_edificio_ejemplo_componente_por_componente():
    r1 = _con_motor_nuevo(EDIFICIO_EJEMPLO)

    for componente, esperado in EDIFICIO_R1.items():
        assert r1[componente] == approx(esperado, rel=1e-9), componente
    assert r1["total"] == approx(sum(EDIFICIO_R1.values()), rel=1e-9)



def test_los_cuatro_tipos_de_riesgo_se_pueden_traducir():
    for tipo in (1, 2, 3, 4):
        r = _con_motor_nuevo(EDIFICIO_EJEMPLO, tipo=tipo)
        assert r["total"] > 0
        assert r["R_T"] > 0