"""
Paso 59: el modelo de documento y el dibujante PDF.

No necesitan pantalla gráfica. Cubren los tipos de bloque, el índice y el «página X de N»
verdaderos, y lo que el dibujante hace cuando algo falta: avisar, nunca dejar un cuadro
negro ni romper.
"""
import re

import pytest

pytest.importorskip("reportlab")

from calculate_risk.informe import documento as d          # noqa: E402
from calculate_risk.informe import pdf                      # noqa: E402


def _paginas_del_archivo(ruta) -> int:
    with open(ruta, "rb") as f:
        return len(re.findall(rb"/Type\s*/Page[^s]", f.read()))


def _documento(bloques, **nombrados):
    return d.Documento(titulo="Informe de prueba", bloques=bloques, **nombrados)


# ---------------------------------------------------------------------------
# El modelo rechaza lo que no se puede dibujar
# ---------------------------------------------------------------------------

def test_escapar_protege_el_marcado():
    assert d.escapar("A & B <c>") == "A &amp; B &lt;c&gt;"


@pytest.mark.parametrize("construir", [
    lambda: d.Titulo("x", nivel=3),
    lambda: d.Parrafo("x", estilo="gigante"),
    lambda: d.Tabla([]),
    lambda: d.Tabla([["a", "b"], ["c"]]),
    lambda: d.Tabla([["a", "b"]], anchos=(1,)),
    lambda: d.Tabla([["a", "b"]], derecha=(2,)),
])
def test_el_modelo_rechaza_bloques_mal_formados(construir):
    with pytest.raises(ValueError):
        construir()


def test_las_secciones_son_los_titulos_de_nivel_1():
    doc = _documento([d.Titulo("Uno"), d.Titulo("sub", 2), d.Parrafo("x"), d.Titulo("Dos")])
    assert doc.secciones() == ["Uno", "Dos"]


# ---------------------------------------------------------------------------
# Sale un PDF de verdad, con todos los tipos de bloque
# ---------------------------------------------------------------------------

def _con_todos_los_tipos(figura):
    return _documento([
        d.Contenido(),
        d.Titulo("1. Alcance"),
        d.Parrafo("Texto con R<sub>1</sub> y N<sub>G</sub> en 1/km<super>2</super>."),
        d.Parrafo("Una nota.", "nota"),
        d.Titulo("Subsección", 2),
        d.Formula(r"N_D = N_G \cdot A_D \cdot C_D \cdot 10^{-6}"),
        d.Tabla([["Comp.", "Valor"], ["R<sub>A</sub>", "1,0e-9"]], anchos=(3, 1), derecha=(1,)),
        d.Figura(figura, 60, "Figura 1. Prueba."),
        d.Recuadro("NO CUMPLE", False),
        d.Espacio(5),
        d.Recuadro("CUMPLE", True),
        d.Salto(),
        d.Titulo("2. Conclusión"),
        d.Parrafo("Fin."),
    ], subtitulo="Sub", sobretitulo="Memoria de cálculo", autor="Charlightning",
        encabezado_izq="Izquierda", encabezado_der="Derecha", pie="Pie",
        portada=[d.Tabla([["Proyecto", "Casa"]], anchos=(1, 3), cabecera=False)])


@pytest.fixture
def png(tmp_path):
    matplotlib = pytest.importorskip("matplotlib")
    from matplotlib.figure import Figure
    figura = Figure(figsize=(2, 1))
    figura.text(0.1, 0.4, "figura")
    ruta = tmp_path / "f.png"
    figura.savefig(str(ruta), format="png")
    assert matplotlib
    return str(ruta)


def test_un_documento_con_todos_los_tipos_sale_en_pdf(tmp_path, png):
    ruta = tmp_path / "informe.pdf"

    resultado = pdf.dibujar(_con_todos_los_tipos(png), str(ruta))

    assert ruta.read_bytes().startswith(b"%PDF")
    assert resultado.paginas == _paginas_del_archivo(ruta) >= 3
    assert resultado.advertencias == []


def test_el_indice_dice_la_pagina_real_de_cada_seccion(tmp_path, png):
    resultado = pdf.dibujar(_con_todos_los_tipos(png), str(tmp_path / "i.pdf"))

    assert [t for t, _ in resultado.secciones] == ["1. Alcance", "2. Conclusión"]
    (_, pagina_uno), (_, pagina_dos) = resultado.secciones
    assert pagina_uno == 2                              # la portada es la 1
    assert pagina_dos > pagina_uno                      # el Salto la empuja a otra hoja


