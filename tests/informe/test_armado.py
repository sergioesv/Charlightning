"""
Paso 61a: el informe armado desde el caso.

Vigilan tres cosas: que los números del informe sean los del motor (los mismos que ve el
panel), que N_G nunca aparezca sin su procedencia, y que el documento completo se dibuje
sin advertencias. No necesitan pantalla gráfica.
"""
import re
from datetime import date
from pathlib import Path

import pytest

pytest.importorskip("reportlab")

from calculate_risk.informe import armado                      # noqa: E402
from calculate_risk.informe import documento as d              # noqa: E402
from calculate_risk.informe import pdf                          # noqa: E402
from calculate_risk.norma import casos, medidas, riesgos        # noqa: E402
from calculate_risk.norma.modelo import Emplazamiento           # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


def _por_tipo(caso, tipos=(1,)):
    return {t: riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                               caso["N_G"], tipos=(t,))[t] for t in tipos}


def _texto(documento) -> str:
    """Todo el texto del documento, en un solo string, para buscar en él."""
    trozos = [documento.titulo, documento.subtitulo]
    for bloque in documento.portada + documento.bloques:
        if isinstance(bloque, (d.Titulo, d.Parrafo, d.Recuadro)):
            trozos.append(getattr(bloque, "texto"))
        elif isinstance(bloque, d.Formula):
            trozos.append(bloque.tex)
        elif isinstance(bloque, d.Tabla):
            trozos += [celda for fila in bloque.filas for celda in fila]
        elif isinstance(bloque, d.Figura):
            trozos.append(bloque.pie)
    return "\n".join(str(t) for t in trozos)


def _armar(caso, **nombrados):
    return armado.armar({1: caso}, _por_tipo(caso), **nombrados)


# ---------------------------------------------------------------------------
# El formato solo presenta
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("valor, esperado", [
    (2.5056e-5, "2,506 × 10<super>-5</super>"),
    (1e-5, "1 × 10<super>-5</super>"),
    (0.5, "5 × 10<super>-1</super>"),
    (2.0, "2"),
    (0, "0"),
])
def test_cientifico_usa_coma_y_no_deja_ceros_de_mas(valor, esperado):
    assert armado.cientifico(valor) == esperado


def test_la_notacion_de_las_formulas_es_la_misma_con_otra_sintaxis():
    assert armado.tex_cientifico(2.5056e-5) == "2{,}506 \\times 10^{-5}"


@pytest.mark.parametrize("valor, esperado", [
    (15, "15"), (0.5, "0,5"), (2577.88, "2&nbsp;577,88"), (100, "100"), (0, "0"),
])
def test_plano_no_come_ceros_ni_usa_punto_decimal(valor, esperado):
    assert armado.plano(valor, 2) == esperado


def test_corriente_deja_un_factor_normal_como_esta():
    assert armado.corriente(0.5) == "0,5"
    assert armado.corriente(1) == "1"
    assert armado.corriente(1e-5) == "1 × 10<super>-5</super>"


def test_la_fecha_sale_en_espanol():
    assert armado.fecha_larga(date(2026, 9, 28)) == "28 de septiembre de 2026"


# ---------------------------------------------------------------------------
# La estructura del informe
# ---------------------------------------------------------------------------

def test_hay_ocho_secciones_en_orden(caso):
    assert _armar(caso).secciones() == [
        "1. Alcance y base normativa",
        "2. Términos, responsabilidad y notación",
        "3. Emplazamiento y densidad de descargas",
        "4. Datos de la estructura, las zonas y las líneas",
        "5. Frecuencia de impactos y componentes del riesgo",
        "6. Veredicto y medidas de protección",
        "7. Conclusión y firma",
        "8. Referencias",
    ]


def test_el_documento_tiene_contenido_y_portada(caso):
    documento = _armar(caso, proyecto={"Proyecto": "Casa", "Diseñador": "Ana"})
    assert any(isinstance(b, d.Contenido) for b in documento.bloques)
    assert documento.autor == "Ana"
    assert documento.encabezado_der == "Casa"


