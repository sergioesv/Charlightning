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


def test_si_no_se_buscaron_medidas_de_un_riesgo_que_no_cumple_se_dice(caso):
    texto = _texto(_armar(caso, soluciones=None))
    assert "No se buscaron medidas de protección para R<sub>1</sub>" in texto


def test_un_riesgo_que_cumple_no_tiene_seccion_de_medidas(caso):
    from dataclasses import replace
    protegido = {**caso, "zonas": [replace(z, n_z=0.001) for z in caso["zonas"]]}
    assert "Medidas de protección para" not in _texto(_armar(protegido))


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


# ---------------------------------------------------------------------------
# Las medidas de CADA riesgo que no cumple
# ---------------------------------------------------------------------------

def _cuatro_riesgos(caso):
    from dataclasses import replace
    z = caso["zonas"][0]
    zonas = {1: z, 2: replace(z, L_F=0.1, L_O=0.01), 3: replace(z, c_z=20.0, L_F=0.1),
             4: replace(z, L_F=0.1, L_O=0.01, c_b=60.0, c_c=30.0, c_s=10.0)}
    estructura = replace(caso["estructura"], c_t=100.0)
    casos_ = {t: {**caso, "estructura": estructura, "zonas": [zonas[t]]} for t in zonas}
    por_tipo = {t: riesgos.evaluar(estructura, caso["lineas"], [zonas[t]], caso["N_G"],
                                   tipos=(t,))[t] for t in zonas}
    return casos_, por_tipo


def test_cada_riesgo_que_no_cumple_tiene_su_tabla_de_medidas(caso):
    casos_, por_tipo = _cuatro_riesgos(caso)
    incumplen = [t for t, r in por_tipo.items() if not r["cumple"]]
    assert incumplen == [1, 2, 4]
    soluciones = {t: medidas.explorar(casos_[t]["estructura"], caso["lineas"],
                                      casos_[t]["zonas"], caso["N_G"], tipo=t)
                  for t in incumplen}

    documento = armado.armar(casos_, por_tipo, soluciones=soluciones)
    titulos = [b.texto for b in documento.bloques if isinstance(b, d.Titulo)]

    for t in incumplen:
        assert f"Medidas de protección para R<sub>{t}</sub>" in titulos
        primera = soluciones[t][0].riesgo
        assert armado.cientifico(primera) in _texto(documento)
    assert "Medidas de protección para R<sub>3</sub>" not in titulos      # R3 cumple


def test_la_conclusion_habla_de_cada_riesgo_que_no_cumple(caso):
    casos_, por_tipo = _cuatro_riesgos(caso)
    documento = armado.armar(casos_, por_tipo, soluciones={1: [], 2: None})
    conclusion = [b.texto for b in documento.bloques
                  if isinstance(b, d.Parrafo) and re.match(r"R<sub>\d</sub> = ", b.texto)]
    assert [t.split(" ")[0] for t in conclusion] == [
        "R<sub>1</sub>", "R<sub>2</sub>", "R<sub>4</sub>"]
    assert "Ninguna combinación" in conclusion[0]


def test_las_figuras_del_veredicto_se_numeran_en_orden(caso, tmp_path):
    casos_, por_tipo = _cuatro_riesgos(caso)
    figura = tmp_path / "v.png"
    figura.write_bytes(b"x")
    documento = armado.armar(
        casos_, por_tipo, soluciones={1: [], 2: []},
        figuras={"veredicto": {1: str(figura), 2: str(figura)}})
    pies = [b.pie for b in documento.bloques if isinstance(b, d.Figura)]
    assert pies == []           # con soluciones vacías no hay figura que poner


def test_el_informe_de_los_cuatro_riesgos_se_dibuja_sin_advertencias(caso, tmp_path):
    casos_, por_tipo = _cuatro_riesgos(caso)
    soluciones = {t: medidas.explorar(casos_[t]["estructura"], caso["lineas"],
                                      casos_[t]["zonas"], caso["N_G"], tipo=t)
                  for t in (1, 2, 4)}
    documento = armado.armar(casos_, por_tipo, soluciones=soluciones)
    resultado = pdf.dibujar(documento, str(tmp_path / "cuatro.pdf"))
    assert resultado.advertencias == []


