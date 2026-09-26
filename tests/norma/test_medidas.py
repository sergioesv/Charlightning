"""
Paso 38a: catalogo de medidas de proteccion y su aplicacion a un caso.

Lo importante: el catalogo no trae ningun numero propio, sale de tablas.py.
La comprobacion fuerte es que, escogiendo del catalogo "SPCR nivel IV" +
"DPS NPR III-IV", la casa rural del Anexo E.2 da 0,141e-5, que es justo la
solucion b) publicada por la norma.
"""
import pytest
from pytest import approx

from calculate_risk.norma import costos, medidas, riesgos, tablas
from calculate_risk.norma import costos, medidas, riesgos, tablas
from calculate_risk.norma.adaptador import caso_desde_pantalla
from tests.datos_pantalla import CASA_RURAL, EDIFICIO_EJEMPLO


def casa_rural():
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)
    return c["estructura"], c["lineas"], c["zonas"], c["N_G"]


def casa_rural():
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)
    return c["estructura"], c["lineas"], c["zonas"], c["N_G"]


def _r1(estructura, lineas, zonas, N_G):
    return riesgos.evaluar(estructura, lineas, zonas, N_G, tipos=(1,))[1]


def test_el_catalogo_sale_de_las_tablas_de_la_norma():
    cat = {m.nombre: m for m in medidas.catalogo()}

    # SPCR nivel IV -> P_B de la Tabla B.2
    spcr = cat["spcr:spcr_nivel_IV"]
    assert spcr.efectos == (medidas.Efecto("zona", "P_B", tablas.PB["spcr_nivel_IV"]),)

    # Un DPS coordinado baja P_DPS (Tabla B.3) y P_EB (Tabla B.7) a la vez
    dps = cat["dps:npr_I"]
    assert set(dps.efectos) == {
        medidas.Efecto("sistema", "P_DPS", tablas.PDPS["npr_I"]),
        medidas.Efecto("linea", "P_EB", tablas.PEB["npr_I"]),
    }

    # El blindaje de la linea toca C_LD y C_LI (Tabla B.4)
    blindaje = cat["blindaje_linea:aerea_apantallada_conectada_barra"]
    valores = tablas.CLD_CLI["aerea_apantallada_conectada_barra"]
    assert set(blindaje.efectos) == {
        medidas.Efecto("linea", "C_LD", valores["CLD"]),
        medidas.Efecto("linea", "C_LI", valores["CLI"]),
    }


def test_las_familias_son_alternativas_entre_si():
    fam = medidas.familias(medidas.catalogo())

    assert set(fam) == {"spcr", "dps", "tension_estructura", "tension_linea",
                        "incendio", "cableado_interno", "blindaje_linea"}
    # Dentro de una familia, todas las medidas tocan los mismos campos
    for nombre, lista in fam.items():
        campos = {tuple(sorted(e.campo for e in m.efectos)) for m in lista}
        assert len(campos) == 1, nombre


def test_aplicar_no_modifica_el_caso_original():
    estructura, lineas, zonas, N_G = casa_rural()
    spcr = next(m for m in medidas.catalogo() if m.nombre == "spcr:spcr_nivel_I")

    medidas.aplicar(estructura, lineas, zonas, [spcr])

    assert zonas[0].P_B == 1.0          # sigue sin SPCR
    assert lineas[0].P_EB == 1.0


def testcasa_rural_con_spcr_iv_y_dps_da_la_solucion_b_de_la_norma():
    estructura, lineas, zonas, N_G = casa_rural()
    assert not _r1(estructura, lineas, zonas, N_G)["cumple"]

    cat = {m.nombre: m for m in medidas.catalogo()}
    elegidas = [cat["spcr:spcr_nivel_IV"], cat["dps:npr_III_IV"]]
    e, l, z = medidas.aplicar(estructura, lineas, zonas, elegidas)

    r1 = _r1(e, l, z, N_G)
    assert r1["total"] == approx(0.141e-5, rel=0.01)   # Anexo E.2, solucion b)
    assert r1["cumple"]


def test_los_costos_se_pasan_aparte_porque_la_norma_no_los_trae():
    sin_costos = {m.nombre: m.costo for m in medidas.catalogo()}
    assert set(sin_costos.values()) == {0.0}

    con_costos = {m.nombre: m.costo
                  for m in medidas.catalogo(costos={"spcr:spcr_nivel_IV": 12_000_000})}
    assert con_costos["spcr:spcr_nivel_IV"] == 12_000_000
    assert con_costos["dps:npr_I"] == 0.0





# ---------------------------------------------------------------------------
# Paso 38b: barrido de combinaciones
# ---------------------------------------------------------------------------

def test_combinaciones_toma_a_lo_sumo_una_medida_por_familia():
    cat = medidas.catalogo()
    combos = list(medidas.combinaciones(cat))

    esperadas = 1
    for lista in medidas.familias(cat).values():
        esperadas *= len(lista) + 1        # +1 = no instalar nada de esa familia
    assert len(combos) == esperadas

    assert () in combos                    # la combinacion vacia esta
    for combo in combos:
        familias_usadas = [m.familia for m in combo]
        assert len(familias_usadas) == len(set(familias_usadas))


