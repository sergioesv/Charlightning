"""
Paso 50: la memoria de cálculo desde un caso del modelo.

La memoria del Paso 40 nació leyendo el diccionario plano de la pantalla
vieja, que solo sabía de una zona y una línea. Aquí recibe el caso completo,
así que las tablas de entrada y de áreas ya no suponen nada: hay una fila por
zona y una por línea, y las frecuencias de cada línea salen por separado.

La prueba que cierra el paso compila el PDF de verdad (si hay LaTeX) con un
caso de dos zonas.
"""
import shutil

import pytest
from pytest import approx

from calculate_risk.norma import casos, memoria, riesgos

RUTA_CASA_RURAL = "casos/casa_rural.json"
hay_latex = shutil.which("pdflatex") is not None


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


def _evaluar(caso, tipos=(1,)):
    return {t: riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                               caso["N_G"], tipos=(t,))[t] for t in tipos}


@pytest.fixture
def una_zona(caso):
    return {1: caso}, _evaluar(caso)


@pytest.fixture
def dos_zonas(caso):
    from dataclasses import replace
    original = caso["zonas"][0]
    partido = {**caso, "zonas": [replace(original, nombre="planta_baja", n_z=2),
                                 replace(original, nombre="planta_alta", n_z=3)]}
    return {1: partido}, _evaluar(partido)


# ---------------------------------------------------------------------------
# Las llaves planas: mismo contenido, otro envase
# ---------------------------------------------------------------------------

def test_las_llaves_planas_traen_componentes_totales_y_tolerable(una_zona):
    _, por_tipo = una_zona

    planas = memoria._llaves_planas(por_tipo)

    assert planas["R_1"] == approx(2.506e-5, rel=0.01)
    assert planas["R_T1"] == 1e-5
    assert planas["R_V1"] == por_tipo[1]["R_V"]
    assert sum(planas[f"{c}1"] for c in riesgos.COMPONENTES) == approx(planas["R_1"])


# ---------------------------------------------------------------------------
# El documento
# ---------------------------------------------------------------------------

def test_el_documento_tiene_las_secciones(una_zona):
    tex = memoria.memoria_tex_caso(*una_zona)

    for seccion in ("Datos de entrada", "Áreas de colección",
                    "Componentes de riesgo", "Resultado",
                    "Desarrollo del cálculo"):
        assert seccion in tex, seccion
    assert tex.startswith("\\documentclass")
    assert tex.rstrip().endswith("\\end{document}")


def test_el_veredicto_de_la_casa_rural_es_el_de_la_norma(una_zona):
    tex = memoria.memoria_tex_caso(*una_zona)

    assert memoria.numero(2.506e-5)[:5] in tex
    assert "\\textbf{No cumple}" in tex


def test_hay_una_fila_por_linea_con_sus_frecuencias(una_zona):
    tex = memoria.memoria_tex_caso(*una_zona)

    assert "potencia" in tex and "telecomunicacion" in tex
    assert "$N_{DJ}$ (ec. A.5)" in tex        # la columna existe aunque valga 0


def test_una_estructura_sin_lineas_lo_dice(caso):
    sin_lineas = {**caso, "lineas": []}

    tex = memoria.memoria_tex_caso({1: sin_lineas}, _evaluar(sin_lineas))

    assert "no tiene líneas de servicio conectadas" in tex
    assert "$R_U$, $R_V$, $R_W$ y $R_Z$ no intervienen" in tex


# ---------------------------------------------------------------------------
# Varias zonas: lo que la memoria vieja no podía contar
# ---------------------------------------------------------------------------

def test_con_una_zona_no_se_pone_la_tabla_de_aportes(una_zona):
    tex = memoria.memoria_tex_caso(*una_zona)

    assert "Aporte de cada zona" not in tex
    assert "Zonas (1)" in tex


def test_con_dos_zonas_se_ve_el_aporte_de_cada_una(dos_zonas):
    tex = memoria.memoria_tex_caso(*dos_zonas)

    assert "Zonas (2)" in tex
    assert "Aporte de cada zona" in tex
    assert "planta\\_baja" in tex and "planta\\_alta" in tex


def test_con_dos_zonas_el_desarrollo_dice_cual_esta_desarrollando(dos_zonas):
    tex = memoria.memoria_tex_caso(*dos_zonas)

    assert "Se desarrolla la zona" in tex
    assert "el riesgo total suma las 2 zonas" in tex


def test_partir_la_zona_no_cambia_el_total_del_documento(una_zona, dos_zonas):
    # Misma comprobación que en el editor, pero mirando lo que dice el papel.
    entera = memoria._llaves_planas(una_zona[1])["R_1"]
    partida = memoria._llaves_planas(dos_zonas[1])["R_1"]

    assert partida == approx(entera, rel=1e-9)


# ---------------------------------------------------------------------------
# El texto del usuario sigue sin poder romper el documento
# ---------------------------------------------------------------------------

def test_los_nombres_de_zona_y_linea_se_escapan(caso):
    from dataclasses import replace
    raro = {**caso,
            "zonas": [replace(caso["zonas"][0], nombre="Bodega 50% & Cía_2")],
            "lineas": [replace(caso["lineas"][0], nombre="línea #1")]}

    tex = memoria.memoria_tex_caso({1: raro}, _evaluar(raro))

    assert "Bodega 50\\% \\& Cía\\_2" in tex
    assert "línea \\#1" in tex
    for linea in tex.splitlines():
        assert "%" not in linea.replace("\\%", ""), linea


def test_escribir_deja_el_archivo(tmp_path, una_zona):
    ruta = memoria.escribir_memoria_caso(tmp_path / "m.tex", *una_zona)

    assert open(ruta, encoding="utf-8").read().startswith("\\documentclass")


@pytest.mark.skipif(not hay_latex, reason="pdflatex no está instalado")
def test_un_caso_de_dos_zonas_compila_de_verdad(tmp_path, dos_zonas):
    ruta = memoria.escribir_memoria_caso(
        tmp_path / "m.tex", *dos_zonas,
        proyecto={"Proyecto": "Prueba 100% & Cía"})

    pdf = memoria.compilar(ruta)

    with open(pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"