"""
Paso 56: de dónde viene el riesgo y qué medida baja cada parte.

Punto 4 de la Fase 6, el que pidió Sergio con «NO SE QUE VARIABLES INTERVIENEN
PARA MITIGAR TAL DAÑO». Dos piezas:

  - medidas.de_donde_viene(): reparte el riesgo entre sus ocho componentes y,
    para cada uno, prueba cada medida SOLA para ver cuáles lo bajan. No hay
    ninguna tabla de "qué medida toca qué componente": se mide sobre el caso.
  - ventanas/desglose.py: la ventana que lo enseña.

La casa rural del Anexo E.2 es el caso de referencia: R_V se lleva el 96 % del
riesgo, y por eso las dos soluciones que publica la norma actúan sobre R_V.
"""
import pytest
from pytest import approx

from calculate_risk.norma import casos, etiquetas, medidas, riesgos

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


@pytest.fixture
def aportes(caso):
    return medidas.de_donde_viene(caso["estructura"], caso["lineas"],
                                  caso["zonas"], caso["N_G"], tipo=1)


def _aporte(aportes, componente):
    return next(a for a in aportes if a.componente == componente)


# ---------------------------------------------------------------------------
# De qué está hecho el riesgo
# ---------------------------------------------------------------------------

def test_los_aportes_suman_el_riesgo_completo(caso, aportes):
    total = riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                            caso["N_G"], tipos=(1,))[1]["total"]

    assert sum(a.valor for a in aportes) == approx(total)


def test_en_la_casa_rural_manda_el_dano_fisico_por_la_linea(aportes):
    # Es lo que dice la memoria del proyecto: R_V es el 96 % del riesgo, y de
    # ahí que las dos soluciones publicadas actúen sobre la línea.
    assert aportes[0].componente == "R_V"
    assert aportes[0].porcentaje == approx(95.8, abs=0.5)


def test_van_de_mayor_a_menor(aportes):
    valores = [a.valor for a in aportes]

    assert valores == sorted(valores, reverse=True)


def test_los_componentes_en_cero_no_salen(aportes):
    # La casa rural no tiene R_C ni R_M ni R_W ni R_Z: no hay nada que bajar.
    assert all(a.valor > 0 for a in aportes)
    assert {a.componente for a in aportes} == {"R_A", "R_B", "R_U", "R_V"}


def test_cada_componente_dice_qué_parte_del_riesgo_es(aportes):
    assert sum(a.fraccion for a in aportes) == approx(1.0)


# ---------------------------------------------------------------------------
# Qué medidas bajan cada componente
# ---------------------------------------------------------------------------

def test_el_spcr_baja_el_dano_fisico_a_la_estructura(aportes):
    familias = {r.medida.familia for r in _aporte(aportes, "R_B").rebajas}

    assert "spcr" in familias
    # y no aparece ahí lo que no toca a R_B
    assert "tension_estructura" not in familias


def test_el_blindaje_de_la_linea_baja_lo_que_entra_por_la_linea(aportes):
    for componente in ("R_U", "R_V"):
        familias = {r.medida.familia for r in _aporte(aportes, componente).rebajas}

        assert "blindaje_linea" in familias, componente


def test_las_tensiones_de_la_estructura_solo_tocan_R_A(aportes):
    con_tension = {a.componente for a in aportes
                   for r in a.rebajas if r.medida.familia == "tension_estructura"}

    assert con_tension == {"R_A"}


def test_cada_rebaja_baja_de_verdad_ese_componente(aportes):
    for aporte in aportes:
        for rebaja in aporte.rebajas:
            assert rebaja.componente < aporte.valor, rebaja.medida.nombre


def test_las_rebajas_van_de_la_que_mas_baja_a_la_que_menos(aportes):
    for aporte in aportes:
        valores = [r.componente for r in aporte.rebajas]

        assert valores == sorted(valores)


def test_dice_cuando_una_sola_medida_ya_hace_cumplir(aportes):
    # En la casa rural, blindar la línea sola ya deja R1 por debajo de 1e-5:
    # es la primera de las dos soluciones que publica la norma.
    bastan = [r for r in _aporte(aportes, "R_V").rebajas if r.cumple]

    assert bastan
    assert all(r.total <= 1e-5 for r in bastan)


def test_una_estructura_sin_lineas_no_ofrece_medidas_de_linea(caso):
    sin_lineas = medidas.de_donde_viene(caso["estructura"], [], caso["zonas"],
                                        caso["N_G"], tipo=1)

    componentes = {a.componente for a in sin_lineas}
    assert componentes == {"R_A", "R_B"}
    assert all(r.medida.familia != "blindaje_linea"
               for a in sin_lineas for r in a.rebajas)


# ---------------------------------------------------------------------------
# Los textos: el usuario no puede ver "spcr:spcr_nivel_IV"
# ---------------------------------------------------------------------------

def test_todos_los_componentes_tienen_texto():
    assert set(etiquetas.COMPONENTES) == set(riesgos.COMPONENTES)


def test_toda_medida_del_catalogo_tiene_texto():
    for medida in medidas.catalogo():
        texto = etiquetas.texto_de_medida(medida.nombre)

        assert texto.strip()
        assert "_" not in texto, medida.nombre
        assert "Tabla" in texto, medida.nombre