"""
Lo que salió de revisar la NTC 4552-2:2023 contra la IEC 62305-2:2010 (28-sep-2026).

Las ecuaciones y las tablas del motor coinciden con las de la IEC. Pero hay cosas que
las dos normas dicen y el programa todavía no hacía; cada una tiene aquí sus pruebas.
El detalle está en la memoria del proyecto (Revision_IEC_vs_NTC.md).
"""
from dataclasses import replace

import pytest

from calculate_risk.norma import casos, etiquetas, medidas, perdidas, riesgos, tablas
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


# ---------------------------------------------------------------------------
# 3. L_E también en R1 (ecuaciones C.5 y C.6): el daño alcanza a personas de afuera
# ---------------------------------------------------------------------------

def test_sin_personas_afuera_L_FT_es_L_F():
    assert perdidas.l_ft1(0.1, 1.0, 0) == 0.1


def test_L_E_se_suma_a_L_F():
    # L_E = L_FE x t_e / 8760 = 0,5 x 876 / 8760 = 0,05
    assert perdidas.l_ft1(0.1, 0.5, 876) == pytest.approx(0.15)


def test_si_no_se_conocen_la_norma_dice_que_valen_uno():
    # Nota 3 de C.3: L_FE x t_e / 8760 = 1, es decir L_FE = 1 y t_e = 8760.
    assert perdidas.l_ft1(0.1, 1.0, 8760) == pytest.approx(1.1)


def _evaluar(caso, zonas, tipo=1):
    return riesgos.evaluar(caso["estructura"], caso["lineas"], zonas, caso["N_G"],
                           tipos=(tipo,))[tipo]


def test_el_motor_lo_usa_en_el_dano_fisico_de_R1():
    caso = casos.cargar_caso("casos/casa_rural.json")
    antes = _evaluar(caso, caso["zonas"])
    despues = _evaluar(caso, [replace(z, t_e=8760) for z in caso["zonas"]])

    # L_F de la casa rural es 0,1: con L_E = 1, L_FT = 1,1, once veces más.
    assert despues["R_B"] == pytest.approx(antes["R_B"] * 11)
    assert despues["R_V"] == pytest.approx(antes["R_V"] * 11)
    assert despues["R_A"] == pytest.approx(antes["R_A"])       # R_A no es daño físico


def test_no_toca_R4():
    # En R4 el daño de afuera va por c_e (ec. C.14 y C.15), no por t_e.
    caso = casos.cargar_caso("casos/casa_rural.json")
    zonas = [replace(z, L_F=0.1, razones_l4_unitarias=True) for z in caso["zonas"]]
    antes = _evaluar(caso, zonas, tipo=4)
    despues = _evaluar(caso, [replace(z, t_e=8760) for z in zonas], tipo=4)

    assert despues["total"] == pytest.approx(antes["total"])


def test_t_e_se_guarda_y_se_vuelve_a_leer(tmp_path):
    guardados = casos.cargar_casos("casos/casa_rural.json")
    guardados[1]["zonas"] = [replace(z, t_e=500) for z in guardados[1]["zonas"]]

    ruta = casos.guardar_caso(tmp_path / "caso.json", guardados)

    assert casos.cargar_casos(ruta)[1]["zonas"][0].t_e == 500


def test_un_archivo_viejo_sin_t_e_no_suma_nada():
    assert all(z.t_e == 0 for z in casos.cargar_caso("casos/casa_rural.json")["zonas"])