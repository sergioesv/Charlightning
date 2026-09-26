"""
Paso 48: guardar y abrir el caso.

El formato del Paso 33 guarda las pérdidas de UN riesgo. Como el editor
trabaja con los cuatro, la zona puede traer además una llave "perdidas" con
un juego por tipo. Los archivos viejos se siguen leyendo igual, y eso se
prueba con el propio casos/casa_rural.json del repositorio.

La prueba que cierra el paso es la ida y vuelta completa: editor -> archivo
-> editor -> mismo riesgo.
"""
import json

import pytest
from pytest import approx

from calculate_risk.norma import casos, riesgos

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


def _riesgo(caso_leido, tipo=1):
    return riesgos.evaluar(caso_leido["estructura"], caso_leido["lineas"],
                           caso_leido["zonas"], caso_leido["N_G"],
                           tipos=(tipo,))[tipo]["total"]


# ---------------------------------------------------------------------------
# El formato viejo se sigue leyendo
# ---------------------------------------------------------------------------

def test_el_archivo_de_la_casa_rural_se_lee_con_el_formato_nuevo():
    por_tipo = casos.cargar_casos(RUTA_CASA_RURAL)

    assert sorted(por_tipo) == [1]        # su "tipos" dice [1]
    assert _riesgo(por_tipo[1]) == approx(2.506e-5, rel=0.01)


def test_cargar_casos_y_cargar_caso_dan_la_misma_zona(caso):
    por_tipo = casos.cargar_casos(RUTA_CASA_RURAL)

    assert por_tipo[1]["zonas"] == caso["zonas"]
    assert por_tipo[1]["estructura"] == caso["estructura"]
    assert por_tipo[1]["lineas"] == caso["lineas"]


# ---------------------------------------------------------------------------
# Guardar y volver a abrir
# ---------------------------------------------------------------------------

def test_ida_y_vuelta_de_un_solo_riesgo(tmp_path, caso):
    ruta = tmp_path / "uno.json"
    casos.guardar_caso(ruta, {1: caso})

    devuelto = casos.cargar_casos(ruta)

    assert sorted(devuelto) == [1]
    assert devuelto[1]["zonas"] == caso["zonas"]
    assert _riesgo(devuelto[1]) == approx(2.506e-5, rel=0.01)


def test_ida_y_vuelta_de_los_cuatro_riesgos(tmp_path, caso):
    from dataclasses import replace

    # Cuatro casos que comparten todo menos las pérdidas de la zona
    zona = caso["zonas"][0]
    por_tipo = {
        1: {**caso, "zonas": [zona]},
        2: {**caso, "zonas": [replace(zona, L_T=0, L_F=1e-1, L_O=1e-2, h_z=1)]},
        3: {**caso, "zonas": [replace(zona, L_T=0, L_F=1e-1, L_O=0, h_z=1, c_z=500)]},
        4: {**caso, "zonas": [replace(zona, L_F=0.2, L_O=1e-3,
                                      razones_l4_unitarias=True)]},
    }
    ruta = tmp_path / "cuatro.json"
    casos.guardar_caso(ruta, por_tipo)

    devuelto = casos.cargar_casos(ruta)

    assert sorted(devuelto) == [1, 2, 3, 4]
    for tipo in (1, 2, 3, 4):
        assert devuelto[tipo]["zonas"] == por_tipo[tipo]["zonas"], tipo


def test_lo_que_cambia_por_riesgo_no_se_repite_en_lo_comun(tmp_path, caso):
    from dataclasses import replace

    zona = caso["zonas"][0]        # la casa rural tiene L_F = 0,1
    ruta = tmp_path / "x.json"
    casos.guardar_caso(ruta, {1: {**caso, "zonas": [zona]},
                              2: {**caso, "zonas": [replace(zona, L_F=1e-2)]}})

    crudo = json.loads(open(ruta, encoding="utf-8").read())
    guardada = crudo["zonas"][0]

    assert "L_F" not in guardada                  # cambia: solo va en perdidas
    assert guardada["perdidas"]["1"]["L_F"] == zona.L_F
    assert guardada["perdidas"]["2"]["L_F"] == 1e-2
    assert guardada["n_z"] == zona.n_z            # no cambia: queda en lo común


def test_los_sistemas_internos_y_la_adyacente_sobreviven(tmp_path, caso):
    from calculate_risk.norma.modelo import Estructura
    from dataclasses import replace

    con_vecina = replace(caso["lineas"][0],
                         adyacente=Estructura(L=30, W=20, H=10), C_DJ=0.5)
    ruta = tmp_path / "y.json"
    casos.guardar_caso(ruta, {1: {**caso, "lineas": [con_vecina]}})

    devuelto = casos.cargar_casos(ruta)[1]

    assert devuelto["lineas"][0].adyacente == Estructura(L=30, W=20, H=10)
    assert devuelto["lineas"][0].C_DJ == 0.5
    assert len(devuelto["zonas"][0].sistemas_internos) == 2
    assert devuelto["zonas"][0].sistemas_internos[0].nombre == "pot"


def test_una_linea_sin_estructura_vecina_vuelve_sin_ella(tmp_path, caso):
    ruta = tmp_path / "z.json"
    casos.guardar_caso(ruta, {1: caso})

    devuelto = casos.cargar_casos(ruta)[1]

    assert devuelto["lineas"][0].adyacente is None


def test_el_archivo_guardado_es_legible_a_ojo(tmp_path, caso):
    # Un caso es un documento del proyecto: tiene que poder abrirse y leerse.
    ruta = tmp_path / "w.json"
    casos.guardar_caso(ruta, {1: caso})

    texto = open(ruta, encoding="utf-8").read()

    assert texto.startswith("{\n")           # con sangría, no en una sola línea
    assert "telecomunicacion" in texto       # y con los acentos tal cual