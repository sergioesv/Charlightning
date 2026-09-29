"""
Paso 53: lo que se ve en el panel tiene que salir de los datos que se ven.

Es el punto 1 de la Fase 6 y el único de los cinco que toca el rigor del
cálculo. Antes: se calculaba, salía R1 = 2,506e-5 «No cumple», se cambiaba
el SPCR a nivel I y el panel seguía enseñando 2,506e-5. Un pantallazo de esa
pantalla es un resultado que no corresponde a sus datos.

Y lo que no se veía: el Informe armaba la memoria con las entradas FRESCAS
del formulario y los riesgos VIEJOS, así que el documento salía con las
tablas de entrada nuevas y el riesgo antiguo. Eso es lo que prueba
test_el_informe_no_mezcla_entradas_nuevas_con_riesgos_viejos.
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

from calculate_risk.norma import memoria                            # noqa: E402
from ventanas import principal_norma, resultados                    # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def avisos(monkeypatch):
    dichos = []
    monkeypatch.setattr(principal_norma.messagebox, "showinfo",
                        lambda **kwargs: dichos.append(kwargs.get("message", "")))
    return dichos


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def pantalla(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.abrir(RUTA_CASA_RURAL)
    p.calcular()
    return p


def _color_del_veredicto(panel) -> str:
    return str(panel.arbol.tag_configure("no_cumple", "foreground"))


# ---------------------------------------------------------------------------
# El panel se marca en cuanto los datos dejan de ser los del cálculo
# ---------------------------------------------------------------------------

def test_cambiar_un_dato_pone_el_panel_en_gris_y_lo_dice(pantalla):
    pantalla.editor.N_G.poner(40)

    assert pantalla.revisar_cambios() is True
    assert pantalla.resultados.obsoleto
    assert "volver a calcular" in pantalla.resultados.aviso.cget("text")
    assert _color_del_veredicto(pantalla.resultados) == resultados.GRIS
    # y no se puede abrir el desglose de un riesgo que ya no vale
    assert str(pantalla.resultados.boton_desglose.cget("state")) == "disabled"


def test_deshacer_el_cambio_devuelve_el_resultado(pantalla):
    antes = pantalla.editor.N_G.entrada.get()
    pantalla.editor.N_G.poner(40)
    pantalla.revisar_cambios()

    pantalla.editor.N_G.poner(antes)

    assert pantalla.revisar_cambios() is False
    assert not pantalla.resultados.obsoleto
    assert _color_del_veredicto(pantalla.resultados) == resultados.NARANJA
    assert pantalla.resultados.filas()[0][4] == "No cumple"


def test_el_aviso_llega_solo_desde_la_pantalla(pantalla):
    # Sin llamar a revisar_cambios(): el evento de la lista tiene que bastar.
    # Se usa la lista y no una casilla de escribir porque un <KeyRelease> va a
    # la ventana CON EL FOCO, y bajo Xvfb no hay gestor de ventanas que se lo
    # dé a nadie: el evento no llegaría ni a la propia casilla.
    combo = pantalla.editor.estructura.campos["C_D"].combo
    combo.current(1 if combo.current() != 1 else 2)
    combo.event_generate("<<ComboboxSelected>>")

    assert pantalla.resultados.obsoleto


def test_tocar_fuera_del_editor_no_invalida_nada(pantalla):
    pantalla.resultados.arbol.event_generate("<ButtonRelease-1>")

    assert not pantalla.resultados.obsoleto


def test_anadir_una_zona_invalida_el_resultado(pantalla):
    # La zona nueva está vacía, pero el resultado ya no corresponde igual.
    pantalla.editor.zonas.anadir()

    assert pantalla.revisar_cambios() is True


def test_marcar_otro_riesgo_invalida_el_resultado(pantalla):
    pantalla.marcas[4].set(True)

    assert pantalla.revisar_cambios() is True


def test_sin_haber_calculado_no_hay_nada_que_invalidar(raiz, avisos):
    vacia = principal_norma.PrincipalNorma(raiz)

    assert vacia.revisar_cambios() is False
    assert vacia.resultados.marcar_obsoleto() is False


# ---------------------------------------------------------------------------
# El entregable: la memoria nunca mezcla entradas nuevas con riesgos viejos
# ---------------------------------------------------------------------------

def test_el_informe_no_mezcla_entradas_nuevas_con_riesgos_viejos(pantalla, tmp_path,
                                                                 avisos):
    viejo = pantalla.ultimo_calculo[1]["total"]
    # Diez veces más rayos: todas las frecuencias son proporcionales a N_G,
    # así que el riesgo tiene que salir diez veces mayor.
    pantalla.editor.N_G.poner(float(pantalla.editor.N_G.entrada.get()) * 10)
    ruta = tmp_path / "memoria.tex"

    pantalla.informe(ruta)

    nuevo = pantalla.ultimo_calculo[1]["total"]
    assert nuevo == approx(viejo * 10, rel=1e-9)
    contenido = open(ruta, encoding="utf-8").read()
    assert memoria.numero(nuevo) in contenido
    assert memoria.numero(viejo) not in contenido
