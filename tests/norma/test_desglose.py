"""
Paso 56: la ventana «De dónde viene el riesgo».

Arriba los componentes con lo que aporta cada uno; al elegir uno, abajo las
medidas que lo bajan en este caso. Lo que se prueba aquí es lo que el usuario
ve: que arranque por el componente que más pesa, que al cambiar de componente
cambie la lista de abajo, que se diga cuándo una sola medida ya hace cumplir,
y que en la pantalla no aparezca nunca una llave pelada como «spcr:...».
"""
import pytest

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

from calculate_risk.norma import casos, medidas, riesgos                # noqa: E402
from ventanas import desglose                                           # noqa: E402

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
def resultado(caso):
    return riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                           caso["N_G"], tipos=(1,))[1]


@pytest.fixture
def ventana(raiz, caso, resultado):
    aportes = medidas.de_donde_viene(caso["estructura"], caso["lineas"],
                                     caso["zonas"], caso["N_G"], tipo=1)
    return desglose.VentanaDesglose(raiz, 1, aportes, resultado)


def test_arranca_por_el_componente_que_mas_pesa(ventana):
    assert ventana.componentes.selection() == ("R_V",)
    assert "R_V" in ventana.marco_medidas.cget("text")


def test_los_componentes_salen_con_su_valor_y_su_parte(ventana):
    filas = ventana.filas_componentes()

    assert [f[0] for f in filas] == ["R_V", "R_B", "R_U", "R_A"]
    assert filas[0][2] == "95,8 %"


def test_el_componente_lleva_su_explicacion_no_solo_la_letra(ventana):
    texto = ventana.componentes.item("R_V", "text")

    assert "R_V" in texto
    assert "LÍNEA" in texto


def test_al_elegir_otro_componente_cambia_la_lista_de_abajo(ventana):
    antes = ventana.filas_medidas()

    ventana.elegir("R_B")

    assert ventana.filas_medidas() != antes
    assert "R_B" in ventana.marco_medidas.cget("text")
    # el SPCR baja el daño físico a la estructura; el blindaje de línea no
    textos = " ".join(f[0] for f in ventana.filas_medidas())
    assert "SPCR" in textos


def test_dice_cuando_una_sola_medida_ya_hace_cumplir(ventana):
    veredictos = [f[3] for f in ventana.filas_medidas()]

    assert "Sí, ya cumple" in veredictos
    assert "No, ella sola no" in veredictos


def test_no_se_ve_ninguna_llave_pelada(ventana):
    for componente in ("R_V", "R_B", "R_U", "R_A"):
        ventana.elegir(componente)
        for fila in ventana.filas_medidas():

            assert ":" not in fila[0], fila[0]
            assert "_" not in fila[0], fila[0]


def test_un_componente_sin_medidas_dice_que_hacer(raiz, resultado):
    huerfano = medidas.Aporte(componente="R_B", valor=1.0, fraccion=1.0,
                              rebajas=())
    ventana = desglose.VentanaDesglose(raiz, 1, [huerfano], resultado)

    textos = [f[0] for f in ventana.filas_medidas()]

    assert len(textos) == 1
    assert "Ninguna medida" in textos[0]


def test_el_encabezado_lleva_el_riesgo_y_el_veredicto(ventana):
    texto = ventana.titulo.cget("text")

    assert "2,506e-05" in texto
    assert "1,000e-05" in texto
    assert "No cumple" in texto