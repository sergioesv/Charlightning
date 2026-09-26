"""
Lo que de verdad se prueba aquí es que etiquetas.py y tablas.py NO se puedan
separar: toda llave tiene que tener texto, no puede sobrar ninguno, y en
etiquetas.py no puede aparecer ningún número. Esa es la prueba que le faltaba
a opciones.py, que es por lo que se separó de las tablas.
"""
import ast
import inspect

import pytest

from calculate_risk.norma import etiquetas, tablas


def _tablas_de_texto():
    """Los diccionarios de tablas.py cuyas llaves son textos.

    Quedan fuera PLI y las subtablas de PLD indexadas por Uw, que tienen
    llaves numéricas: ahí el usuario no elige una fila, escribe la tensión.
    """
    for nombre, valor in vars(tablas).items():
        if nombre.startswith("_") or not isinstance(valor, dict):
            continue
        if all(isinstance(llave, str) for llave in valor):
            yield nombre, valor


# "CLD" y "CLI" son los dos factores que da cada fila de la Tabla B.4, no
# filas que el usuario elija: no llevan etiqueta.
NO_SON_FILAS = {"CLD", "CLI"}


def _llaves_de_texto(tabla) -> set:
    """Todas las llaves de texto, incluidas las de las subtablas (PLD)."""
    llaves = set()
    for llave, valor in tabla.items():
        if isinstance(llave, str) and llave not in NO_SON_FILAS:
            llaves.add(llave)
        if isinstance(valor, dict):
            llaves |= _llaves_de_texto(valor)
    return llaves


# ---------------------------------------------------------------------------
# Que no se separen de tablas.py
# ---------------------------------------------------------------------------

def test_todas_las_tablas_tienen_etiquetas():
    faltan = [nombre for nombre, _ in _tablas_de_texto()
              if nombre not in etiquetas.ETIQUETAS]

    assert faltan == [], f"tablas sin etiquetas: {faltan}"


def test_toda_llave_tiene_su_texto():
    for nombre, tabla in _tablas_de_texto():
        esperadas = _llaves_de_texto(tabla)
        tiene = set(etiquetas.ETIQUETAS[nombre])

        assert esperadas <= tiene, f"{nombre}: sin texto {esperadas - tiene}"


def test_no_sobran_etiquetas():
    # Una etiqueta huérfana suele significar que la tabla cambió y esto no.
    tablas_por_nombre = dict(_tablas_de_texto())
    for nombre, textos in etiquetas.ETIQUETAS.items():
        reales = _llaves_de_texto(tablas_por_nombre[nombre])
        sobran = set(textos) - reales

        assert sobran == set(), f"{nombre}: etiquetas de más {sobran}"


def test_cada_tabla_dice_de_que_tabla_de_la_norma_sale():
    for nombre in etiquetas.ETIQUETAS:
        assert nombre in etiquetas.NOMBRES, nombre
    assert etiquetas.nombre_de("CD").startswith("Tabla A.1")
    assert etiquetas.nombre_de("HZ").startswith("Tabla C.6")


# ---------------------------------------------------------------------------
# Que aquí no haya valores normativos
# ---------------------------------------------------------------------------

def test_etiquetas_no_contiene_ni_un_numero():
    # Es la garantía de que los valores siguen viviendo solo en tablas.py.
    arbol = ast.parse(inspect.getsource(etiquetas))
    numeros = [n for n in ast.walk(arbol)
               if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
               and not isinstance(n.value, bool)]

    assert not numeros, (
        f"hay un número en etiquetas.py, línea {numeros[0].lineno}: "
        "los valores van solo en tablas.py")


def test_ningun_texto_es_la_llave_pelada():
    # Si alguien pega la llave como etiqueta, el usuario ve "panico_bajo".
    for nombre, textos in etiquetas.ETIQUETAS.items():
        for llave, texto in textos.items():
            assert texto.strip(), f"{nombre}.{llave} sin texto"
            assert "_" not in texto, f"{nombre}.{llave} parece la llave: {texto}"


# ---------------------------------------------------------------------------
# opciones(): lo que va a consumir la pantalla
# ---------------------------------------------------------------------------

def test_opciones_da_el_texto_y_el_valor_en_el_orden_de_la_tabla():
    assert etiquetas.opciones("CD") == [
        ("Rodeada de objetos más altos", 0.25),
        ("Rodeada de objetos de la misma altura o más bajos", 0.5),
        ("Aislada, sin otros objetos cerca", 1),
        ("Aislada sobre una colina o un montículo", 2),
    ]


def test_los_valores_de_opciones_salen_de_tablas():
    for nombre in etiquetas.SIMPLES:
        valores = [valor for _, valor in etiquetas.opciones(nombre)]

        assert valores == list(getattr(tablas, nombre).values())


def test_llaves_va_en_el_mismo_orden_que_opciones():
    for nombre in etiquetas.SIMPLES:
        llaves = etiquetas.llaves(nombre)
        textos = [texto for texto, _ in etiquetas.opciones(nombre)]

        assert llaves == list(getattr(tablas, nombre))
        assert [etiquetas.texto(nombre, k) for k in llaves] == textos


def test_el_urbano_con_edificios_altos_ya_no_puede_valer_cero():
    # La pantalla vieja ofrecía 0 aquí; la Tabla A.4 dice 0,01. Con 0, N_L y
    # N_I se anulan y la línea no puede ser impactada nunca.
    urbano_altos = dict(etiquetas.opciones("CE"))["Urbano con edificios altos"]

    assert urbano_altos == 0.01


def test_la_tabla_del_cableado_ofrece_sus_cuatro_filas():
    # La pantalla vieja solo daba 0,1 y 1, y el 0,1 no es fila de la Tabla B.5.
    valores = [valor for _, valor in etiquetas.opciones("KS3")]

    assert valores == [1, 0.2, 0.01, 0.0001]


def test_cld_cli_entrega_los_dos_factores_de_una_vez():
    primera = etiquetas.opciones("CLD_CLI")[0]

    assert primera == ("Aérea, sin blindaje", {"CLD": 1, "CLI": 1})


def test_las_tablas_de_doble_entrada_avisan_en_vez_de_mentir():
    # PLD y PLI necesitan además la tensión soportada Uw: no son una lista.
    for tabla in ("PLD", "PLI", "RT"):
        with pytest.raises(ValueError, match="opción simple"):
            etiquetas.opciones(tabla)