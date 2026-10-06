"""
Paso 58c: de dónde sale N_G, en la pantalla.

Reemplaza a las pruebas del diálogo «Calcular con lat/lon» (51e), y conserva lo que
ese diálogo arregló: lat = 0 es una coordenada válida y la coma decimal se acepta.
"""
import pathlib
import sys

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

from calculate_risk.norma.modelo import Emplazamiento               # noqa: E402
from ventanas import campos, editor_caso, emplazamiento            # noqa: E402

CASA_RURAL = str(pathlib.Path(__file__).resolve().parents[2] / "casos" / "casa_rural.json")
N_G_MEDELLIN = 2.5810


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def editor(raiz):
    return editor_caso.EditorCaso(raiz)


@pytest.fixture
def panel(editor):
    return editor.emplazamiento


def _escribir(panel, lat, lon):
    panel.lat.poner(lat)
    panel.lon.poner(lon)


# ---------------------------------------------------------------------------
# Por coordenadas
# ---------------------------------------------------------------------------

def test_arranca_por_coordenadas_y_en_blanco(panel):
    assert panel.modo.get() == emplazamiento.COORDENADAS
    assert panel.lat.entrada.get() == "" and panel.lon.entrada.get() == ""
    assert panel.N_G.entrada.get() == ""
    assert str(panel.N_G.entrada.cget("state")) == "readonly"


def test_la_fraccion_arranca_con_el_valor_del_modelo(panel):
    assert panel.fraccion.valor() == Emplazamiento().fraccion_nube_tierra


def test_medellin_da_el_mismo_n_g_que_el_motor(panel):
    _escribir(panel, 6.251, -75.563)

    assert panel.buscar() is not None
    assert panel.N_G.valor() == approx(N_G_MEDELLIN, rel=1e-3)
    assert "10,32" in panel.aviso.cget("text")         # coma, no punto


def test_lat_lon_cero_se_puede_calcular(panel):
    # El bug de la ventana vieja: `if float(lat):` es Falso con lat = 0.
    _escribir(panel, 0, 0)

    assert panel.buscar() is not None
    assert panel.N_G.valor() == approx(0.5126, rel=1e-3)


def test_la_coma_decimal_tambien_sirve(panel):
    _escribir(panel, "6,251", "-75,563")

    assert panel.buscar() is not None
    assert panel.N_G.valor() == approx(N_G_MEDELLIN, rel=1e-3)


def test_la_ficha_se_lee_en_el_aviso(panel):
    _escribir(panel, 2.44, -76.61)
    panel.buscar()

    texto = panel.aviso.cget("text")
    assert "4,6 km" in texto and "158 h" in texto and "0,25" in texto


def test_la_fraccion_se_puede_cambiar(panel):
    _escribir(panel, 2.44, -76.61)
    panel.fraccion.poner("0,3")

    assert panel.buscar().N_G == approx(11.64 * 0.3, abs=0.01)


def test_una_latitud_imposible_avisa_y_no_calcula(panel):
    _escribir(panel, 100, -75)

    assert panel.buscar() is None
    assert "Latitud" in panel.aviso.cget("text")
    assert panel.lat.en_error


def test_resolver_recalcula_desde_las_coordenadas(panel):
    # N_G no puede quedar desfasado: aunque alguien lo cambie, manda lo que dan
    # las coordenadas.
    _escribir(panel, 2.44, -76.61)
    panel.N_G.poner(99)

    n_g, donde = panel.resolver()

    assert n_g == approx(2.91, abs=0.01)
    assert panel.N_G.valor() == approx(2.91, abs=0.01)
    assert donde.modo == "coordenadas" and donde.lat == 2.44 and donde.lon == -76.61


# ---------------------------------------------------------------------------
# Los dos avisos nuevos
# ---------------------------------------------------------------------------