# ---------------------------------------------------------------------------
# Los números son los del motor
# ---------------------------------------------------------------------------

def test_el_riesgo_calculado_es_el_del_motor(caso):
    por_tipo = _por_tipo(caso)
    texto = _texto(_armar(caso))
    assert armado.cientifico(por_tipo[1]["total"]) in texto
    assert armado.cientifico(por_tipo[1]["R_T"]) in texto


def test_la_tabla_de_componentes_trae_cada_componente_del_motor(caso):
    por_tipo = _por_tipo(caso)
    texto = _texto(_armar(caso))
    for componente in riesgos.COMPONENTES:
        valor = por_tipo[1][componente]
        if valor:
            assert armado.cientifico(valor) in texto


def test_el_desarrollo_multiplica_los_mismos_tres_factores(caso):
    por_tipo = _por_tipo(caso)
    zona = next(iter(por_tipo[1]["zonas"].values()))
    formulas = [b.tex for b in _armar(caso).bloques if isinstance(b, d.Formula)]
    esperado = armado.tex_cientifico(zona["R_B"])
    assert any(f.endswith(f"\\mathbf{{{esperado}}}") and "R_{B}" in f for f in formulas)


def test_las_participaciones_suman_cien(caso):
    aportes = armado.aportes_de(_por_tipo(caso)[1])
    assert sum(pct for _, _, pct in aportes) == pytest.approx(100.0)
    assert [v for _, v, _ in aportes] == sorted((v for _, v, _ in aportes), reverse=True)


def test_un_caso_sin_lineas_lo_dice(caso):
    sin_lineas = {**caso, "lineas": []}
    assert "no tiene líneas de servicio" in _texto(_armar(sin_lineas))


# ---------------------------------------------------------------------------
# N_G nunca viaja sin su procedencia
# ---------------------------------------------------------------------------

def test_declarado_imprime_la_fuente_y_la_escapa(caso):
    caso = {**caso, "emplazamiento": Emplazamiento(
        modo="declarado", fuente="Red local <IDEAM> & Cía")}
    texto = _texto(_armar(caso))
    assert "declarada por el diseñador" in texto
    assert "Red local &lt;IDEAM&gt; &amp; Cía" in texto


def test_declarado_sin_fuente_lo_avisa_en_vez_de_callar(caso):
    caso = {**caso, "emplazamiento": Emplazamiento(modo="declarado", fuente="")}
    assert "no se indicó fuente" in _texto(_armar(caso))


def test_un_caso_viejo_sin_emplazamiento_pide_documentar_la_fuente(caso):
    caso = {**caso, "emplazamiento": None}
    assert "no registra de dónde sale" in _texto(_armar(caso))


def test_por_coordenadas_sin_ficha_no_inventa_la_ficha(caso):
    caso = {**caso, "emplazamiento": Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)}
    texto = _texto(_armar(caso))
    assert "no se pudo leer la ficha" in texto
    assert "Celda de la grilla" not in texto


def test_por_coordenadas_con_ficha_imprime_todo_lo_que_hace_falta_para_reproducirla(caso):
    pytest.importorskip("netCDF4")
    from calculate_risk.norma import densidad
    ficha = densidad.ficha_desde_lat_lon(2.44, -76.61)
    caso = {**caso, "N_G": ficha.N_G,
            "emplazamiento": Emplazamiento(modo="coordenadas", lat=2.44, lon=-76.61)}
    texto = _texto(_armar(caso, ficha=ficha))
    for esperado in ("Tropical Rainfall Measuring Mission", "2,450° N", "76,650° O",
                     "4,6 km", "11,64", "158 h", "0,227", "Z = 3,4", "2,643",
                     "adoptado por el diseñador"):
        assert esperado in texto, esperado
    assert "doi:10.5067/LIS/LIS/DATA301" in texto        # las referencias del dato


def test_las_referencias_de_la_nasa_solo_salen_si_se_uso_la_nasa(caso):
    assert "LIS/LIS/DATA301" not in _texto(_armar(caso))
    assert "ICONTEC" in _texto(_armar(caso))


