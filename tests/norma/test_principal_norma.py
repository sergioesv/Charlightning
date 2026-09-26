"""
Paso 51a: la ventana de la pantalla nueva.

Junta el editor y el panel de resultados. Lo que se prueba es el
comportamiento de los botones, no el dibujo: que Calcular llene el panel,
que Abrir y Guardar pasen por un archivo de verdad, que el Informe escriba
la memoria, y sobre todo que **nada de eso calcule con datos que faltan**.

Los messagebox bloquean esperando un clic, así que se reemplazan por una
lista donde quedan anotados: además de no colgar la prueba, permite
comprobar QUÉ le dijo el programa al usuario.
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

from ventanas import principal_norma                                # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def avisos(monkeypatch):
    """Lo que el programa le habría dicho al usuario."""
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
    return p


# ---------------------------------------------------------------------------
# La ventana está armada
# ---------------------------------------------------------------------------

def test_tiene_los_cinco_botones(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)

    assert sorted(p.botones) == ["Abrir caso", "Calcular", "Guardar caso",
                                 "Informe", "Volver"]


def test_arranca_evaluando_solo_el_riesgo_de_vidas(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)

    assert p.tipos() == (1,)


def test_se_pueden_marcar_mas_riesgos(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.marcas[4].set(True)

    assert p.tipos() == (1, 4)


def test_sin_ningun_riesgo_marcado_evalua_r1(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.marcas[1].set(False)

    assert p.tipos() == (1,)


# ---------------------------------------------------------------------------
# Calcular
# ---------------------------------------------------------------------------

def test_calcular_da_el_riesgo_de_la_norma_y_llena_el_panel(pantalla):
    resultado = pantalla.calcular()

    assert resultado[1]["total"] == approx(2.506e-5, rel=0.01)
    filas = pantalla.resultados.filas()
    assert filas[0][4] == "No cumple"
    assert filas[1][1] == "Z2_interior"


def test_calcular_con_datos_a_medias_avisa_y_no_deja_resultados(pantalla, avisos):
    pantalla.editor.zonas.anadir()          # una zona nueva, vacía

    assert pantalla.calcular() is None
    assert pantalla.resultados.filas() == []
    assert "Zona 2" in avisos[-1]


def test_volver_a_calcular_no_acumula(pantalla):
    pantalla.calcular()
    antes = len(pantalla.resultados.filas())

    pantalla.calcular()

    assert len(pantalla.resultados.filas()) == antes


# ---------------------------------------------------------------------------
# Abrir y guardar
# ---------------------------------------------------------------------------

def test_abrir_carga_el_caso_y_borra_los_resultados_viejos(pantalla):
    pantalla.calcular()

    pantalla.abrir(RUTA_CASA_RURAL)

    assert pantalla.editor.lineas.nombres() == ["potencia", "telecomunicacion"]
    assert pantalla.resultados.filas() == []


def test_abrir_un_archivo_que_no_existe_avisa_en_vez_de_caerse(pantalla, avisos):
    assert pantalla.abrir("no_existe.json") is None
    assert avisos            # le dijo algo al usuario


def test_guardar_y_volver_a_abrir_deja_el_mismo_riesgo(pantalla, tmp_path):
    antes = pantalla.calcular()[1]["total"]
    ruta = tmp_path / "caso.json"

    pantalla.guardar(ruta)
    pantalla.abrir(ruta)

    assert pantalla.calcular()[1]["total"] == approx(antes)


def test_no_se_guarda_un_caso_incompleto(pantalla, tmp_path, avisos):
    pantalla.editor.zonas.anadir()
    ruta = tmp_path / "no.json"

    assert pantalla.guardar(ruta) is None
    assert not ruta.exists()
    assert avisos


def test_cancelar_el_dialogo_no_hace_nada(pantalla, monkeypatch):
    monkeypatch.setattr(principal_norma.filedialog, "asksaveasfilename",
                        lambda **kwargs: "")

    assert pantalla.guardar() is None


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def test_el_informe_escribe_la_memoria(pantalla, tmp_path, avisos):
    pantalla.calcular()
    ruta = tmp_path / "memoria.tex"

    pantalla.informe(ruta)

    contenido = open(ruta, encoding="utf-8").read()
    assert contenido.startswith("\\documentclass")
    assert "Z2\\_interior" in contenido
    assert avisos            # dice dónde quedó

def test_el_informe_deja_las_figuras_y_el_csv_junto_al_tex(pantalla, tmp_path, avisos):
    # Paso 51c: el informe de la pantalla nueva ya no es solo el .tex. Los PNG
    # tienen que quedar en la MISMA carpeta o LaTeX no los encuentra al compilar.
    pantalla.calcular()

    pantalla.informe(tmp_path / "memoria.tex")

    assert (tmp_path / "memoria_sensibilidad.png").exists()
    assert (tmp_path / "memoria_medidas.csv").exists()
    assert "memoria_sensibilidad.png" in open(tmp_path / "memoria.tex",
                                              encoding="utf-8").read()


def test_el_informe_calcula_solo_si_hace_falta(pantalla, tmp_path):
    # Sin haber pulsado Calcular, el Informe tiene que calcular por su cuenta.
    ruta = tmp_path / "memoria.tex"

    pantalla.informe(ruta)

    assert pantalla.ultimo_calculo is not None
    assert ruta.exists()


def test_sin_datos_no_hay_informe(raiz, tmp_path, avisos):
    vacia = principal_norma.PrincipalNorma(raiz)
    ruta = tmp_path / "memoria.tex"

    assert vacia.informe(ruta) is None
    assert not ruta.exists()


# ---------------------------------------------------------------------------
# Buscar medidas
# ---------------------------------------------------------------------------

def test_el_buscador_solo_corre_si_algo_no_cumple(pantalla):
    # Sin calcular no hay nada que buscar.
    assert pantalla.buscar_medidas() is None


def test_el_buscador_encuentra_soluciones_para_la_casa_rural(pantalla):
    pantalla.calcular()

    soluciones = pantalla.buscar_medidas()

    assert soluciones, "la casa rural sí tiene solución en la norma"
    assert all(s.cumple for s in soluciones)
    assert soluciones[0].riesgo < 1e-5
    # y quedan a la vista, ordenadas
    assert len(pantalla.tabla_medidas.get_children()) <= (
        principal_norma.CUANTAS_SOLUCIONES)


def test_las_dos_soluciones_de_la_norma_estan_entre_las_encontradas(pantalla):
    # El Anexo E.2 publica 0,223e-5 y 0,141e-5 para la casa rural.
    pantalla.calcular()

    riesgos_hallados = [s.riesgo for s in pantalla.buscar_medidas()]

    for publicado in (0.223e-5, 0.141e-5):
        assert any(r == approx(publicado, rel=0.02) for r in riesgos_hallados), publicado


# ---------------------------------------------------------------------------
# Los datos del proyecto llegan al informe
# ---------------------------------------------------------------------------

def test_los_datos_del_proyecto_van_al_informe(pantalla, tmp_path, avisos):
    principal_norma.papo["proyecto"] = "Casa rural del Anexo E.2"
    principal_norma.papo["descripcion"] = "Prueba de la descripción"
    pantalla.calcular()
    ruta = tmp_path / "m.tex"

    pantalla.informe(ruta)

    contenido = open(ruta, encoding="utf-8").read()
    assert "Casa rural del Anexo E.2" in contenido
    assert "Prueba de la descripción" in contenido