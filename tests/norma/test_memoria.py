"""
Paso 40: las piezas compartidas de la memoria de cálculo en LaTeX.

Aquí viven las pruebas que NO dependen de cómo se armó el caso: el formato de
los números, el escape del texto del usuario, la compilación con pdflatex y el
desarrollo del cálculo paso a paso (lo que hace que sea una memoria y no una
hoja de resultados). Las de la estructura del documento con varias zonas y
varias líneas están en test_memoria_caso.py.

Paso 51f: antes el documento se armaba desde el diccionario plano de la
pantalla vieja (`memoria_tex(datos, resultados)`). Esa mitad del módulo se
retiró con la pantalla; ahora todo sale de memoria_tex_caso(). Los números
comprobados son los mismos: A_D = 2 577,88 m², N_D = 1,031e-2, R_V = 95,8 %
del total de la casa rural del Anexo E.2.
"""
import shutil

import pytest
from pytest import approx

from calculate_risk.norma import casos, medidas, memoria, riesgos
from tests.norma.casos_de_prueba import RUTA_CASA_RURAL, casa_rural

hay_latex = shutil.which("pdflatex") is not None
ZONA_CASA_RURAL = "Z2_interior"


def _caso_y_resultado(tipo=1):
    """({tipo: caso}, {tipo: resultado}), lo que pide memoria_tex_caso()."""
    caso = casos.cargar_caso(RUTA_CASA_RURAL)
    r = riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                        caso["N_G"], tipos=(tipo,))[tipo]
    return {tipo: caso}, {tipo: r}


def _memoria_casa_rural(**kwargs):
    return memoria.memoria_tex_caso(*_caso_y_resultado(), **kwargs)


def _zona_casa_rural(tipo=1):
    _, por_tipo = _caso_y_resultado(tipo)
    return por_tipo[tipo]["zonas"][ZONA_CASA_RURAL]


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
    soluciones = medidas.explorar(*casa_rural(), tipo=1,
                                 solo_familias={"spcr", "dps"})
    tex = _memoria_casa_rural(soluciones=soluciones)

    assert "spcr:spcr\\_nivel\\_IV" in tex
    assert "spcr:spcr_nivel_IV" not in tex.replace("\\_", "_XX_")


# ---------------------------------------------------------------------------
# Compilacion (solo si hay LaTeX)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not hay_latex, reason="pdflatex no está instalado")
def test_el_documento_compila_de_verdad(tmp_path):
    ruta = memoria.escribir_memoria_caso(
        tmp_path / "m.tex", *_caso_y_resultado(),
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
    zona = _zona_casa_rural()
    tex = _memoria_casa_rural()

    assert zona["_detalle"]["N_D"] == approx(1.031e-2, rel=0.01)
    assert memoria.numero(zona["_detalle"]["N_D"]) in tex


# ---------------------------------------------------------------------------
# Paso 40b: el desarrollo del calculo (lo que hace que sea una memoria)
# ---------------------------------------------------------------------------

def test_el_motor_devuelve_los_valores_intermedios():
    d = _zona_casa_rural()["_detalle"]

    # Los de la estructura, contra la Tabla E.7 de la norma
    assert d["A_D"] == approx(2.578e3, rel=0.001)
    assert d["N_D"] == approx(1.03e-2, rel=0.01)
    # Los de cada linea, por separado
    assert set(d["lineas"]) == {"potencia", "telecomunicacion"}
    assert d["lineas"]["potencia"]["N_L"] == approx(8.00e-2, rel=0.01)
    assert d["lineas"]["telecomunicacion"]["N_L"] == approx(1.60e-1, rel=0.01)


def test_el_desarrollo_muestra_la_formula_con_los_numeros():
    zona = _zona_casa_rural()
    tex = _memoria_casa_rural()

    assert "Desarrollo del cálculo" in tex
    # R_B = N_D x P_B x L_B, con los tres numeros y el resultado
    assert "R_{B} = (N_D) \\times P_B \\times L_B" in tex
    assert memoria.numero(zona["_detalle"]["N_D"]) in tex
    assert memoria.numero(zona["R_B"]) in tex


def test_el_desarrollo_dice_que_componentes_no_aplican():
    # En la casa rural L_O = 0, asi que R_C, R_M, R_W y R_Z no intervienen
    # en R1 (numeral 4.3). Eso hay que decirlo, no dejarlo en blanco.
    tex = _memoria_casa_rural()

    for letra in ("C", "M", "W", "Z"):
        assert f"$R_{{{letra}}}$ no interviene en $R_1$" in tex


def test_la_participacion_coincide_con_lo_que_dice_la_norma():
    # La norma dice de la casa rural: domina R_V (~96 %), luego R_B (~4 %).
    zona = _zona_casa_rural()
    tex = _memoria_casa_rural()

    assert "De dónde viene $R_1$" in tex
    assert zona["R_V"] / zona["total"] == approx(0.958, abs=0.005)
    assert "$95.8$\\,\\%" in tex


def test_el_separador_de_miles_no_se_come_la_coma_decimal():
    # Bug real: el .replace(",", " ") del costo borraba la coma de
    # numero() y "2{,}233 x 10^-6" salia como "2233 x 10^-6".
    soluciones = medidas.explorar(
        *casa_rural(), tipo=1,
        catalogo_medidas=medidas.catalogo(costos={"dps:npr_III_IV": 1_000_000}),
        solo_familias={"dps"})
    tex = _memoria_casa_rural(soluciones=soluciones)

    assert "2{,}233 \\times 10^{-6}" in tex
    assert "1~000~000" in tex


# ---------------------------------------------------------------------------
# Las secciones opcionales
# ---------------------------------------------------------------------------

def test_las_secciones_opcionales_solo_salen_si_se_piden():
    sin = _memoria_casa_rural()
    assert "Medidas de protección recomendadas" not in sin
    assert "Análisis de sensibilidad" not in sin

    con = _memoria_casa_rural(figuras=[("grafico.png", "Un pie de figura")])
    assert "Análisis de sensibilidad" in con
    assert "\\includegraphics" in con and "grafico.png" in con


def test_si_ninguna_medida_alcanza_el_informe_lo_dice():
    # Callarlo seria peor que no ponerlo: daria a entender que no hacen falta.
    sin_pedir = _memoria_casa_rural(soluciones=None)
    ninguna = _memoria_casa_rural(soluciones=[])

    assert "Medidas de protección recomendadas" not in sin_pedir
    assert "Ninguna combinación de las medidas contempladas" in ninguna