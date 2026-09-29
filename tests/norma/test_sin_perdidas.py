"""
Bug 4 del 28-sep: un riesgo marcado sin ninguna pérdida cargada daba 0 y «Cumple».

Los cuatro ejemplos del Anexo E solo traen R1. Si se marcaba R2, R3 o R4, las
zonas no tenían pérdidas de ese riesgo y el motor devolvía 0,0: el mismo cero en
silencio que daba la casilla de N_G vacía en el programa viejo. El motor ahora
sabe reconocerlo (riesgos.sin_perdidas) y la pantalla lo dice en vez de calcular
(las pruebas de la pantalla están en test_principal_norma.py).
"""
import pytest

from calculate_risk.norma import riesgos
from calculate_risk.norma.modelo import Zona


@pytest.mark.parametrize("tipo", [1, 2, 3, 4])
def test_sin_ninguna_perdida_el_riesgo_esta_vacio(tipo):
    assert riesgos.sin_perdidas([Zona("Z1"), Zona("Z2")], tipo)


@pytest.mark.parametrize("tipo, campo", [
    (1, "L_T"), (1, "L_F"), (1, "L_O"),
    (2, "L_F"), (2, "L_O"),
    (3, "L_F"),
    (4, "L_T"), (4, "L_F"), (4, "L_O"),
])
def test_basta_una_perdida_en_una_sola_zona(tipo, campo):
    # Una zona exterior sin pérdidas es una respuesta válida; lo que no vale es
    # que no haya NADA que perder en toda la estructura.
    zonas = [Zona("Z1"), Zona("Z2", **{campo: 0.1})]

    assert not riesgos.sin_perdidas(zonas, tipo)


def test_una_perdida_que_no_es_de_ese_riesgo_no_cuenta():
    # R3 (patrimonio) solo tiene daño físico: un L_O cargado no lo llena.
    assert riesgos.sin_perdidas([Zona("Z1", L_O=0.01, c_z=5)], 3)