def test_fuera_de_cobertura_lo_dice_y_pasa_solo_a_declarado(panel):
    _escribir(panel, 45, -75)

    assert panel.buscar() is None
    assert panel.modo.get() == emplazamiento.DECLARADO
    assert "cobertura" in panel.aviso.cget("text")
    assert str(panel.N_G.entrada.cget("state")) == "normal"

# Lo que pegó Sergio el 28-sep, con las casillas cambiadas.
POPAYAN_LAT = "2.4399978804082365"
POPAYAN_LON = "-76.61607271745503"


def test_las_casillas_de_lat_lon_muestran_un_numero_pegado_entero(panel):
    # Con ancho 12 no se veía el número completo y no se notaba el error de tipeo.
    for campo in (panel.lat, panel.lon):
        assert int(campo.entrada.cget("width")) >= len(POPAYAN_LON)


def test_lat_lon_al_reves_lo_dice_y_no_cambia_de_modo(panel):
    _escribir(panel, POPAYAN_LON, POPAYAN_LAT)

    assert panel.buscar() is None
    assert "al revés" in panel.aviso.cget("text")
    # Se queda en coordenadas: pasar a declarado escondería lo que hay que corregir.
    assert panel.modo.get() == emplazamiento.COORDENADAS
    assert panel.lat.en_error and panel.lon.en_error
    assert panel.N_G.entrada.get() == ""


def test_lat_lon_al_reves_no_deja_calcular(panel):
    _escribir(panel, POPAYAN_LON, POPAYAN_LAT)

    with pytest.raises(campos.DatoFaltante, match="al revés"):
        panel.resolver()


def test_al_corregir_lat_lon_al_reves_se_calcula_y_se_quita_la_marca(panel):
    _escribir(panel, POPAYAN_LON, POPAYAN_LAT)
    panel.buscar()
    _escribir(panel, POPAYAN_LAT, POPAYAN_LON)

    assert panel.buscar().N_G == approx(2.91, abs=0.01)
    assert not panel.lat.en_error and not panel.lon.en_error

def test_una_celda_en_cero_no_se_calcula_en_silencio(panel):
    _escribir(panel, 0.0, -30.0)                      # Atlántico ecuatorial

    assert panel.buscar() is None
    assert panel.N_G.entrada.get() == ""
    assert "no registra descargas" in panel.aviso.cget("text")
    with pytest.raises(campos.DatoFaltante):
        panel.resolver()


# ---------------------------------------------------------------------------
# Declarado
# ---------------------------------------------------------------------------

def test_declarado_sin_fuente_avisa(panel):
    panel.poner_modo(emplazamiento.DECLARADO)
    panel.N_G.poner(4)

    with pytest.raises(campos.DatoFaltante) as fallo:
        panel.resolver()

    assert "Fuente" in str(fallo.value)


def test_declarado_con_fuente_entrega_n_g_y_procedencia(panel):
    panel.poner_modo(emplazamiento.DECLARADO)
    panel.N_G.poner(4)
    panel.fuente.poner("Red local, 2015-2020")

    n_g, donde = panel.resolver()

    assert n_g == 4.0
    assert donde == Emplazamiento(modo="declarado", fuente="Red local, 2015-2020")


def test_declarado_no_pide_coordenadas(panel):
    panel.poner_modo(emplazamiento.DECLARADO)
    panel.N_G.poner(4)
    panel.fuente.poner("x")

    panel.resolver()                                   # no lanza


def test_el_cambio_de_modo_avisa_al_editor(panel):
    avisos = []
    panel.al_cambiar = lambda: avisos.append(1)

    panel.radio_declarado.invoke()

    assert avisos and panel.modo.get() == emplazamiento.DECLARADO


# ---------------------------------------------------------------------------
# Enganchado al editor
# ---------------------------------------------------------------------------

def test_abrir_la_casa_rural_deja_su_fuente_a_la_vista(editor):
    editor.abrir(CASA_RURAL)

    panel = editor.emplazamiento
    assert panel.modo.get() == emplazamiento.DECLARADO
    assert "Anexo E.2" in panel.fuente.valor()
    assert editor.N_G.valor() == 4.0