def test_el_barrido_encuentra_las_dos_soluciones_publicadas_de_la_norma():
    estructura, lineas, zonas, N_G = casa_rural()

    soluciones = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                                  solo_familias={"spcr", "dps"})
    por_nombre = {s.nombres: s for s in soluciones}

    # Solucion a) del Anexo E.2: DPS coordinados NPR IV -> 0,223e-5
    sola_dps = por_nombre[("dps:npr_III_IV",)]
    assert sola_dps.riesgo == approx(0.223e-5, rel=0.01)
    assert sola_dps.cumple

    # Solucion b): SPCR clase IV + esos mismos DPS -> 0,141e-5
    spcr_y_dps = por_nombre[("spcr:spcr_nivel_IV", "dps:npr_III_IV")]
    assert spcr_y_dps.riesgo == approx(0.141e-5, rel=0.01)
    assert spcr_y_dps.cumple


def test_el_barrido_descarta_lo_que_no_cumple():
    estructura, lineas, zonas, N_G = casa_rural()

    cumplen = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                               solo_familias={"spcr"})
    todas = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                             solo_familias={"spcr"}, solo_las_que_cumplen=False)

    assert all(s.cumple for s in cumplen)
    assert len(todas) > len(cumplen)
    # Sin ninguna medida la casa rural no cumple (2,51e-5 > 1e-5)
    sin_nada = next(s for s in todas if s.medidas == ())
    assert not sin_nada.cumple and sin_nada.riesgo == approx(2.51e-5, rel=0.01)


def test_las_soluciones_salen_ordenadas_por_costo():
    estructura, lineas, zonas, N_G = casa_rural()
    # Hay que ponerle precio a TODAS las medidas de las familias que se usen:
    # una medida sin precio cuenta como gratis y se iria de primeras.
    precios = {
        "dps:npr_III_IV": 1_000_000, "dps:npr_II": 2_000_000, "dps:npr_I": 4_000_000,
        "spcr:spcr_nivel_IV": 5_000_000, "spcr:spcr_nivel_III": 8_000_000,
        "spcr:spcr_nivel_II": 12_000_000, "spcr:spcr_nivel_I": 20_000_000,
        "spcr:captador_nivel_I_con_armadura_continua": 30_000_000,
        "spcr:techo_metalico_o_captacion_completa_con_armadura": 40_000_000,
    }

    soluciones = medidas.explorar(
        estructura, lineas, zonas, N_G, tipo=1,
        catalogo_medidas=medidas.catalogo(costos=precios),
        solo_familias={"spcr", "dps"},
    )

    costos = [s.costo for s in soluciones]
    assert costos == sorted(costos)
    # La mas barata que cumple es poner solo los DPS NPR IV (1 millon)
    assert soluciones[0].nombres == ("dps:npr_III_IV",)
    assert soluciones[0].costo == 1_000_000




# ---------------------------------------------------------------------------
# Paso 38c: costo-beneficio del Anexo D
# ---------------------------------------------------------------------------

ECONOMIA = {"c_t": 500_000_000, "i": 0.04, "a": 0.05, "m": 0.01}

PRECIOS = {
    "dps:npr_III_IV": 3_000_000, "dps:npr_II": 6_000_000, "dps:npr_I": 10_000_000,
    "spcr:spcr_nivel_IV": 25_000_000, "spcr:spcr_nivel_III": 35_000_000,
    "spcr:spcr_nivel_II": 50_000_000, "spcr:spcr_nivel_I": 80_000_000,
    "spcr:captador_nivel_I_con_armadura_continua": 120_000_000,
    "spcr:techo_metalico_o_captacion_completa_con_armadura": 200_000_000,
}


def _edificio_con_economia():
    """El edificio de prueba, con su caso de L4 aparte para el Anexo D."""
    estructura, lineas, zonas, N_G = edificio(1)
    est4, lin4, zon4, _ = edificio(4)
    economia = dict(ECONOMIA, caso_l4=(est4, lin4, zon4))
    return (estructura, lineas, zonas, N_G), economia


def _explorar_con_economia():
    (estructura, lineas, zonas, N_G), economia = _edificio_con_economia()
    return medidas.explorar(
        estructura, lineas, zonas, N_G, tipo=1,
        catalogo_medidas=medidas.catalogo(costos=PRECIOS),
        solo_familias={"spcr", "dps"},
        solo_las_que_cumplen=False,
        economia=economia,
    )


def test_el_anexo_d_exige_el_caso_armado_para_l4():
    # El caso de R1 no sirve para R4: la zona lleva otros L_F, L_O y otras
    # razones c/c_t. Si no se pasa caso_l4, hay que avisar en vez de dar 0.
    (estructura, lineas, zonas, N_G), _ = _edificio_con_economia()

    with pytest.raises(ValueError, match="caso_l4"):
        medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                         solo_familias={"spcr"},
                         economia={"c_t": 1, "i": 0, "a": 0, "m": 0})


def test_sin_medidas_el_ahorro_es_exactamente_cero():
    # Sin proteccion, las perdidas residuales son las mismas perdidas y no hay
    # costo de medidas: S_M = C_L - (0 + C_L) = 0.
    sin_nada = next(s for s in _explorar_con_economia() if s.medidas == ())

    assert sin_nada.C_PM == 0
    assert sin_nada.C_RL == approx(sin_nada.C_L)
    assert sin_nada.S_M == approx(0.0)


def test_el_ahorro_es_el_de_las_ecuaciones_del_anexo_d():
    for s in _explorar_con_economia():
        C_PM = costos.c_pm(s.costo, ECONOMIA["i"], ECONOMIA["a"], ECONOMIA["m"])
        assert s.C_PM == approx(C_PM)
        assert s.S_M == approx(costos.s_m(s.C_L, s.C_PM, s.C_RL))


def test_con_economia_ordena_por_ahorro_anual():
    soluciones = _explorar_con_economia()

    claves = [(not s.cumple, -s.S_M) for s in soluciones]
    assert claves == sorted(claves)