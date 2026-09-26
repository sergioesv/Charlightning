"""
Paso 51e: el diálogo que calcula N_G desde latitud y longitud.

Es lo único que hacía la pantalla vieja y la nueva no: el botón «Calcular
ddt». Se rehace sobre norma/densidad.py (Paso 35), así que de paso se lleva
los dos defectos de la ventana vieja: lat = 0 tomada como casilla vacía y la
coma decimal rechazada. Las dos cosas están probadas abajo.
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

from ventanas import dialogo_densidad, editor_caso                   # noqa: E402

N_G_MEDELLIN = 2.3435


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def recibido():
    return []


@pytest.fixture
def dialogo(raiz, recibido):
    return dialogo_densidad.DialogoDensidad(raiz, recibido.append)


# ---------------------------------------------------------------------------
# El número es el del Paso 35
# ---------------------------------------------------------------------------

def test_medellin_da_el_mismo_n_g_que_el_motor(dialogo):
    # Arranca en Medellín, como la ventana vieja.
    assert dialogo.calcular() == approx(N_G_MEDELLIN, rel=1e-3)
    texto = dialogo.aviso.cget("text")
    assert "2,34" in texto and "2.34" not in texto     # coma, no punto


def test_lat_lon_cero_se_puede_calcular(dialogo):
    # El bug de la ventana vieja: `if float(lat):` es Falso con lat = 0, así
    # que el ecuador y el meridiano de Greenwich no se calculaban nunca.
    dialogo.campos["lat"].poner(0)
    dialogo.campos["lon"].poner(0)

    assert dialogo.calcular() == approx(0.4654, rel=1e-3)


def test_la_coma_decimal_tambien_sirve(dialogo):
    # La ventana vieja contestaba "recuerda que debes ingresar números,
    # separarlo con punto, no por coma".
    dialogo.campos["lat"].poner("6,251")
    dialogo.campos["lon"].poner("-75,563")

    assert dialogo.calcular() == approx(N_G_MEDELLIN, rel=1e-3)


# ---------------------------------------------------------------------------
# Nada entra al caso sin que el usuario lo acepte
# ---------------------------------------------------------------------------

def test_hasta_no_calcular_no_se_puede_usar(dialogo, recibido):
    assert str(dialogo.boton_usar.cget("state")) == "disabled"
    assert dialogo.usar() is None
    assert recibido == []


def test_usar_entrega_el_valor_y_cierra(dialogo, recibido):
    dialogo.calcular()

    assert dialogo.usar() == approx(N_G_MEDELLIN, rel=1e-3)
    assert recibido[0] == approx(N_G_MEDELLIN, rel=1e-3)


def test_una_latitud_imposible_avisa_y_no_calcula(dialogo):
    dialogo.campos["lat"].poner(100)

    assert dialogo.calcular() is None
    assert "Latitud" in dialogo.aviso.cget("text")
    assert dialogo.campos["lat"].en_error


def test_sin_netcdf4_lo_dice_en_vez_de_caerse(dialogo, monkeypatch):
    # El programa tiene que abrirse en un PC sin la librería: ahí N_G se
    # escribe a mano.
    import sys
    from calculate_risk import norma
    monkeypatch.setitem(sys.modules, "netCDF4", None)
    monkeypatch.delitem(sys.modules, "calculate_risk.norma.densidad", raising=False)
    monkeypatch.delattr(norma, "densidad", raising=False)

    assert dialogo.calcular() is None
    assert "netCDF4" in dialogo.aviso.cget("text")


# ---------------------------------------------------------------------------
# Enganchado al editor del caso
# ---------------------------------------------------------------------------

def test_el_editor_tiene_el_boton_que_tenia_la_pantalla_vieja(raiz):
    editor = editor_caso.EditorCaso(raiz)

    assert editor.boton_densidad.cget("text") == "Calcular con lat/lon"


def test_el_valor_calculado_queda_en_el_n_g_del_editor(raiz):
    editor = editor_caso.EditorCaso(raiz)
    dialogo = editor.pedir_densidad()

    dialogo.calcular()
    dialogo.usar()

    assert editor.N_G.valor() == approx(N_G_MEDELLIN, rel=1e-3)