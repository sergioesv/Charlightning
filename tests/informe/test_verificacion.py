"""
Trazabilidad de las memorias: el registro que se guarda, el código y el QR que se imprimen.

Vigilan que el registro NO lleve datos personales, que la huella cambie con los datos, y que
el PDF con verificación salga completo (portada, cajetín dual, QR) sin advertencias.
"""
import dataclasses
import re
from dataclasses import replace
from datetime import datetime, timezone

import pytest

pytest.importorskip("reportlab")

from calculate_risk.informe import armado, pdf, verificacion         # noqa: E402
from calculate_risk.informe import documento as d                     # noqa: E402
from calculate_risk.norma import casos, riesgos                       # noqa: E402
from calculate_risk.norma.modelo import Emplazamiento                 # noqa: E402

AHORA = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def datos():
    caso = casos.cargar_caso("casos/casa_rural.json")
    por_tipo = {1: riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                                   caso["N_G"], tipos=(1,))[1]}
    return {1: caso}, por_tipo


def test_el_registro_tiene_el_formato_y_nada_personal(datos):
    por_caso, por_tipo = datos
    registro = verificacion.registro_de(por_caso, por_tipo, AHORA)
    assert re.fullmatch(r"CHL-2026-[0-9A-F]{6}", registro.id)
    assert registro.created_at.startswith("2026-10-08T12:00:00")
    assert registro.verdict == "NO CUMPLE" and registro.risk_r1 == por_tipo[1]["total"]
    assert {f.name for f in dataclasses.fields(registro)} == {
        "id", "created_at", "coordinates", "risk_r1", "verdict", "data_hash", "engine_version"}


def test_la_huella_es_estable_y_cambia_con_cualquier_dato(datos):
    por_caso, por_tipo = datos
    huella = verificacion.huella_de(por_caso, por_tipo)
    assert verificacion.huella_de(por_caso, por_tipo) == huella
    estructura = replace(por_caso[1]["estructura"], H=por_caso[1]["estructura"].H + 1)
    otro = {1: {**por_caso[1], "estructura": estructura}}
    assert verificacion.huella_de(otro, por_tipo) != huella


def test_las_coordenadas_se_redondean(datos):
    por_caso, por_tipo = datos
    emplazamiento = Emplazamiento(modo="coordenadas", lat=5.69234, lon=-76.65811)
    con_sitio = {1: {**por_caso[1], "emplazamiento": emplazamiento}}
    assert verificacion.registro_de(con_sitio, por_tipo, AHORA).coordinates == "5.69,-76.66"
    assert verificacion.registro_de(por_caso, por_tipo, AHORA).coordinates == ""


def test_lo_que_se_imprime_es_el_codigo_el_enlace_y_el_comienzo_de_la_huella(datos):
    registro = verificacion.registro_de(*datos, AHORA)
    impreso = registro.impreso()
    assert impreso.url == f"https://charlightning.org/verify/{registro.id}"
    assert impreso.huella == registro.data_hash[:10].upper()


def _armar(datos, **nombrados):
    por_caso, por_tipo = datos
    return armado.armar(por_caso, por_tipo, proyecto={"Proyecto": "Prueba", "Diseñador": "Ana Pérez",
                                                      "Matrícula profesional": "CN-123"},
                        **nombrados)


def test_el_documento_trae_la_marca_el_cajetin_y_el_veredicto_en_la_portada(datos):
    registro = verificacion.registro_de(*datos, AHORA)
    documento = _armar(datos, verificacion=registro)
    assert documento.verificacion.id == registro.id
    assert "Sergio A. Estrada Vélez" in documento.encabezado_izq
    assert "Charlightning v" in documento.pie and "charlightning.org" in documento.pie
    assert "Sergio Andrés Estrada Vélez" in documento.credito
    portada = [b for b in documento.portada if isinstance(b, d.Recuadro)]
    assert len(portada) == 1 and "NO CUMPLE" in portada[0].etiqueta
    firma = next(b for b in documento.bloques if isinstance(b, d.Firma))
    assert firma.proyectista == "Ana Pérez" and firma.matricula == "CN-123"
    assert "Sergio Andrés Estrada Vélez" in firma.autoria and registro.id in firma.sello


def test_sin_registro_no_hay_qr_ni_codigo(datos):
    documento = _armar(datos)
    assert documento.verificacion is None
    firma = next(b for b in documento.bloques if isinstance(b, d.Firma))
    assert "CHL-" not in firma.sello


def test_el_pdf_con_verificacion_sale_sin_advertencias(datos, tmp_path):
    documento = _armar(datos, verificacion=verificacion.registro_de(*datos, AHORA))
    resultado = pdf.dibujar(documento, str(tmp_path / "memoria.pdf"))
    assert resultado.advertencias == []
    contenido = (tmp_path / "memoria.pdf").read_bytes()
    assert contenido.startswith(b"%PDF") and resultado.paginas >= 3