def test_el_indice_se_dibuja_y_no_mueve_las_secciones(tmp_path):
    # Sin un lector de PDF no se puede leer el texto; se compara con la composición SIN
    # índice: si el índice no dibujara nada, el archivo pesaría igual.
    con = _documento([d.Contenido(), d.Titulo("A"), d.Salto(), d.Titulo("B")])
    sin = _documento([d.Titulo("A"), d.Salto(), d.Titulo("B")])

    r_con = pdf.dibujar(con, str(tmp_path / "con.pdf"))
    r_sin = pdf.dibujar(sin, str(tmp_path / "sin.pdf"))

    assert (tmp_path / "con.pdf").stat().st_size > (tmp_path / "sin.pdf").stat().st_size
    assert [p for _, p in r_con.secciones] == [p for _, p in r_sin.secciones]


def test_una_seccion_larga_empuja_las_siguientes_y_el_indice_lo_sigue(tmp_path):
    relleno = [d.Parrafo("Línea de relleno. " * 30) for _ in range(40)]
    doc = _documento([d.Contenido(), d.Titulo("Primera")] + relleno + [d.Titulo("Última")])

    resultado = pdf.dibujar(doc, str(tmp_path / "largo.pdf"))

    (_, primera), (_, ultima) = resultado.secciones
    assert primera == 2 and ultima >= 4
    assert resultado.paginas >= ultima


def test_siempre_hay_portada_y_luego_el_cuerpo(tmp_path):
    resultado = pdf.dibujar(_documento([d.Parrafo("x")]), str(tmp_path / "p.pdf"))

    assert resultado.paginas == 2                       # portada + una página de cuerpo


# ---------------------------------------------------------------------------
# Lo que falta se avisa, no rompe
# ---------------------------------------------------------------------------

def test_un_caracter_que_la_fuente_no_trae_se_sustituye_y_se_avisa(tmp_path):
    doc = _documento([d.Parrafo("N<sub>G</sub> ≈ 2,6 y Σ")])

    resultado = pdf.dibujar(doc, str(tmp_path / "u.pdf"))

    assert any("≈" in a and "~" in a for a in resultado.advertencias)
    assert any("Σ" in a for a in resultado.advertencias)


def test_un_caracter_sin_sustituto_sale_como_interrogacion_y_se_avisa(tmp_path):
    resultado = pdf.dibujar(_documento([d.Parrafo("rayo ⚡")]), str(tmp_path / "u.pdf"))

    assert any("⚡" in a and "?" in a for a in resultado.advertencias)


def test_las_tildes_y_la_enie_no_avisan(tmp_path):
    resultado = pdf.dibujar(_documento([d.Parrafo("Año, ñandú, señal, ° y ×")]),
                            str(tmp_path / "t.pdf"))

    assert resultado.advertencias == []


def test_una_figura_que_falta_se_avisa_y_el_informe_sale(tmp_path):
    doc = _documento([d.Figura(str(tmp_path / "no_existe.png"), 100, "Figura 9")])

    resultado = pdf.dibujar(doc, str(tmp_path / "f.pdf"))

    assert any("no_existe.png" in a for a in resultado.advertencias)
    assert (tmp_path / "f.pdf").read_bytes().startswith(b"%PDF")


def test_una_formula_que_no_se_puede_componer_se_avisa_y_el_informe_sale(tmp_path):
    resultado = pdf.dibujar(_documento([d.Formula(r"\mal{")]), str(tmp_path / "m.pdf"))

    assert any("fórmula" in a for a in resultado.advertencias)
    assert (tmp_path / "m.pdf").read_bytes().startswith(b"%PDF")


def test_sin_matplotlib_la_formula_sale_como_texto_y_se_avisa(tmp_path, monkeypatch):
    import sys
    for modulo in ("matplotlib", "matplotlib.figure"):
        monkeypatch.setitem(sys.modules, modulo, None)

    resultado = pdf.dibujar(_documento([d.Formula("x^2")]), str(tmp_path / "s.pdf"))

    assert any("fórmula" in a for a in resultado.advertencias)
    assert (tmp_path / "s.pdf").read_bytes().startswith(b"%PDF")


def test_un_texto_de_usuario_escapado_no_rompe_la_composicion(tmp_path):
    peligroso = d.escapar("Casa <lote 3> & finca")

    resultado = pdf.dibujar(_documento([d.Parrafo(peligroso), d.Titulo(peligroso)]),
                            str(tmp_path / "e.pdf"))

    assert resultado.advertencias == []


def test_un_bloque_desconocido_es_un_error_claro(tmp_path):
    with pytest.raises(TypeError, match="desconocido"):
        pdf.dibujar(_documento(["esto no es un bloque"]), str(tmp_path / "x.pdf"))