"""
Paso 33: carga de un caso de evaluación de riesgo desde un archivo JSON.
Paso 48: guardado, y el formato ampliado a los cuatro riesgos.

El JSON tiene 4 llaves: "N_G", "tipos" (lista de riesgos a evaluar, 1-4),
"estructura" (un objeto) y "lineas"/"zonas" (listas de objetos). Cada objeto
usa exactamente los mismos nombres de campo que las dataclasses de modelo.py.

Las pérdidas de una zona son de UN tipo de riesgo (ver el reparto
COMUNES / POR_TIPO de ventanas/formularios.py), así que un caso que evalúa
los cuatro necesita cuatro juegos. Para eso una zona puede traer además la
llave "perdidas":

    "zonas": [{ ...lo común..., "perdidas": {"1": {...}, "4": {...}} }]

Si "perdidas" no está, se usan los campos sueltos de la zona para todos los
tipos de "tipos", que es el formato del Paso 33 y el de casos/casa_rural.json.
Los archivos viejos se siguen leyendo igual.
"""
import json
from dataclasses import asdict

from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona


def _sistema_interno(datos: dict) -> SistemaInterno:
    return SistemaInterno(**datos)


def _zona(datos: dict) -> Zona:
    datos = dict(datos)
    sistemas = datos.pop("sistemas_internos", [])
    return Zona(sistemas_internos=[_sistema_interno(s) for s in sistemas], **datos)


def _linea(datos: dict) -> Linea:
    datos = dict(datos)
    adyacente = datos.pop("adyacente", None)
    if adyacente is not None:
        adyacente = Estructura(**adyacente)
    return Linea(adyacente=adyacente, **datos)


def cargar_caso(ruta: str) -> dict:
    """Lee un archivo JSON y devuelve lo necesario para llamar riesgos.evaluar:
    {"estructura": Estructura, "lineas": [Linea], "zonas": [Zona],
     "N_G": float, "tipos": tuple[int]}."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)

    return {
        "estructura": Estructura(**datos["estructura"]),
        "lineas": [_linea(d) for d in datos.get("lineas", [])],
        "zonas": [_zona(d) for d in datos.get("zonas", [])],
        "N_G": datos["N_G"],
        "tipos": tuple(datos.get("tipos", [1])),
    }


# ---------------------------------------------------------------------------
# Paso 48: los cuatro riesgos en un archivo
# ---------------------------------------------------------------------------

def cargar_casos(ruta: str) -> dict:
    """Lee un archivo y devuelve {tipo: caso}, un caso por riesgo guardado.

    Sirve para los dos formatos: si las zonas no traen "perdidas", el caso es
    el mismo para todos los tipos que liste "tipos".
    """
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)

    estructura = Estructura(**datos["estructura"])
    lineas = [_linea(d) for d in datos.get("lineas", [])]
    N_G = datos["N_G"]
    zonas = datos.get("zonas", [])

    tipos = _tipos_guardados(zonas, datos.get("tipos", [1]))
    return {
        tipo: {
            "estructura": estructura,
            "lineas": lineas,
            "zonas": [_zona_de_tipo(z, tipo) for z in zonas],
            "N_G": N_G,
        }
        for tipo in tipos
    }


def _tipos_guardados(zonas: list, por_defecto) -> list:
    """Qué riesgos trae el archivo: los de "perdidas" si están, si no "tipos"."""
    con_perdidas = [z for z in zonas if "perdidas" in z]
    if not con_perdidas:
        return [int(t) for t in por_defecto]
    guardados = set(int(t) for t in con_perdidas[0]["perdidas"])
    for zona in con_perdidas[1:]:
        guardados &= set(int(t) for t in zona["perdidas"])
    return sorted(guardados)


def _zona_de_tipo(datos: dict, tipo: int) -> Zona:
    """La zona con las pérdidas del riesgo pedido."""
    datos = dict(datos)
    perdidas = datos.pop("perdidas", None)
    if perdidas is not None:
        datos.update(perdidas.get(str(tipo), perdidas.get(tipo, {})))
    return _zona(datos)


def guardar_caso(ruta: str, casos: dict) -> str:
    """Escribe {tipo: caso} en un archivo JSON, con las pérdidas por riesgo.

    casos es lo que devuelve EditorCaso.casos_por_tipo(). La estructura, las
    líneas y N_G se toman del primero: son las mismas para los cuatro.
    """
    tipos = sorted(casos)
    primero = casos[tipos[0]]

    zonas = []
    for indice, zona in enumerate(primero["zonas"]):
        comun = asdict(zona)
        por_tipo = {tipo: asdict(casos[tipo]["zonas"][indice]) for tipo in tipos}

        # Los campos que cambian de un riesgo a otro salen del bloque común y
        # se escriben en TODOS los tipos, incluido el primero: si solo se
        # anotaran las diferencias contra el primero, los valores de ese se
        # perderian al sacarlos de lo común.
        cambian = {campo for valores in por_tipo.values()
                   for campo, valor in valores.items() if valor != comun[campo]}
        for campo in cambian:
            comun.pop(campo, None)
        comun["perdidas"] = {str(tipo): {campo: valores[campo] for campo in cambian}
                             for tipo, valores in por_tipo.items()}
        zonas.append(comun)

    datos = {
        "N_G": primero["N_G"],
        "tipos": tipos,
        "estructura": asdict(primero["estructura"]),
        "lineas": [asdict(linea) for linea in primero["lineas"]],
        "zonas": zonas,
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    return str(ruta)