def test_el_porcentaje_que_mitiga_sale_del_riesgo_sin_medidas(caso):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    base = _por_tipo(caso)[1]["total"]
    texto = _texto(_armar(caso, soluciones=soluciones))
    primera = soluciones[0]
    esperado = armado._reduccion(base, primera.riesgo)
    assert esperado in texto
    assert esperado == "95,9 %"                     # 1 - 1,032e-6 / 2,506e-5


@pytest.mark.parametrize("base, riesgo, esperado", [
    (100.0, 25.0, "75,0 %"), (100.0, 0.05, "99,950 %"), (0.0, 1.0, "—")])
def test_reduccion_muestra_mas_decimales_cerca_del_cien(base, riesgo, esperado):
    assert armado._reduccion(base, riesgo) == esperado


# ---------------------------------------------------------------------------
# Las tres formas de la tabla de medidas
# ---------------------------------------------------------------------------

def _combinacion(caso, *nombres):
    catalogo = {m.nombre: m for m in medidas.catalogo()}
    return tuple(catalogo[n] for n in nombres)


def test_el_factor_que_cambia_sale_de_comparar_el_caso_antes_y_despues(caso):
    dps = armado.factores_que_cambian(caso, _combinacion(caso, "dps:npr_III_IV"))
    fuego = armado.factores_que_cambian(
        caso, _combinacion(caso, "incendio:extincion_o_alarma_automatica"))
    assert dps == "P<sub>EB</sub>: de 1 a 0,05<br/>P<sub>DPS</sub>: de 1 a 0,05"
    assert fuego == "r<sub>p</sub>: de 1 a 0,2"


def test_una_combinacion_lista_todos_sus_factores(caso):
    texto = armado.factores_que_cambian(caso, _combinacion(
        caso, "dps:npr_III_IV", "incendio:extincion_o_alarma_automatica"))
    assert "P<sub>EB</sub>: de 1 a 0,05" in texto and "r<sub>p</sub>: de 1 a 0,2" in texto


def test_sin_medidas_no_cambia_ningun_factor(caso):
    assert armado.factores_que_cambian(caso, ()) == "—"


def test_la_forma_con_factor_agrega_la_columna(caso):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    documento = _armar(caso, soluciones=soluciones, medidas_como="con_factor")
    tablas = [b for b in documento.bloques if isinstance(b, d.Tabla)]
    tabla = next(t for t in tablas if "Factor que cambia" in t.filas[0])
    assert tabla.filas[0][:3] == ["N.º", "Medidas", "Factor que cambia"]
    assert any("P<sub>EB</sub>: de 1 a 0,05" in fila[2] for fila in tabla.filas[1:])
    assert sum(tabla.anchos) == pytest.approx(166)


def test_la_forma_solo_porcentaje_no_trae_el_riesgo_resultante(caso):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    documento = _armar(caso, soluciones=soluciones, medidas_como="solo_porcentaje")
    tabla = next(b for b in documento.bloques
                 if isinstance(b, d.Tabla) and "Reduce" in b.filas[0])
    assert tabla.filas[0] == ["N.º", "Medidas", "Reduce"]
    assert sum(tabla.anchos) == pytest.approx(166)
    assert tabla.derecha == (2,)


def test_una_forma_desconocida_se_rechaza(caso):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    with pytest.raises(ValueError):
        _armar(caso, soluciones=soluciones, medidas_como="rara")


@pytest.mark.parametrize("forma", ["completa", "con_factor", "solo_porcentaje"])
def test_las_tres_formas_se_dibujan_sin_advertencias(caso, tmp_path, forma):
    soluciones = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                  caso["N_G"], tipo=1)
    documento = _armar(caso, soluciones=soluciones, medidas_como=forma)
    resultado = pdf.dibujar(documento, str(tmp_path / f"{forma}.pdf"))
    assert resultado.advertencias == []

def test_el_titulo_de_la_norma_es_el_de_su_portada(caso):
    documento = _armar(caso)
    assert documento.subtitulo == ("NTC 4552-2:2023 — Protección contra el rayo. "
                                   "Parte 2: Evaluación del riesgo")
    assert "Protección contra el rayo. Parte 2: Evaluación del riesgo" in _texto(documento)
    assert "descargas eléctricas atmosféricas (rayos)" not in _texto(documento)



