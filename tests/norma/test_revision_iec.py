"""
Lo que salió de revisar la NTC 4552-2:2023 contra la IEC 62305-2:2010 (28-sep-2026).

Las ecuaciones y las tablas del motor coinciden con las de la IEC. Pero hay cosas que
las dos normas dicen y el programa todavía no hacía; cada una tiene aquí sus pruebas.
El detalle está en la memoria del proyecto (Revision_IEC_vs_NTC.md).
"""
from dataclasses import replace

import pytest

from calculate_risk.norma import casos, etiquetas, medidas, riesgos, tablas
from calculate_risk.norma.modelo import SistemaInterno, Zona

MEJORES = ("mejor_que_npr_I_1_5x", "mejor_que_npr_I_2x", "mejor_que_npr_I_3x")


# ---------------------------------------------------------------------------
# 1. La fila «mejores que NPR I» de las Tablas B.3 (P_DPS) y B.7 (P_EB)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tabla", [tablas.PDPS, tablas.PEB])
def test_son_los_tres_valores_del_hospital(tabla):
    # E.4.5: DPS 1,5, 3 y 2 veces mejores que NPR I dan 0,005, 0,001 y 0,002.
    assert [tabla[llave] for llave in MEJORES] == [0.005, 0.002, 0.001]


@pytest.mark.parametrize("tabla", [tablas.PDPS, tablas.PEB])
def test_caben_en_el_rango_que_da_la_nota(tabla):
    # La nota de la tabla dice «0,005 - 0,001», y todos quedan por debajo del NPR I.
    for llave in MEJORES:
        assert 0.001 <= tabla[llave] <= 0.005 < tabla["npr_I"]


def test_la_pantalla_las_ofrece():
    opciones = dict(etiquetas.opciones("PDPS"))
    assert opciones["DPS 2 veces mejor que NPR I (Nota 2)"] == 0.002
    assert dict(etiquetas.opciones("PEB"))["DPS 3 veces mejor que NPR I (Nota 3)"] == 0.001


def test_el_buscador_de_medidas_no_las_propone_solas():
    # Exigen justificar las características del DPS: se declaran, no se sugieren.
    nombres = [m.nombre for m in medidas.familias(medidas.catalogo())["dps"]]
    assert nombres == ["dps:npr_III_IV", "dps:npr_II", "dps:npr_I"]


# ---------------------------------------------------------------------------
# 2. Medidas que la norma solo da por efectivas con SPCR (Nota 1 del numeral B.2 y
#    Nota 1 de la Tabla B.3). Decisión de Sergio (29-sep): solo se avisa.
# ---------------------------------------------------------------------------

AVISOS = tablas.PTA["avisos_de_peligro"]
DPS_I = tablas.PDPS["npr_I"]


def test_medidas_contra_tension_de_paso_sin_spcr_se_avisan():
    avisos = riesgos.avisos_sin_spcr([Zona("Z1", P_TA=AVISOS)])

    assert len(avisos) == 1
    assert "Zona Z1" in avisos[0] and "Nota 1 del numeral B.2" in avisos[0]


def test_un_dps_coordinado_sin_spcr_se_avisa():
    zona = Zona("Z1", sistemas_internos=[SistemaInterno("potencia", P_DPS=DPS_I)])

    assert "Nota 1 de la Tabla B.3" in riesgos.avisos_sin_spcr([zona])[0]


def test_con_spcr_no_hay_nada_que_avisar():
    zona = Zona("Z1", P_B=tablas.PB["spcr_nivel_IV"], P_TA=AVISOS,
                sistemas_internos=[SistemaInterno("potencia", P_DPS=DPS_I)])

    assert riesgos.avisos_sin_spcr([zona]) == []


def test_la_cerca_del_ejemplo_E3_no_se_avisa():
    # P_TA = 0 es una restricción física o la armadura usada como bajante; el ejemplo
    # E.3 pone una cerca en el jardín sin SPCR.
    cerca = tablas.PTA["restricciones_fisicas_o_armadura_bajada"]

    assert riesgos.avisos_sin_spcr([Zona("Z2", P_TA=cerca)]) == []


def test_la_casa_rural_no_tiene_avisos():
    assert riesgos.avisos_sin_spcr(casos.cargar_caso("casos/casa_rural.json")["zonas"]) == []


def test_solo_se_avisa_el_calculo_no_cambia():
    caso = casos.cargar_caso("casos/casa_rural.json")
    zonas = [replace(z, P_TA=AVISOS) for z in caso["zonas"]]

    r = riesgos.evaluar(caso["estructura"], caso["lineas"], zonas, caso["N_G"])[1]

    detalle = next(iter(r["zonas"].values()))["_detalle"]
    assert detalle["P_A"] == AVISOS          # P_A = P_TA x P_B, con P_TA reducido igual