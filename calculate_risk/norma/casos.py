"""
Paso 33: carga de un caso de evaluación de riesgo desde un archivo JSON.

El JSON tiene 4 llaves: "N_G", "tipos" (lista de riesgos a evaluar, 1-4),
"estructura" (un objeto) y "lineas"/"zonas" (listas de objetos). Cada objeto
usa exactamente los mismos nombres de campo que las dataclasses de modelo.py.
"""
import json

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