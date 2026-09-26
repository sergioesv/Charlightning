"""
Paso 49: el panel de resultados.

Lo que la pantalla vieja no podía enseñar es el desglose POR ZONA, porque
solo manejaba una. Aquí cada riesgo trae colgando sus zonas con lo que
aporta cada una.

También se comprueba lo del color: cumple y no cumple van en azul y naranja,
los mismos de graficos.py, y nunca solo por color — el veredicto va escrito.
"""
import pytest
from pytest import approx

tkinter = pytest.importorskip("tkinter")


def _hay_pantalla() -> bool:
    try:
        raiz = tkinter.Tk()
    except Exception:
        return False
    raiz.destroy()
    return True


pytestmark = pytest.mark.skipif(not _hay_pantalla(),
                                reason="no hay pantalla gráfica (ni Xvfb)")

from calculate_risk.norma import casos, tablas                      # noqa: E402
from ventanas import editor_caso, resultados                        # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


@pytest.fixture
def editor(raiz, caso):
    e = editor_caso.EditorCaso(raiz)
    e.poner_caso(caso, tipo=1)
    return e


@pytest.fixture
def panel(raiz):
    return resultados.PanelResultados(raiz)


# ---------------------------------------------------------------------------
# Formato de los números
# ---------------------------------------------------------------------------

def test_los_riesgos_salen_con_coma_decimal():
    assert resultados.numero(2.506e-5) == "2,506e-05"
    assert resultados.numero(0) == "0"


def test_la_participacion_sale_en_porcentaje():
    assert resultados.porcentaje(1, 4) == "25,0 %"
    assert resultados.porcentaje(1, 0) == "—"


# ---------------------------------------------------------------------------
# El editor ya sabe evaluar
# ---------------------------------------------------------------------------

def test_el_editor_evalua_el_riesgo_de_la_norma(editor):
    # Anexo E.2: R1 = 2,506e-5, y no cumple contra R_T = 1e-5.
    r = editor.evaluar(tipos=(1,))[1]

    assert r["total"] == approx(2.506e-5, rel=0.01)
    assert r["R_T"] == tablas.RT["L1"]
    assert r["cumple"] is False


# ---------------------------------------------------------------------------
# Lo que se ve en el panel
# ---------------------------------------------------------------------------

def test_cada_riesgo_trae_colgando_sus_zonas(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))

    filas = panel.filas()
    assert filas[0][0] == "riesgo"
    assert "R1" in filas[0][1]
    assert filas[1][0] == "zona"
    assert filas[1][1] == "Z2_interior"


def test_el_veredicto_va_escrito_no_solo_en_color(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))

    fila = panel.filas()[0]

    assert fila[2] == "2,506e-05"
    assert fila[3] == "1,000e-05"
    assert fila[4] == "No cumple"


def test_una_sola_zona_aporta_el_cien_por_ciento(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))

    assert panel.filas()[1][4] == "100,0 %"


def test_con_dos_zonas_se_ve_lo_que_aporta_cada_una(panel, editor, caso):
    original = caso["zonas"][0]
    editor.zonas.formularios[0].comun.campos["nombre"].poner("A")
    editor.zonas.formularios[0].comun.campos["n_z"].poner(1)
    segunda = editor.zonas.anadir({1: original})
    segunda.comun.campos["nombre"].poner("B")
    segunda.comun.campos["n_z"].poner(4)

    panel.mostrar(editor.evaluar(tipos=(1,)))

    zonas = [f for f in panel.filas() if f[0] == "zona"]
    assert [z[1] for z in zonas] == ["A", "B"]
    # R_B y R_V llevan n_z/n_t: la de 4 personas aporta más que la de 1
    assert zonas[0][4] != zonas[1][4]


def test_los_cuatro_riesgos_caben_en_la_tabla(panel, editor):
    for formulario in editor.zonas.formularios:
        formulario.pestanas[4].campos["L_F"].poner_llave("otros")

    panel.mostrar(editor.evaluar())

    riesgos_vistos = [f[1] for f in panel.filas() if f[0] == "riesgo"]
    assert len(riesgos_vistos) == 4
    assert riesgos_vistos[0].startswith("R1")
    assert riesgos_vistos[3].startswith("R4")


# ---------------------------------------------------------------------------
# El aviso y el botón de medidas
# ---------------------------------------------------------------------------

def test_si_no_cumple_se_habilita_el_boton_de_medidas(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))

    assert "No cumple: R1" in panel.aviso.cget("text")
    assert str(panel.boton_medidas.cget("state")) == "normal"


def test_si_cumple_no_hace_falta_buscar_medidas(panel, editor):
    # R3 de la casa rural es 0: no hay patrimonio cultural que perder.
    panel.mostrar(editor.evaluar(tipos=(3,)))

    assert "por debajo del tolerable" in panel.aviso.cget("text")
    assert str(panel.boton_medidas.cget("state")) == "disabled"


def test_volver_a_mostrar_no_acumula_filas(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))
    antes = len(panel.filas())

    panel.mostrar(editor.evaluar(tipos=(1,)))

    assert len(panel.filas()) == antes


def test_limpiar_deja_el_panel_en_blanco(panel, editor):
    panel.mostrar(editor.evaluar(tipos=(1,)))

    panel.limpiar()

    assert panel.filas() == []
    assert panel.aviso.cget("text") == ""


# ---------------------------------------------------------------------------
# El color no es lo único que lleva el significado
# ---------------------------------------------------------------------------

def test_los_colores_son_los_mismos_de_los_graficos():
    # Si alguien cambia la paleta en un sitio y no en el otro, esto falla.
    from calculate_risk.norma import graficos

    assert resultados.AZUL == graficos.AZUL
    assert resultados.NARANJA == graficos.NARANJA


def test_no_se_usan_verde_ni_rojo():
    # Verde y rojo es el par que no distingue el daltonismo más común.
    for color in (resultados.AZUL, resultados.NARANJA):
        rojo, verde, azul = (int(color[i:i + 2], 16) for i in (1, 3, 5))

        assert not (verde > rojo and verde > azul + 40), color   # no es verde
        assert not (rojo > 180 and verde < 80 and azul < 80), color   # no es rojo


def test_el_tolerable_sale_de_la_tabla_4():
    for tipo in (1, 2, 3, 4):
        assert resultados.tolerable(tipo) == tablas.RT[f"L{tipo}"]