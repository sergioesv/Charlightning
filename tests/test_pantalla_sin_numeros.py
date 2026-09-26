"""
Criterio 2 del Hito F: no queda ningún valor normativo fuera de tablas.py.

Esto no es una prueba de estilo: es la que impide que vuelvan las once
diferencias que tenía la pantalla vieja. Ahí las listas desplegables traían
los valores escritos a mano en el código de la ventana, y once de ellos no
coincidían con la tabla de la norma — C_E = 0 donde la Tabla A.4 dice 0,01,
L_F = 0,01 para el servicio eléctrico donde la Tabla C.8 dice 0,1, un K_S3
de 0,1 que no es fila de la Tabla B.5... Cada una cambiaba el resultado, y
ninguna prueba las veía, porque el número estaba en el widget.

La regla que lo evita es simple: la pantalla no escribe valores, los pide a
etiquetas.opciones(), que los saca de tablas.py. Así que en ventanas/ no
puede aparecer ningún número con decimales que sea un valor de las tablas.

No se miran los enteros: en ventanas/ son filas, columnas, anchos y márgenes
de los widgets, y también el número del riesgo (1 a 4).
"""
import ast
import pathlib

CARPETA_PANTALLA = pathlib.Path("ventanas")
RUTA_TABLAS = pathlib.Path("calculate_risk/norma/tablas.py")


def _numeros(ruta, solo_decimales=False) -> list:
    """[(linea, valor)] de cada número escrito en el archivo."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    hallados = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant) or isinstance(nodo.value, bool):
            continue
        if solo_decimales and not isinstance(nodo.value, float):
            continue
        if isinstance(nodo.value, (int, float)):
            hallados.append((nodo.lineno, float(nodo.value)))
    return hallados


def _valores_de_las_tablas() -> set:
    return {valor for _, valor in _numeros(RUTA_TABLAS)}


def test_hay_algo_que_revisar():
    # Si un día ventanas/ cambia de sitio, esta prueba no puede pasar sola.
    assert list(CARPETA_PANTALLA.glob("*.py")), "no se encontró ventanas/"
    assert len(_valores_de_las_tablas()) > 20


def test_la_pantalla_no_escribe_ningun_valor_de_las_tablas():
    de_tabla = _valores_de_las_tablas()

    culpables = []
    for ruta in sorted(CARPETA_PANTALLA.rglob("*.py")):
        for linea, valor in _numeros(ruta, solo_decimales=True):
            if valor in de_tabla:
                culpables.append(f"{ruta}:{linea}: {valor}")

    assert not culpables, (
        "un valor de la norma escrito en la pantalla; tiene que salir de "
        "tablas.py por etiquetas.opciones():\n" + "\n".join(culpables))


def test_los_unicos_decimales_de_la_pantalla_son_las_coordenadas_de_ejemplo():
    # Hoy ventanas/ tiene exactamente dos números con decimales, y son la
    # latitud y la longitud de Medellín que trae puestas el diálogo de N_G.
    #
    # Esta es la prueba fuerte, más que la de arriba: un valor escrito a mano
    # que HOY coincida con la tabla pasaría la otra y se separaría el día que
    # la tabla cambie. Si aparece un tercer decimal en la pantalla, hay que
    # mirar de dónde salió antes de añadirlo aquí.
    #
    # El menos de la longitud no entra: en el árbol del código -75.563 es un
    # menos aplicado a 75,563. Da igual, ningún valor de tabla es negativo.
    decimales = {(str(ruta), valor)
                 for ruta in sorted(CARPETA_PANTALLA.rglob("*.py"))
                 for _, valor in _numeros(ruta, solo_decimales=True)}

    assert decimales == {("ventanas/dialogo_densidad.py", 6.251),
                         ("ventanas/dialogo_densidad.py", 75.563)}