"""
Lo que salió de revisar la NTC 4552-2:2023 contra la IEC 62305-2:2010 (28-sep-2026).

Las ecuaciones y las tablas del motor coinciden con las de la IEC. Pero hay cosas que
las dos normas dicen y el programa todavía no hacía; cada una tiene aquí sus pruebas.
El detalle está en la memoria del proyecto (Revision_IEC_vs_NTC.md).
"""
import pytest

from calculate_risk.norma import etiquetas, medidas, tablas

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