# ---------------------------------------------------------------------------
# Paso 61b: lo que la estructura YA tiene, y la protección de cada línea
# ---------------------------------------------------------------------------

def _caso_con(caso, *nombres):
    """El caso con esas medidas del catálogo ya instaladas."""
    e, l, z = medidas.aplicar(caso["estructura"], caso["lineas"], caso["zonas"],
                              _combinacion(caso, *nombres))
    return dict(caso, estructura=e, lineas=l, zonas=z)


def _tabla_de_adoptadas(documento):
    return next((b for b in documento.bloques
                 if isinstance(b, d.Tabla) and b.filas[0][0] == "Dónde"), None)


def test_la_tabla_de_lineas_trae_C_LD_C_LI_y_P_EB(caso):
    tabla = next(b for b in _armar(caso).bloques
                 if isinstance(b, d.Tabla) and "P<sub>EB</sub>" in b.filas[0])
    assert tabla.filas[0] == ["Línea", "U<sub>W</sub> [kV]", "P<sub>LD</sub>",
                              "P<sub>LI</sub>", "C<sub>LD</sub>", "C<sub>LI</sub>",
                              "P<sub>EB</sub>"]
    assert len(tabla.filas) == 1 + len(caso["lineas"])
    assert sum(tabla.anchos) == pytest.approx(166)


def test_la_casa_rural_solo_tiene_adoptado_el_cableado_de_potencia(caso):
    # Es el caso SIN medidas; lo único que no es la peor fila es K_S3 = 0,2.
    tabla = _tabla_de_adoptadas(_armar(caso))
    assert len(tabla.filas) == 2
    assert "Cable sin blindar, evitando bucles grandes" in tabla.filas[1][2]
    assert tabla.filas[1][3] == "K<sub>S3</sub> = 0,2"


def test_sin_ninguna_medida_el_informe_lo_dice(caso):
    from dataclasses import replace

    zonas = [replace(z, sistemas_internos=[replace(si, K_S3=1.0) for si in z.sistemas_internos])
             for z in caso["zonas"]]
    documento = _armar(dict(caso, zonas=zonas))
    assert _tabla_de_adoptadas(documento) is None
    assert "no tiene ninguna medida de protección" in _texto(documento)


def test_las_medidas_instaladas_salen_con_su_fila_y_su_factor(caso):
    protegido = _caso_con(caso, "spcr:spcr_nivel_IV", "dps:npr_III_IV")
    tabla = _tabla_de_adoptadas(armado.armar({1: protegido}, _por_tipo(protegido)))
    filas = [" | ".join(f) for f in tabla.filas[1:]]
    assert any("SPCR de nivel IV" in f and "P<sub>B</sub> = 0,2" in f for f in filas)
    assert any("DPS de NPR III-IV" in f and "P<sub>EB</sub> = 0,05" in f for f in filas)
    assert any("DPS de NPR III-IV" in f and "P<sub>DPS</sub> = 0,05" in f for f in filas)


def test_el_blindaje_se_nombra_con_la_fila_de_su_tipo_de_linea(caso):
    # La Tabla B.4 da el mismo C_LD y C_LI a la línea aérea y a la subterránea:
    # el informe elige la que corresponde a cómo va instalada cada una (C_I).
    protegido = _caso_con(caso, "blindaje_linea:subterranea_apantallada_conectada_barra")
    tabla = _tabla_de_adoptadas(armado.armar({1: protegido}, _por_tipo(protegido)))
    por_linea = {f[0]: f[2] for f in tabla.filas[1:] if "Tabla B.4" in f[1]}
    assert por_linea["potencia"].startswith("Subterránea apantallada")     # enterrada
    assert por_linea["telecomunicacion"].startswith("Aérea apantallada")    # aérea


def test_un_valor_que_no_es_fila_de_la_tabla_se_declara(caso):
    from dataclasses import replace

    # El hospital del E.4 usa P_DPS = 0,002: la Tabla B.3 da un rango (0,005-0,001).
    zonas = [replace(z, sistemas_internos=[replace(si, P_DPS=0.002) for si in z.sistemas_internos])
             for z in caso["zonas"]]
    tabla = _tabla_de_adoptadas(_armar(dict(caso, zonas=zonas)))
    assert any(f[2] == "Valor declarado" and f[3] == "P<sub>DPS</sub> = 0,002"
               for f in tabla.filas[1:])