def test_guardar_y_reabrir_por_coordenadas_conserva_todo(editor, raiz, tmp_path):
    editor.abrir(CASA_RURAL)
    editor.emplazamiento.poner_modo(emplazamiento.COORDENADAS)
    _escribir(editor.emplazamiento, 2.44, -76.61)
    ruta = str(tmp_path / "popayan.json")

    editor.guardar(ruta, tipos=(1,))
    otro = editor_caso.EditorCaso(raiz)
    otro.abrir(ruta)

    assert otro.emplazamiento.modo.get() == emplazamiento.COORDENADAS
    assert otro.emplazamiento.lat.valor() == 2.44
    assert otro.N_G.valor() == approx(2.91, abs=0.01)
    assert otro.casos_por_tipo(tipos=(1,))[1]["emplazamiento"].lat == 2.44


def test_un_archivo_sin_emplazamiento_abre_pero_pide_la_fuente(editor, raiz, tmp_path):
    import json
    datos = json.loads(pathlib.Path(CASA_RURAL).read_text(encoding="utf-8"))
    datos.pop("emplazamiento")
    ruta = tmp_path / "viejo.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    editor.abrir(str(ruta))

    assert editor.N_G.valor() == 4.0
    assert "fuente" in editor.emplazamiento.aviso.cget("text")
    with pytest.raises(campos.DatoFaltante) as fallo:
        editor.casos_por_tipo(tipos=(1,))
    assert "Fuente" in str(fallo.value)


def test_un_n_g_guardado_que_no_concuerda_con_las_coordenadas_se_avisa(editor):
    caso = {"N_G": 99.0, "estructura": None,
            "emplazamiento": Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)}

    editor.emplazamiento.poner(caso["N_G"], caso["emplazamiento"])

    assert "no coincide" in editor.emplazamiento.aviso.cget("text")


def test_sin_netcdf4_lo_dice_en_vez_de_caerse(panel, monkeypatch):
    # El programa tiene que abrirse en un PC sin la librería: ahí N_G se declara.
    from calculate_risk import norma
    monkeypatch.setitem(sys.modules, "netCDF4", None)
    monkeypatch.delitem(sys.modules, "calculate_risk.norma.densidad", raising=False)
    monkeypatch.delattr(norma, "densidad", raising=False)
    _escribir(panel, 6.251, -75.563)

    assert panel.buscar() is None
    assert "netCDF4" in panel.aviso.cget("text")


def test_declarar_funciona_aunque_falte_netcdf4(panel, monkeypatch):
    from calculate_risk import norma
    monkeypatch.setitem(sys.modules, "netCDF4", None)
    monkeypatch.delitem(sys.modules, "calculate_risk.norma.densidad", raising=False)
    monkeypatch.delattr(norma, "densidad", raising=False)
    panel.poner_modo(emplazamiento.DECLARADO)
    panel.N_G.poner(4)
    panel.fuente.poner("Red local")

    assert panel.resolver()[0] == 4.0


def test_cambiar_de_modo_pone_el_resultado_en_gris(raiz):
    # Criterio 2 del Hito G: lo que se ve tiene que ser lo que se calculó. Cambiar
    # de modo entra en la huella del editor.
    editor = editor_caso.EditorCaso(raiz)
    antes = editor.huella()

    editor.emplazamiento.radio_declarado.invoke()

    assert editor.huella() != antes


def test_limpiar_vuelve_a_coordenadas_y_en_blanco(editor):
    editor.abrir(CASA_RURAL)

    editor.limpiar()

    panel = editor.emplazamiento
    assert panel.modo.get() == emplazamiento.COORDENADAS
    assert panel.N_G.entrada.get() == "" and panel.fuente.crudo() == ""
    assert panel.aviso.cget("text") == ""