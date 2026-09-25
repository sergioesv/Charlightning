"""
Paso 38: medidas de protección (numeral 5 y Figura 1 de la NTC 4552-2:2023).

La Figura 1 describe el procedimiento: se evalúa R; si R > R_T hay que instalar
medidas de protección y volver a evaluar, hasta que R <= R_T. Este módulo es la
parte que faltaba para automatizar ese ciclo: describir cada medida y poder
aplicarla a un caso.

Una medida NO es un dato nuevo de la norma: es escoger otro valor en una de las
tablas que ya están en tablas.py. Por eso el catálogo se arma leyendo tablas.py
y no se inventa ningún número.

Las medidas se agrupan en FAMILIAS (SPCR, DPS, blindaje de líneas...). De cada
familia se escoge una sola opción, porque son alternativas entre sí.

El costo NO viene de la norma (depende del proyecto): se pasa aparte, como un
diccionario {nombre de la medida: costo}.
"""
import copy
from dataclasses import dataclass, replace

from calculate_risk.norma import tablas


@dataclass(frozen=True)
class Efecto:
    """Un parámetro que cambia al instalar la medida.

    destino: "zona", "linea" o "sistema" (los sistemas internos de la zona).
    """
    destino: str
    campo: str
    valor: float


@dataclass(frozen=True)
class Medida:
    """Una medida de protección concreta (una fila de una tabla del Anexo B o C)."""
    nombre: str
    familia: str
    efectos: tuple
    costo: float = 0.0


def _medidas_de_tabla(familia: str, tabla: dict, destino: str, campo: str, saltar=()) -> list:
    """Una medida por cada fila de una tabla simple {clave: valor}."""
    return [
        Medida(nombre=f"{familia}:{clave}", familia=familia,
               efectos=(Efecto(destino, campo, valor),))
        for clave, valor in tabla.items() if clave not in saltar
    ]


def catalogo(costos: dict = None) -> list:
    """Todas las medidas de protección que el modelo sabe representar.

    costos: {nombre de la medida: costo}. Lo que no aparezca queda en 0.
    """
    medidas = []

    # --- Tabla B.2: SPCR (sistema de protección contra rayos) -> P_B
    medidas += _medidas_de_tabla("spcr", tablas.PB, "zona", "P_B", saltar=("sin_spcr",))

    # --- Tablas B.3 y B.7: DPS coordinados -> P_DPS (sistemas) y P_EB (líneas).
    # Las dos tablas tienen las mismas llaves y valores: un mismo sistema de DPS
    # baja las dos probabilidades.
    for clave, valor in tablas.PDPS.items():
        if clave == "sin_dps_coordinado":
            continue
        medidas.append(Medida(
            nombre=f"dps:{clave}", familia="dps",
            efectos=(Efecto("sistema", "P_DPS", valor),
                     Efecto("linea", "P_EB", tablas.PEB[clave])),
        ))

    # --- Tabla B.1: medidas contra tensión de paso y contacto en la estructura
    medidas += _medidas_de_tabla("tension_estructura", tablas.PTA, "zona", "P_TA",
                                 saltar=("sin_medidas",))

    # --- Tabla B.6: medidas contra tensión de contacto por las líneas
    medidas += _medidas_de_tabla("tension_linea", tablas.PTU, "zona", "P_TU",
                                 saltar=("sin_medidas",))

    # --- Tabla C.4: medidas contra incendio -> r_p
    medidas += _medidas_de_tabla("incendio", tablas.RP, "zona", "r_p",
                                 saltar=("sin_medidas",))

    # --- Tabla B.5: cableado interno apantallado -> K_S3
    medidas += _medidas_de_tabla("cableado_interno", tablas.KS3, "sistema", "K_S3",
                                 saltar=("sin_blindar_sin_precauciones",))

    # --- Tabla B.4: blindaje y puesta a tierra de la línea -> C_LD y C_LI
    for clave, valores in tablas.CLD_CLI.items():
        if clave in ("aerea_sin_blindaje", "enterrada_sin_blindaje"):
            continue
        medidas.append(Medida(
            nombre=f"blindaje_linea:{clave}", familia="blindaje_linea",
            efectos=(Efecto("linea", "C_LD", valores["CLD"]),
                     Efecto("linea", "C_LI", valores["CLI"])),
        ))

    if costos:
        medidas = [replace(m, costo=costos.get(m.nombre, 0.0)) for m in medidas]
    return medidas


def familias(medidas) -> dict:
    """Agrupa las medidas por familia, conservando el orden del catálogo."""
    agrupadas = {}
    for m in medidas:
        agrupadas.setdefault(m.familia, []).append(m)
    return agrupadas


def aplicar(estructura, lineas, zonas, medidas):
    """Devuelve una COPIA del caso con las medidas instaladas.

    El caso original no se toca, para poder probar muchas combinaciones sobre
    el mismo punto de partida.
    """
    estructura = copy.deepcopy(estructura)
    lineas = copy.deepcopy(lineas)
    zonas = copy.deepcopy(zonas)

    for medida in medidas:
        for efecto in medida.efectos:
            if efecto.destino == "zona":
                for zona in zonas:
                    setattr(zona, efecto.campo, efecto.valor)
            elif efecto.destino == "linea":
                for linea in lineas:
                    setattr(linea, efecto.campo, efecto.valor)
            elif efecto.destino == "sistema":
                for zona in zonas:
                    for sistema in zona.sistemas_internos:
                        setattr(sistema, efecto.campo, efecto.valor)
            else:
                raise ValueError(f"Destino desconocido: {efecto.destino}")

    return estructura, lineas, zonas