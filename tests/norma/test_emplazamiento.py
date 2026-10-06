"""
Paso 58b: el emplazamiento de un caso -- de dónde sale N_G.

Un caso guardado y reabierto conserva coordenadas y procedencia; un N_G declarado
sin fuente se rechaza; los ejemplos del Anexo E dicen que su N_G viene de la norma.
"""
import pathlib

import pytest

from calculate_risk.norma import casos, densidad
from calculate_risk.norma.modelo import Emplazamiento

CARPETA = pathlib.Path(__file__).resolve().parents[2] / "casos"
ARCHIVOS = ["casa_rural", "E3_oficinas", "E4_hospital", "E5_apartamentos"]


def _caso_por_coordenadas():
    base = casos.cargar_casos(str(CARPETA / "casa_rural.json"))[1]
    ficha = densidad.ficha_desde_lat_lon(2.44, -76.61)
    base = dict(base)
    base["N_G"] = ficha.N_G
    base["emplazamiento"] = Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)
    return base


def test_un_caso_guardado_y_reabierto_conserva_coordenadas_y_procedencia(tmp_path):
    ruta = str(tmp_path / "popayan.json")
    casos.guardar_caso(ruta, {1: _caso_por_coordenadas()})
    abierto = casos.cargar_casos(ruta)[1]
    assert abierto["emplazamiento"] == Emplazamiento(
        modo="coordenadas", lat=2.44, lon=-76.61, fraccion_nube_tierra=0.25)
    assert abierto["N_G"] == pytest.approx(2.91, abs=0.01)


def test_un_n_g_declarado_conserva_su_fuente(tmp_path):
    caso = _caso_por_coordenadas()
    caso["emplazamiento"] = Emplazamiento(modo="declarado", fuente="Red local, 2015-2020")
    ruta = str(tmp_path / "declarado.json")
    casos.guardar_caso(ruta, {1: caso})
    assert casos.cargar_casos(ruta)[1]["emplazamiento"].fuente == "Red local, 2015-2020"


def test_la_fraccion_elegida_se_conserva(tmp_path):
    caso = _caso_por_coordenadas()
    caso["emplazamiento"] = Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61,
                                          fraccion_nube_tierra=0.3)
    ruta = str(tmp_path / "f.json")
    casos.guardar_caso(ruta, {1: caso})
    assert casos.cargar_casos(ruta)[1]["emplazamiento"].fraccion_nube_tierra == 0.3


def test_un_archivo_anterior_al_paso_58_se_sigue_leyendo(tmp_path):
    import json
    datos = json.loads((CARPETA / "casa_rural.json").read_text(encoding="utf-8"))
    datos.pop("emplazamiento")
    ruta = tmp_path / "viejo.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    assert casos.cargar_casos(str(ruta))[1]["emplazamiento"] is None
    assert casos.cargar_caso(str(ruta))["emplazamiento"] is None


@pytest.mark.parametrize("nombre", ARCHIVOS)
def test_los_ejemplos_del_anexo_E_dicen_que_su_n_g_viene_de_la_norma(nombre):
    emp = casos.cargar_casos(str(CARPETA / f"{nombre}.json"))[1]["emplazamiento"]
    assert emp.modo == "declarado"
    assert "NTC 4552-2:2023" in emp.fuente
    densidad.validar(emp)


def test_declarado_sin_fuente_se_rechaza():
    with pytest.raises(densidad.EmplazamientoInvalido):
        densidad.validar(Emplazamiento(modo="declarado", fuente="   "))


def test_por_coordenadas_sin_coordenadas_se_rechaza():
    with pytest.raises(densidad.EmplazamientoInvalido):
        densidad.validar(Emplazamiento(modo="coordenadas", lat=2.44))


def test_un_modo_desconocido_se_rechaza():
    with pytest.raises(densidad.EmplazamientoInvalido):
        densidad.validar(Emplazamiento(modo="adivinado", fuente="x"))


def test_por_coordenadas_no_pide_fuente():
    densidad.validar(Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61))


def test_ficha_de_un_emplazamiento_por_coordenadas():
    ficha = densidad.ficha_de(Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61))
    assert ficha.N_G == pytest.approx(2.91, abs=0.01)


def test_un_declarado_no_tiene_ficha():
    with pytest.raises(densidad.EmplazamientoInvalido):
        densidad.ficha_de(Emplazamiento(modo="declarado", fuente="x"))


def test_fuera_de_cobertura_la_ficha_lanza_y_obliga_a_declarar():
    with pytest.raises(densidad.FueraDeCobertura):
        densidad.ficha_de(Emplazamiento(modo="coordenadas", lat=45.0, lon=10.0))


def test_concuerda_detecta_un_n_g_que_ya_no_corresponde_a_las_coordenadas():
    emp = Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)
    n_g = densidad.ficha_de(emp).N_G
    assert densidad.concuerda(emp, n_g) is True
    assert densidad.concuerda(emp, n_g * 1.5) is False


def test_un_declarado_siempre_concuerda():
    assert densidad.concuerda(Emplazamiento(modo="declarado", fuente="x"), 123.0) is True