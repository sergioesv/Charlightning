"""
Paso 40: memoria de calculo en LaTeX.

Lo que se comprueba aqui es lo verificable sin abrir el PDF: que el .tex tenga
las secciones y los valores, que el texto del usuario no pueda romper la
compilacion, y que los numeros salgan en el formato correcto.

La compilacion real a PDF se prueba aparte y solo si hay pdflatex instalado
(en el CI no lo hay, y no vale la pena instalar 400 MB de LaTeX para eso).
"""
import shutil

import pytest
from pytest import approx

from calculate_risk.norma import medidas, memoria
from calculate_risk.norma.adaptador import caso_desde_pantalla, resultados_pantalla
from tests.datos_pantalla import CASA_RURAL

hay_latex = shutil.which("pdflatex") is not None


def _memoria_casa_rural(**kwargs):
    res = resultados_pantalla(CASA_RURAL)
    return memoria.memoria_tex(CASA_RURAL, res, **kwargs)


# ---------------------------------------------------------------------------
# Formato de numeros
# ---------------------------------------------------------------------------

def test_los_riesgos_van_en_notacion_cientifica_con_coma():
    assert memoria.numero(2.506e-5) == "2{,}506 \\times 10^{-5}"
    assert memoria.numero(1e-5) == "1 \\times 10^{-5}"
    assert memoria.numero(0) == "0"


def test_las_magnitudes_normales_no_van_en_cientifica():
    # Poner "1,5 x 10^1" donde dice 15 m solo estorba.
    assert memoria.plano(15) == "15"
    assert memoria.plano(0.5) == "0{,}5"
    assert memoria.plano(2577.876, 2) == "2 577{,}88"


# ---------------------------------------------------------------------------
# Escape: el texto del usuario no puede romper LaTeX
# ---------------------------------------------------------------------------

def test_el_texto_del_usuario_se_escapa():
    assert memoria.escapar("Bodega 50% & Cía_2") == "Bodega 50\\% \\& Cía\\_2"
    assert memoria.escapar("costo $100") == "costo \\$100"


def test_un_proyecto_con_caracteres_raros_no_rompe_el_documento():
    proyecto = {"Proyecto": "Planta #3 & anexo_B (100% cubierto)"}
    tex = _memoria_casa_rural(proyecto=proyecto)

    assert "Planta \\#3 \\& anexo\\_B (100\\% cubierto)" in tex
    # y no queda ningun % sin escapar, que en LaTeX comenta el resto de la linea
    for linea in tex.splitlines():
        sin_escapar = linea.replace("\\%", "")
        assert "%" not in sin_escapar, linea


def test_los_nombres_de_las_medidas_se_escapan():
    # Los nombres del catalogo llevan "_" (spcr:spcr_nivel_IV), que en LaTeX
    # es un subindice y da error fuera de modo matematico.
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)
    soluciones = medidas.explorar(c["estructura"], c["lineas"], c["zonas"],
                                  c["N_G"], tipo=1, solo_familias={"spcr", "dps"})
    tex = _memoria_casa_rural(soluciones=soluciones)

    assert "spcr:spcr\\_nivel\\_IV" in tex
    assert "spcr:spcr_nivel_IV" not in tex.replace("\\_", "_XX_")


# ---------------------------------------------------------------------------
# Contenido del documento
# ---------------------------------------------------------------------------

def test_estan_todas_las_secciones():
    tex = _memoria_casa_rural()

    for seccion in ("Datos de entrada", "Áreas de colección",
                    "Componentes de riesgo", "Resultado"):
        assert f"\\section{{{seccion}" in tex or seccion in tex, seccion
    assert tex.startswith("\\documentclass")
    assert tex.rstrip().endswith("\\end{document}")


def test_el_veredicto_dice_que_la_casa_rural_no_cumple():
    # R1 = 2,506e-5 contra R_T = 1e-5
    tex = _memoria_casa_rural()

    assert "2{,}506 \\times 10^{-5}" in tex
    assert "\\textbf{No cumple}" in tex


def test_las_secciones_opcionales_solo_salen_si_se_piden():
    sin = _memoria_casa_rural()
    assert "Medidas de protección recomendadas" not in sin
    assert "Análisis de sensibilidad" not in sin

    con = _memoria_casa_rural(
        figuras=[("grafico.png", "Un pie de figura")],
    )
    assert "Análisis de sensibilidad" in con
    assert "\\includegraphics" in con and "grafico.png" in con


def test_escribir_memoria_deja_el_archivo(tmp_path):
    res = resultados_pantalla(CASA_RURAL)
    ruta = memoria.escribir_memoria(tmp_path / "m.tex", CASA_RURAL, res)

    contenido = open(ruta, encoding="utf-8").read()
    assert contenido.startswith("\\documentclass")


# ---------------------------------------------------------------------------
# Compilacion (solo si hay LaTeX)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not hay_latex, reason="pdflatex no está instalado")
def test_el_documento_compila_de_verdad(tmp_path):
    res = resultados_pantalla(CASA_RURAL)
    ruta = memoria.escribir_memoria(tmp_path / "m.tex", CASA_RURAL, res,
                                    proyecto={"Proyecto": "Prueba 100% & Cía"})

    pdf = memoria.compilar(ruta)

    with open(pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_compilar_avisa_si_no_hay_pdflatex(tmp_path, monkeypatch):
    monkeypatch.setattr(memoria.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))

    with pytest.raises(RuntimeError, match="pdflatex"):
        memoria.compilar(tmp_path / "x.tex")


def test_las_frecuencias_del_documento_son_las_calculadas():
    res = resultados_pantalla(CASA_RURAL)
    tex = _memoria_casa_rural()

    assert res["N_D"] == approx(1.031e-2, rel=0.01)
    assert memoria.numero(res["N_D"]) in tex