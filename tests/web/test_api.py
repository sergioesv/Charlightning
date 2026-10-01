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


def test_riesgo_sin_perdidas_no_se_calcula(cliente):
    """Como en el programa: R2 sin pérdidas daría 0 y «Cumple» sin haber evaluado nada."""
    sin_l2 = {"1": {}, "2": {"L_T": 0, "L_F": 0, "L_O": 0}}
    caso = {**CASA_RURAL, "zonas": [{**z, "perdidas": sin_l2} for z in CASA_RURAL["zonas"]]}
    respuesta = cliente.post("/api/evaluar", json=caso)
    assert respuesta.status_code == 422
    assert "R2 no tiene pérdidas cargadas" in respuesta.json()["detail"]


def test_el_esquema_trae_las_tablas_de_la_norma(cliente):
    esquema = cliente.get("/api/esquema").json()
    cd = esquema["tablas"]["CD"]
    assert cd["nombre"].startswith("Tabla A.1")
    assert {"llave": "aislada", "texto": "Aislada, sin otros objetos cerca", "valor": 1} in cd["opciones"]
    assert esquema["tablas"]["CLD_CLI"]["opciones"][0]["valor"] == {"CLD": 1, "CLI": 1}
    pli = {o["llave"]: o["valores"] for o in esquema["doble_entrada"]["PLI"]["opciones"]}
    assert pli["potencia"]["2.5"] == 0.3
    assert esquema["tensiones"] == [1, 1.5, 2.5, 4, 6]
    assert esquema["por_defecto"]["Zona"]["t_z"] == 8760


def test_abrir_un_caso_lo_deja_listo_para_los_formularios(cliente):
    abierto = cliente.post("/api/abrir", json=servicio.ejemplo("E3_oficinas")).json()
    caso = abierto["por_tipo"]["1"]
    assert [z["nombre"] for z in caso["zonas"]] == ["Z1", "Z2", "Z3", "Z4", "Z5"]
    assert caso["lineas"][1]["P_LI"] == 0.5
    assert caso["emplazamiento"]["modo"] == "declarado"


def test_lo_que_guarda_la_web_se_calcula_igual(cliente):
    """El formato que arma la calculadora (pérdidas por riesgo) da lo mismo."""
    abierto = cliente.post("/api/abrir", json=CASA_RURAL).json()["por_tipo"]["1"]
    perdidas = ("L_T", "L_F", "L_O", "h_z", "L_FE", "t_e")
    zonas = [{**{k: v for k, v in z.items() if k not in perdidas},
              "perdidas": {"1": {k: z[k] for k in perdidas}}} for z in abierto["zonas"]]
    caso = {"N_G": abierto["N_G"], "emplazamiento": abierto["emplazamiento"], "tipos": [1],
            "estructura": abierto["estructura"], "lineas": abierto["lineas"], "zonas": zonas}
    datos = cliente.post("/api/evaluar", json=caso).json()
    assert datos["riesgos"]["1"]["total"] == pytest.approx(2.51e-5, rel=0.01)


def test_de_donde_viene_el_riesgo(cliente):
    d = cliente.post("/api/desglose?tipo=1", json=CASA_RURAL).json()
    assert d["aportes"][0]["componente"] == "R_V"
    assert d["aportes"][0]["texto"].startswith("R_V - ")
    assert any(r["cumple"] for r in d["aportes"][0]["rebajas"])
    assert cliente.post("/api/desglose?tipo=3", json=CASA_RURAL).status_code == 422


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
    for pagina in ("/", "/calculadora.html", "/acerca.html", "/validacion.html", "/citar.html",
                   "/apoyar.html", "/contacto.html", "/estilos.css", "/calculadora.js", "/campos.js",
                   "/formularios.js"):
        assert cliente.get(pagina).status_code == 200, pagina


