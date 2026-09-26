"""
Paso 47b: el editor del caso. Aquí cae H19.

La pantalla vieja tenía UNA zona horneada en los nombres de sus widgets, así
que no podía plantear los ejemplos E.3 (cinco zonas) y E.4 (cuatro) que su
propio motor reproduce. El editor tiene una lista de zonas y otra de líneas.

Las dos pruebas que cierran el paso:

  - partir la zona de la casa rural en dos tiene que dar EXACTAMENTE el
    mismo riesgo, porque las pérdidas son proporcionales a n_z/n_t y R es la
    suma sobre zonas (numeral 4.4);
  - un caso de dos zonas armado en el editor tiene que dar lo mismo que el
    mismo caso armado a mano en Python.
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

from calculate_risk.norma import casos, riesgos                     # noqa: E402
from ventanas import campos, editor_caso                            # noqa: E402

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


def _evaluar(caso_leido):
    return riesgos.evaluar(caso_leido["estructura"], caso_leido["lineas"],
                           caso_leido["zonas"], caso_leido["N_G"], tipos=(1,))[1]


# ---------------------------------------------------------------------------
# Lo básico
# ---------------------------------------------------------------------------

def test_el_editor_tiene_estructura_zonas_y_lineas(raiz):
    e = editor_caso.EditorCaso(raiz)

    assert [e.cuaderno.tab(i, "text") for i in range(3)] == [
        "Estructura", "Zonas", "Líneas"]


def test_abrir_la_casa_rural_deja_una_zona_y_dos_lineas(editor):
    assert len(editor.zonas.formularios) == 1
    assert editor.lineas.nombres() == ["potencia", "telecomunicacion"]
    assert editor.N_G.valor() == 4.0


def test_la_casa_rural_desde_el_editor_da_el_riesgo_de_la_norma(editor):
    # Anexo E.2: R1 = 2,506e-5. Ahora sale del caso completo, no de una pieza.
    leido = editor.casos_por_tipo(tipos=(1,))[1]

    assert _evaluar(leido)["total"] == approx(2.506e-5, rel=0.01)


def test_lo_que_se_abre_es_lo_que_se_lee(editor, caso):
    leido = editor.casos_por_tipo(tipos=(1,))[1]

    assert leido["estructura"] == caso["estructura"]
    assert leido["lineas"] == caso["lineas"]
    assert leido["zonas"] == caso["zonas"]
    assert leido["N_G"] == caso["N_G"]


# ---------------------------------------------------------------------------
# H19: varias zonas
# ---------------------------------------------------------------------------

def test_partir_la_zona_en_dos_no_cambia_el_riesgo(editor, caso):
    # Las pérdidas llevan el factor n_z/n_t (ec. C.2 y siguientes) y R suma
    # sobre zonas: una zona de 5 personas equivale a dos de 2 y 3.
    una = _evaluar(editor.casos_por_tipo(tipos=(1,))[1])["total"]

    primera = editor.zonas.formularios[0]
    primera.comun.campos["nombre"].poner("mitad_A")
    primera.comun.campos["n_z"].poner(2)
    original = caso["zonas"][0]
    segunda = editor.zonas.anadir({1: original})
    segunda.comun.campos["nombre"].poner("mitad_B")
    segunda.comun.campos["n_z"].poner(3)

    partida = _evaluar(editor.casos_por_tipo(tipos=(1,))[1])

    assert len(partida["zonas"]) == 2
    assert partida["total"] == approx(una, rel=1e-9)


def test_dos_zonas_desde_el_editor_dan_lo_mismo_que_a_mano(editor, caso):
    original = caso["zonas"][0]
    primera = editor.zonas.formularios[0]
    primera.comun.campos["n_z"].poner(2)
    segunda = editor.zonas.anadir({1: original})
    segunda.comun.campos["nombre"].poner("otra")
    segunda.comun.campos["n_z"].poner(3)

    del_editor = _evaluar(editor.casos_por_tipo(tipos=(1,))[1])

    from dataclasses import replace
    a_mano = riesgos.evaluar(
        caso["estructura"], caso["lineas"],
        [replace(original, n_z=2), replace(original, nombre="otra", n_z=3)],
        caso["N_G"], tipos=(1,))[1]

    assert del_editor["total"] == approx(a_mano["total"], rel=1e-12)


def test_no_se_puede_quedar_sin_zonas(editor):
    editor.zonas.lista.selection_clear(0, "end")
    editor.zonas.lista.selection_set(0)

    with pytest.raises(campos.DatoFaltante, match="al menos 1 zona"):
        editor.zonas.quitar()


def test_una_estructura_sin_lineas_si_se_puede(editor):
    editor.lineas.poner([])

    leido = editor.casos_por_tipo(tipos=(1,))[1]
    r = _evaluar(leido)

    assert leido["lineas"] == []
    assert r["R_V"] == 0 and r["R_B"] > 0        # solo queda lo de la estructura


# ---------------------------------------------------------------------------
# Ida y vuelta de los cuatro riesgos
# ---------------------------------------------------------------------------

def test_los_cuatro_casos_van_y_vuelven(editor, caso):
    # R1 ya viene del JSON; R2 y R3 se dejan en "no aplica" y R4 solo
    # necesita su pérdida por daño físico, que no es opcional en la C.12.
    for formulario in editor.zonas.formularios:
        formulario.pestanas[4].campos["L_F"].poner_llave("otros")
    antes = editor.casos_por_tipo()

    editor.poner(antes)

    assert editor.casos_por_tipo() == antes


# ---------------------------------------------------------------------------
# Lo que falta se dice entero
# ---------------------------------------------------------------------------

def test_un_editor_vacio_dice_todo_lo_que_falta(raiz):
    vacio = editor_caso.EditorCaso(raiz)

    with pytest.raises(campos.DatoFaltante) as fallo:
        vacio.casos_por_tipo(tipos=(1,))

    mensaje = str(fallo.value)
    assert "N_g:" in mensaje or "N_G" in mensaje
    assert "Estructura:" in mensaje
    assert "Zonas:" in mensaje
    assert "al menos 1 zona" in mensaje


def test_lo_que_falta_dice_en_que_zona_es(editor):
    editor.zonas.anadir()      # una zona nueva, vacía

    with pytest.raises(campos.DatoFaltante) as fallo:
        editor.casos_por_tipo(tipos=(1,))

    mensaje = str(fallo.value)
    assert "Zona 2" in mensaje
    assert "Nombre de la zona" in mensaje