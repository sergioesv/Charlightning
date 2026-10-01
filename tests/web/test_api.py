"""
La página web: la API responde lo mismo que el motor y rechaza lo que no sirve.
"""
import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from web import api, servicio
from web.limite import Limite

CASA_RURAL = json.loads(Path("casos/casa_rural.json").read_text(encoding="utf-8"))


@pytest.fixture
def cliente(monkeypatch):
    # Límites nuevos en cada prueba, para que no se estorben entre ellas.
    monkeypatch.setattr(api, "limite_calculo", Limite(1000, 60))
    monkeypatch.setattr(api, "limite_informe", Limite(1000, 60))
    return TestClient(api.app)


def test_salud(cliente):
    assert cliente.get("/api/salud").json()["estado"] == "ok"


def test_la_casa_rural_da_lo_de_la_norma(cliente):
    datos = cliente.post("/api/evaluar", json=CASA_RURAL).json()
    r1 = datos["riesgos"]["1"]
    assert r1["total"] == pytest.approx(2.51e-5, rel=0.01)
    assert r1["R_T"] == 1e-5
    assert r1["cumple"] is False
    assert r1["componentes"]["R_V"] == pytest.approx(2.40e-5, rel=0.01)


def test_la_validacion_reproduce_el_anexo_E(cliente):
    filas = cliente.get("/api/validacion").json()
    assert len(filas) == len(servicio.VALIDACION)
    for fila in filas:
        assert abs(fila["diferencia_pct"]) <= 1.1, fila


def test_los_ejemplos_son_los_de_la_carpeta_casos(cliente):
    nombres = cliente.get("/api/ejemplos").json()
    assert "casa_rural" in nombres
    assert cliente.get("/api/ejemplos/casa_rural").json() == CASA_RURAL
    assert cliente.get("/api/ejemplos/..%2Fapp").status_code == 404


def test_un_caso_con_un_campo_desconocido_se_rechaza_con_el_motivo(cliente):
    malo = {**CASA_RURAL, "estructura": {**CASA_RURAL["estructura"], "altura": 3}}
    respuesta = cliente.post("/api/evaluar", json=malo)
    assert respuesta.status_code == 422
    assert "altura" in respuesta.json()["detail"]


@pytest.mark.parametrize("cambio, palabra", [
    ({"N_G": 0}, "N_G"),
    ({"N_G": "mucho"}, "N_G"),
    ({"zonas": []}, "zona"),
    ({"tipos": [7]}, "1, 2, 3 o 4"),
    ({"emplazamiento": {"modo": "declarado", "fuente": ""}}, "fuente"),
])
def test_casos_invalidos(cliente, cambio, palabra):
    respuesta = cliente.post("/api/evaluar", json={**CASA_RURAL, **cambio})
    assert respuesta.status_code == 422
    assert palabra in respuesta.json()["detail"]


def test_json_roto_y_demasiado_grande(cliente):
    assert cliente.post("/api/evaluar", content=b"{no es json").status_code == 400
    grande = b"[" + b"0," * api.MAX_BYTES + b"0]"
    assert cliente.post("/api/evaluar", content=grande).status_code == 413


def test_riesgo_sin_perdidas_avisa_en_vez_de_cumplir(cliente):
    sin_l2 = {"1": {}, "2": {"L_T": 0, "L_F": 0, "L_O": 0}}
    caso = {**CASA_RURAL, "zonas": [{**z, "perdidas": sin_l2} for z in CASA_RURAL["zonas"]]}
    datos = cliente.post("/api/evaluar", json=caso).json()
    assert "1" in datos["riesgos"]
    assert "2" not in datos["riesgos"]
    assert any(a.startswith("R2") for a in datos["avisos"])


def test_n_g_desde_coordenadas(cliente):
    ficha = cliente.get("/api/ng", params={"lat": 6.25, "lon": -75.56}).json()
    assert ficha["N_G"] > 0
    assert ficha["distancia_km"] < 10


def test_n_g_fuera_de_cobertura(cliente):
    respuesta = cliente.get("/api/ng", params={"lat": 60, "lon": 10})
    assert respuesta.status_code == 422
    assert "cobertura" in respuesta.json()["detail"]


def test_con_coordenadas_el_n_g_lo_pone_el_servidor(cliente):
    caso = {**CASA_RURAL, "N_G": 999,
            "emplazamiento": {"modo": "coordenadas", "lat": 6.25, "lon": -75.56}}
    datos = cliente.post("/api/evaluar", json=caso).json()
    ficha = cliente.get("/api/ng", params={"lat": 6.25, "lon": -75.56}).json()
    assert datos["N_G"] == pytest.approx(ficha["N_G"])


def test_informe_pdf(cliente):
    respuesta = cliente.post("/api/informe?medidas=false",
                             json={"caso": CASA_RURAL, "proyecto": {"Proyecto": "Prueba"}})
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"
    assert respuesta.content.startswith(b"%PDF")


def test_informe_sin_caso(cliente):
    assert cliente.post("/api/informe", json={"proyecto": {}}).status_code == 400


def test_limite_de_peticiones(cliente, monkeypatch):
    monkeypatch.setattr(api, "limite_calculo", Limite(2, 60))
    codigos = [cliente.get("/api/ng", params={"lat": 6, "lon": -75}).status_code
               for _ in range(3)]
    assert codigos == [200, 200, 429]


def test_las_paginas_se_sirven(cliente):
    for pagina in ("/", "/calculadora.html", "/validacion.html", "/citar.html",
                   "/apoyar.html", "/estilos.css", "/calculadora.js"):
        assert cliente.get(pagina).status_code == 200, pagina


def test_el_limite_se_libera_con_el_tiempo():
    ahora = [0.0]
    limite = Limite(1, 60, reloj=lambda: ahora[0])
    assert limite.permitir("a")
    assert not limite.permitir("a")
    assert limite.permitir("b")
    ahora[0] = 61
    assert limite.permitir("a")
