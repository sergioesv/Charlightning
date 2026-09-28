"""
Paso 60: las figuras del informe.

Comprueban que cada figura sale como PNG legible, que los errores son claros, que el mapa
respeta la proporción geográfica, que las fronteras existen y que dibujar no toca el
estado global de matplotlib (la pantalla del programa lo usa).
"""
import os

import pytest

matplotlib = pytest.importorskip("matplotlib")

from calculate_risk.informe import figuras          # noqa: E402

MAGIA_PNG = b"\x89PNG\r\n\x1a\n"


def _es_png(ruta) -> bool:
    with open(ruta, "rb") as f:
        return f.read(8) == MAGIA_PNG


def _tamano(ruta):
    from matplotlib.image import imread
    alto, ancho = imread(str(ruta)).shape[:2]
    return ancho, alto


# ---------------------------------------------------------------------------
# Fronteras
# ---------------------------------------------------------------------------

def test_el_archivo_de_fronteras_esta_en_el_repositorio():
    assert os.path.exists(figuras.RUTA_PAISES)


def test_hay_mas_de_doscientos_paises_y_colombia_entre_ellos():
    nombres = [nombre for nombre, _ in figuras.contornos()]
    assert len(nombres) > 200 and "Colombia" in nombres


def test_popayan_cae_en_colombia_y_el_atlantico_en_ningun_pais():
    paises = figuras.contornos()
    assert figuras.pais_que_contiene(paises, 2.44, -76.61) == "Colombia"
    assert figuras.pais_que_contiene(paises, 0.0, -30.0) is None


# ---------------------------------------------------------------------------
# Proporción geográfica
# ---------------------------------------------------------------------------

def test_en_el_ecuador_la_proporcion_es_uno():
    assert figuras.aspecto_geografico(0) == pytest.approx(1.0)


def test_a_sesenta_grados_un_grado_de_longitud_mide_la_mitad():
    assert figuras.aspecto_geografico(60) == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# Las cuatro figuras
# ---------------------------------------------------------------------------

def test_el_mapa_de_popayan_sale_como_png(tmp_path):
    pytest.importorskip("netCDF4")
    ruta = figuras.mapa_del_sitio(2.44, -76.61, "Vivienda rural", str(tmp_path / "mapa.png"))

    assert _es_png(ruta)
    ancho, alto = _tamano(ruta)
    assert ancho > 1000 and alto > 800


def test_el_mapa_de_un_sitio_en_el_mar_tambien_sale(tmp_path):
    pytest.importorskip("netCDF4")
    ruta = figuras.mapa_del_sitio(0.0, -30.0, "Mar", str(tmp_path / "mar.png"))

    assert _es_png(ruta)


def test_el_mapa_fuera_de_cobertura_lanza_y_no_dibuja(tmp_path):
    pytest.importorskip("netCDF4")
    from calculate_risk.norma import densidad
    destino = tmp_path / "nada.png"

    with pytest.raises(densidad.FueraDeCobertura):
        figuras.mapa_del_sitio(45.0, 10.0, "Europa", str(destino))

    assert not destino.exists()


def test_el_area_de_captacion_sale_como_png(tmp_path):
    ruta = figuras.area_de_captacion(15, 20, 6, 2577.9, str(tmp_path / "a.png"),
                                     lineas=("potencia", "telecomunicación"))

    assert _es_png(ruta)


def test_el_area_de_captacion_cuando_gobierna_el_saliente_sale_como_png(tmp_path):
    ruta = figuras.area_de_captacion(15, 20, 6, 3000.0, str(tmp_path / "s.png"),
                                     saliente_gobierna=True)

    assert _es_png(ruta)


def test_el_aporte_de_componentes_sale_como_png(tmp_path):
    ruta = figuras.aporte_de_componentes(
        [("$R_V$", 2.4e-5), ("$R_B$", 1.0e-6), ("$R_C$", 0.0)], str(tmp_path / "c.png"))

    assert _es_png(ruta)


def test_el_aporte_de_componentes_sin_ningun_riesgo_es_un_error_claro(tmp_path):
    with pytest.raises(ValueError, match="ning"):
        figuras.aporte_de_componentes([("$R_V$", 0.0)], str(tmp_path / "c.png"))


def test_el_riesgo_contra_tolerable_sale_como_png(tmp_path):
    ruta = figuras.riesgo_contra_tolerable(
        [("Sin protección", 2.5e-5), ("Con medida", 1.0e-6)], 1e-5, str(tmp_path / "v.png"))

    assert _es_png(ruta)


@pytest.mark.parametrize("barras, tolerable", [([], 1e-5), ([("a", 0.0)], 1e-5),
                                               ([("a", 1e-6)], 0.0)])
def test_el_riesgo_contra_tolerable_rechaza_valores_imposibles(tmp_path, barras, tolerable):
    with pytest.raises(ValueError):
        figuras.riesgo_contra_tolerable(barras, tolerable, str(tmp_path / "v.png"))


def test_la_notacion_cientifica_usa_coma_y_exponente():
    assert figuras._cientifico(1e-5) == "1,0 × 10$^{-5}$"


# ---------------------------------------------------------------------------
# No se mete con el resto de matplotlib
# ---------------------------------------------------------------------------

def test_dibujar_no_cambia_el_backend_ni_deja_figuras_abiertas(tmp_path):
    import matplotlib.pyplot as plt
    antes = matplotlib.get_backend(), plt.get_fignums()

    figuras.riesgo_contra_tolerable([("a", 2e-5)], 1e-5, str(tmp_path / "v.png"))
    figuras.aporte_de_componentes([("$R_V$", 1e-5)], str(tmp_path / "c.png"))

    assert (matplotlib.get_backend(), plt.get_fignums()) == antes


def test_dibujar_no_cambia_las_preferencias_de_matplotlib(tmp_path):
    familia = matplotlib.rcParams["font.family"]
    fuente_matematica = matplotlib.rcParams["mathtext.fontset"]

    figuras.riesgo_contra_tolerable([("a", 2e-5)], 1e-5, str(tmp_path / "v.png"))

    assert matplotlib.rcParams["font.family"] == familia
    assert matplotlib.rcParams["mathtext.fontset"] == fuente_matematica