# ---------------------------------------------------------------------------
# Veredicto, medidas y conclusión salen de los números
# ---------------------------------------------------------------------------

def test_el_recuadro_es_naranja_si_no_cumple(caso):
    recuadros = [b for b in _armar(caso).bloques if isinstance(b, d.Recuadro)]
    assert len(recuadros) == 1 and recuadros[0].cumple is False
    assert "NO CUMPLE" in recuadros[0].texto


def test_el_recuadro_es_azul_si_cumple(caso):
    from dataclasses import replace
    protegido = {**caso, "zonas": [replace(z, n_z=0.001) for z in caso["zonas"]]}
    documento = _armar(protegido)
    recuadro = next(b for b in documento.bloques if isinstance(b, d.Recuadro))
    assert recuadro.cumple is True
    assert "cumple" in _texto(documento)


def test_sin_soluciones_pedidas_no_hay_seccion_de_medidas(caso):
    assert "Medidas de protección para" not in _texto(_armar(caso, soluciones=None))


def test_si_no_hay_ninguna_combinacion_que_baste_se_dice(caso):
    assert "Ninguna combinación de las medidas contempladas" in _texto(
        _armar(caso, soluciones=[]))


def test_las_medidas_salen_con_nombre_legible_y_sin_costo_si_no_hay_precios(caso):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    texto = _texto(_armar(caso, soluciones=soluciones))
    assert "(Tabla B." in texto
    assert "blindaje_linea:" not in texto
    assert "no se cargaron costos" in texto
    assert "Costo" not in texto


def test_la_conclusion_nombra_el_componente_dominante(caso):
    por_tipo = _por_tipo(caso)
    componente, _, pct = armado.aportes_de(por_tipo[1])[0]
    texto = _texto(_armar(caso))
    assert f"{armado.coma(pct, 1)} %" in texto
    assert armado._sub(componente) in texto


# ---------------------------------------------------------------------------
# Varias zonas y varios riesgos
# ---------------------------------------------------------------------------

def test_con_dos_zonas_avisa_cual_se_desarrolla_y_que_el_total_las_suma(caso):
    from dataclasses import replace
    original = caso["zonas"][0]
    partido = {**caso, "zonas": [replace(original, nombre="planta_baja", n_z=2),
                                 replace(original, nombre="planta_alta", n_z=3)]}
    texto = _texto(_armar(partido))
    assert "planta_baja" in texto and "suma las 2 zonas" in texto


def test_con_los_cuatro_riesgos_todos_tienen_su_fila(caso):
    casos_por_tipo = {t: caso for t in (1, 2, 3, 4)}
    documento = armado.armar(casos_por_tipo, _por_tipo(caso, (1, 2, 3, 4)))
    texto = _texto(documento)
    for nombre in armado.NOMBRES_RIESGOS.values():
        assert nombre in texto


# ---------------------------------------------------------------------------
# El documento se dibuja completo y sin avisos
# ---------------------------------------------------------------------------

def test_el_informe_completo_se_dibuja_sin_advertencias(caso, tmp_path):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    documento = _armar(
        caso, proyecto={"Proyecto": "Vivienda & Cía", "Diseñador": "Sergio Estrada",
                        "Dirección": "Popayán", "Teléfono": ""},
        soluciones=soluciones, fecha=date(2026, 9, 28))

    resultado = pdf.dibujar(documento, str(tmp_path / "informe.pdf"))

    assert resultado.advertencias == []
    assert resultado.paginas >= 4
    assert [t for t, _ in resultado.secciones] == documento.secciones()
    assert Path(resultado.ruta).stat().st_size > 5000


def test_el_pdf_no_contiene_cuadros_negros_por_subindices(caso, tmp_path):
    resultado = pdf.dibujar(_armar(caso), str(tmp_path / "i.pdf"))
    assert not re.search(r"[₀-₉²³¹]", _texto(_armar(caso)))
    assert resultado.advertencias == []