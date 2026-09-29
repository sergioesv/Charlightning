"""
Paso 61b: el informe en PDF con una sola llamada (informe/generar.py).

Lo que se vigila: que salga el PDF y nada más en la carpeta, que las figuras que no se
pueden hacer no tumben el informe (lo dicen en `avisos`), que las medidas solo se busquen
para los riesgos que no cumplen, y que los números lleguen tal cual los dio el motor.
No necesitan pantalla gráfica.
"""
from datetime import date

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("matplotlib")

from calculate_risk.informe import armado, figuras, generar      # noqa: E402
from calculate_risk.norma import casos, medidas, riesgos          # noqa: E402
from calculate_risk.norma.modelo import Emplazamiento             # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"
PROYECTO = {"Proyecto": "Vivienda rural", "Diseñador": "Sergio Estrada Vega"}


@pytest.fixture
def casa():
    return casos.cargar_casos(RUTA_CASA_RURAL)


def _evaluar(casos_):
    return {t: riesgos.evaluar(c["estructura"], c["lineas"], c["zonas"], c["N_G"],
                               tipos=(t,))[t] for t, c in casos_.items()}


def _generar(carpeta, casos_, **nombrados):
    nombrados.setdefault("buscar_medidas", False)       # explorar tarda: solo donde importa
    return generar.generar_informe(carpeta, casos_, _evaluar(casos_), proyecto=PROYECTO,
                                   nombre="informe", fecha=date(2026, 9, 28), **nombrados)


def test_la_casa_rural_sale_en_pdf_con_sus_figuras_y_sus_medidas(casa, tmp_path):
    informe = _generar(tmp_path, casa, buscar_medidas=True)

    assert informe.ruta == str(tmp_path / "informe.pdf")
    assert (tmp_path / "informe.pdf").read_bytes()[:4] == b"%PDF"
    assert informe.paginas > 3
    assert informe.avisos == []
    # declarado: sin mapa; R1 no cumple: figura del veredicto
    assert informe.figuras == ("area", "aporte", "veredicto")


def test_en_la_carpeta_solo_queda_el_pdf(casa, tmp_path):
    _generar(tmp_path, casa)

    assert [p.name for p in tmp_path.iterdir()] == ["informe.pdf"]


def test_por_coordenadas_trae_el_mapa(casa, tmp_path):
    popayan = Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)
    por_coordenadas = {t: dict(c, emplazamiento=popayan) for t, c in casa.items()}

    informe = _generar(tmp_path, por_coordenadas)

    assert "mapa" in informe.figuras
    assert informe.avisos == []


def test_sin_matplotlib_el_informe_sale_igual_y_lo_dice(casa, tmp_path, monkeypatch):
    def sin_libreria(*argumentos, **nombrados):
        raise ImportError("No module named 'matplotlib'")
    monkeypatch.setattr(generar, "dibujar_figuras", sin_libreria)

    informe = _generar(tmp_path, casa)

    assert (tmp_path / "informe.pdf").exists()
    assert informe.figuras == ()
    assert any("sin figuras" in aviso for aviso in informe.avisos)


def test_una_figura_que_falla_no_arrastra_a_las_demas(casa, tmp_path, monkeypatch):
    def rota(*argumentos, **nombrados):
        raise ValueError("no hay datos")
    monkeypatch.setattr(figuras, "aporte_de_componentes", rota)

    informe = _generar(tmp_path, casa)

    assert informe.figuras == ("area",)
    assert any("de dónde viene el riesgo" in aviso for aviso in informe.avisos)


def test_un_riesgo_que_cumple_no_busca_medidas(casa, tmp_path, monkeypatch):
    def no_deberia(*argumentos, **nombrados):
        raise AssertionError("se exploraron medidas de un riesgo que cumple")
    monkeypatch.setattr(medidas, "explorar", no_deberia)
    pocos_rayos = {t: dict(c, N_G=0.01) for t, c in casa.items()}

    informe = _generar(tmp_path, pocos_rayos, buscar_medidas=True)

    assert (tmp_path / "informe.pdf").exists()
    assert "veredicto" not in informe.figuras


def test_los_numeros_llegan_tal_cual_los_dio_el_motor(casa, tmp_path, monkeypatch):
    # generar no recalcula: pasa a armar() el MISMO por_tipo que recibió (el del panel).
    recibido = {}
    original = armado.armar

    def espia(casos_, por_tipo, **nombrados):
        recibido["por_tipo"] = por_tipo
        return original(casos_, por_tipo, **nombrados)
    monkeypatch.setattr(armado, "armar", espia)
    por_tipo = _evaluar(casa)

    generar.generar_informe(tmp_path, casa, por_tipo, buscar_medidas=False)

    assert recibido["por_tipo"] is por_tipo


def test_avisa_cada_etapa_para_que_la_pantalla_lo_muestre(casa, tmp_path):
    etapas = []

    _generar(tmp_path, casa, buscar_medidas=True, avance=etapas.append)

    assert etapas == ["Leyendo el dato de N_G…",
                      "Buscando medidas de protección para R1…",
                      "Dibujando las figuras…",
                      "Componiendo el PDF…"]