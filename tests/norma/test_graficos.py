"""
Paso 39b: figuras PNG de los barridos.

Un grafico no se puede "probar" mirandolo desde pytest, asi que lo que se
comprueba es lo verificable: que el archivo se cree, que sea un PNG de verdad
(por su firma binaria), que no se quede ninguna figura abierta consumiendo
memoria, y que los casos borde no revienten.
"""
import matplotlib.pyplot as plt

from calculate_risk.norma import barridos, graficos, medidas
from calculate_risk.norma.adaptador import caso_desde_pantalla
from tests.datos_pantalla import CASA_RURAL

FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def _casa_rural():
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)
    return c["estructura"], c["lineas"], c["zonas"], c["N_G"]


def _es_png(ruta):
    with open(ruta, "rb") as f:
        return f.read(8) == FIRMA_PNG


def test_curva_de_sensibilidad_genera_un_png(tmp_path):
    puntos = barridos.barrer(*_casa_rural(), valores=[1, 2, 4, 8], destino="N_G")
    ruta = graficos.curva_sensibilidad(puntos, tmp_path / "ng.png",
                                       etiqueta_x="N_G", titulo="Prueba")

    assert _es_png(ruta)
    assert (tmp_path / "ng.png").stat().st_size > 5000


def test_la_curva_acepta_escala_logaritmica(tmp_path):
    puntos = barridos.barrer(*_casa_rural(), valores=[0.5, 1, 2, 4, 8, 16],
                             destino="N_G")
    ruta = graficos.curva_sensibilidad(puntos, tmp_path / "log.png",
                                       escala_x="log")

    assert _es_png(ruta)


def test_dispersion_costo_riesgo_genera_un_png(tmp_path):
    estructura, lineas, zonas, N_G = _casa_rural()
    soluciones = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                                  solo_familias={"spcr", "dps"},
                                  solo_las_que_cumplen=False)
    ruta = graficos.dispersion_costo_riesgo(soluciones, tmp_path / "costo.png")

    assert _es_png(ruta)


def test_la_dispersion_funciona_aunque_todas_cumplan(tmp_path):
    # Si se filtran solo las que cumplen, no hay puntos naranjas: la figura
    # tiene que salir igual, sin reventar por una lista vacia.
    estructura, lineas, zonas, N_G = _casa_rural()
    soluciones = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                                  solo_familias={"spcr", "dps"})

    assert all(s.cumple for s in soluciones)
    assert _es_png(graficos.dispersion_costo_riesgo(soluciones, tmp_path / "todas.png"))


def test_no_quedan_figuras_abiertas(tmp_path):
    # matplotlib avisa a partir de 20 figuras abiertas; si no se cierran, un
    # barrido largo se come la memoria.
    abiertas_antes = len(plt.get_fignums())

    puntos = barridos.barrer(*_casa_rural(), valores=[1, 2], destino="N_G")
    for i in range(3):
        graficos.curva_sensibilidad(puntos, tmp_path / f"f{i}.png")

    assert len(plt.get_fignums()) == abiertas_antes