def test_el_limite_se_libera_con_el_tiempo():
    ahora = [0.0]
    limite = Limite(1, 60, reloj=lambda: ahora[0])
    assert limite.permitir("a")
    assert not limite.permitir("a")
    assert limite.permitir("b")
    ahora[0] = 61
    assert limite.permitir("a")


def test_contador_de_visitas(tmp_path):
    from web.contador import Contador
    contador = Contador(tmp_path / "sub" / "visitas.json")
    assert contador.leer() == 0
    assert [contador.sumar() for _ in range(3)] == [1, 2, 3]
    assert Contador(tmp_path / "sub" / "visitas.json").leer() == 3


def test_contador_por_la_api(cliente, monkeypatch, tmp_path):
    from web.contador import Contador
    monkeypatch.setattr(api, "contador", Contador(tmp_path / "visitas.json"))
    assert cliente.get("/api/visitas").json() == {"visitas": 0}
    assert cliente.post("/api/visitas").json() == {"visitas": 1}
    assert cliente.get("/api/visitas").json() == {"visitas": 1}


def test_contacto_guarda_y_envia(tmp_path):
    from web.contacto import Buzon
    enviados = []
    buzon = Buzon(tmp_path / "mensajes.jsonl", destino="autor@ejemplo.org", clave="x",
                  enviar=lambda clave, destino, m: enviados.append((destino, m)) or True)
    assert buzon.recibir({"nombre": "Ana", "correo": "ana@ejemplo.org", "mensaje": "Hola"})
    assert enviados[0][0] == "autor@ejemplo.org"
    assert "Hola" in (tmp_path / "mensajes.jsonl").read_text(encoding="utf-8")


def test_contacto_sin_configurar_solo_guarda(tmp_path):
    from web.contacto import Buzon
    buzon = Buzon(tmp_path / "mensajes.jsonl")
    assert buzon.recibir({"nombre": "Ana", "mensaje": "Hola"}) is False
    assert (tmp_path / "mensajes.jsonl").exists()


def test_contacto_por_la_api(cliente, monkeypatch, tmp_path):
    from web.contacto import Buzon
    monkeypatch.setattr(api, "buzon", Buzon(tmp_path / "m.jsonl"))
    monkeypatch.setattr(api, "limite_contacto", Limite(2, 600))
    assert cliente.post("/api/contacto", json={"nombre": "", "mensaje": "x"}).status_code == 422
    assert cliente.post("/api/contacto", json={"nombre": "A", "correo": "malo", "mensaje": "x"}).status_code == 422
    # El robot que llena el campo trampa recibe «enviado» y no se guarda nada.
    assert cliente.post("/api/contacto", json={"nombre": "R", "mensaje": "spam",
                                               "sitio_web": "http://spam"}).json() == {"enviado": True}
    assert not (tmp_path / "m.jsonl").exists()
    assert cliente.post("/api/contacto", json={"nombre": "A", "mensaje": "x"}).status_code == 429


def test_el_contador_no_baja_del_minimo(tmp_path, monkeypatch):
    from web.contador import Contador
    monkeypatch.setenv("CONTADOR_MINIMO", "57")
    contador = Contador(tmp_path / "visitas.json")
    assert contador.leer() == 57
    assert contador.sumar() == 58


def test_los_archivos_van_con_su_version(cliente):
    """La página nueva nunca se mezcla con una hoja de estilos vieja guardada en caché."""
    html = cliente.get("/").text
    import re
    css = re.search(r'href="(/estilos\.css\?v=\w+)"', html).group(1)
    assert cliente.get("/").headers["cache-control"] == "no-cache"
    assert "immutable" in cliente.get(css).headers["cache-control"]
    js = cliente.get(re.search(r'src="(/calculadora\.js\?v=\w+)"', html).group(1)).text
    assert re.search(r'from "\./campos\.js\?v=\w+"', js)
    assert cliente.get("/estilos.css").headers["cache-control"] == "no-cache"
