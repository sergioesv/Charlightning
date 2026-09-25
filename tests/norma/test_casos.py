"""
Paso 33: prueba que un caso completo se pueda describir en JSON (carpeta
casos/) en vez de construirlo a mano en Python, y que dé el mismo resultado.

Usa casos/casa_rural.json -- el mismo caso (Anexo E.2, sin protección) que
ya está probado a mano en tests/norma/test_anexo_E2.py.
"""
import os

from pytest import approx

from calculate_risk.norma import riesgos
from calculate_risk.norma.casos import cargar_caso

RUTA_CASA_RURAL = os.path.join(
    os.path.dirname(__file__), "..", "..", "casos", "casa_rural.json"
)


def test_cargar_caso_arma_los_objetos_correctos():
    caso = cargar_caso(RUTA_CASA_RURAL)

    assert caso["N_G"] == 4.0
    assert caso["tipos"] == (1,)
    assert caso["estructura"].L == 15.0
    assert len(caso["lineas"]) == 2
    assert {ln.nombre for ln in caso["lineas"]} == {"potencia", "telecomunicacion"}
    assert len(caso["zonas"]) == 1
    assert len(caso["zonas"][0].sistemas_internos) == 2


def test_caso_rural_desde_json_da_el_mismo_resultado_que_a_mano():
    caso = cargar_caso(RUTA_CASA_RURAL)
    r1 = riesgos.evaluar(
        caso["estructura"], caso["lineas"], caso["zonas"], caso["N_G"], tipos=caso["tipos"]
    )[1]

    # Mismos valores de referencia que test_anexo_E2.test_casa_rural_sin_proteccion
    assert r1["R_B"] == approx(0.103e-5, rel=0.03)
    assert r1["R_V"] == approx(2.40e-5, rel=0.01)
    assert r1["total"] == approx(2.51e-5, rel=0.01)
    assert not r1["cumple"]