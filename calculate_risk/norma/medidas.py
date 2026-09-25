"""
medidas de protección (numeral 5 y Figura 1 de la NTC 4552-2:2023).

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
import itertools
from dataclasses import dataclass, replace

from calculate_risk.norma import costos, riesgos, tablas


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




# ---------------------------------------------------------------------------
# Paso 38b: barrido de combinaciones (el ciclo de la Figura 1, automatizado)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Solucion:
    """Una combinación de medidas ya evaluada."""
    medidas: tuple
    riesgo: float
    R_T: float
    cumple: bool
    costo: float

    # Anexo D (solo si se dieron los datos economicos)
    C_L: float = None      # costo de las perdidas sin proteccion (ec. D.2)
    C_RL: float = None     # perdidas residuales con la proteccion (ec. D.4)
    C_PM: float = None     # costo anual de las medidas (ec. D.5)
    S_M: float = None      # ahorro anual; se justifica si S_M > 0 (ec. D.6)

    @property
    def nombres(self) -> tuple:
        return tuple(m.nombre for m in self.medidas)


def combinaciones(medidas):
    """Todas las combinaciones posibles tomando a lo sumo UNA medida por familia.

    Incluye la combinación vacía (no instalar nada), que es el punto de partida.
    """
    opciones = [[None] + lista for lista in familias(medidas).values()]
    for elegidas in itertools.product(*opciones):
        yield tuple(m for m in elegidas if m is not None)


def explorar(estructura, lineas, zonas, N_G, tipo=1, catalogo_medidas=None,
             solo_familias=None, solo_las_que_cumplen=True, economia=None) -> list:
    """Prueba combinaciones de medidas y devuelve las soluciones evaluadas.

    Es el ciclo de la Figura 1 hecho de una vez: en vez de instalar, recalcular
    y repetir a mano, se calcula R para cada combinación posible.

    solo_familias: nombres de familia a considerar (None = todas).

    economia: {"c_t": valor total de la estructura, "i": interes,
    "a": amortizacion, "m": mantenimiento, "caso_l4": (estructura, lineas, zonas)}.
    Si se da, cada solucion trae ademas el analisis del Anexo D y las soluciones
    se ordenan por el ahorro anual S_M (de mayor a menor); si no, por costo.

    OJO con "caso_l4": el Anexo D siempre trabaja sobre R4, y el caso armado
    para R1 no sirve para R4 (la zona lleva otros L_F, L_O y otras razones
    c/c_t). Por eso hay que pasar aparte el mismo caso pero armado para L4.
    Si ya se esta evaluando tipo=4, se puede omitir.
    """
    medidas_disponibles = catalogo_medidas if catalogo_medidas is not None else catalogo()
    if solo_familias is not None:
        medidas_disponibles = [m for m in medidas_disponibles if m.familia in solo_familias]

    # Anexo D: el costo de las perdidas SIN proteccion es el punto de partida
    C_L = caso_l4 = None
    if economia is not None:
        caso_l4 = economia.get("caso_l4")
        if caso_l4 is None:
            if tipo != 4:
                raise ValueError(
                    "El Anexo D trabaja sobre R4: hay que pasar economia['caso_l4'] "
                    "con el mismo caso armado para L4"
                )
            caso_l4 = (estructura, lineas, zonas)
        r4_base = riesgos.evaluar(*caso_l4, N_G, tipos=(4,))[4]
        C_L = costos.c_l(r4_base["total"], economia["c_t"])

    soluciones = []
    for combinacion in combinaciones(medidas_disponibles):
        e, l, z = aplicar(estructura, lineas, zonas, combinacion)
        r = riesgos.evaluar(e, l, z, N_G, tipos=(tipo,))[tipo]
        if solo_las_que_cumplen and not r["cumple"]:
            continue

        C_P = sum(m.costo for m in combinacion)
        C_RL = C_PM = S_M = None
        if economia is not None:
            r4 = riesgos.evaluar(*aplicar(*caso_l4, combinacion), N_G, tipos=(4,))[4]
            C_RL = costos.c_rl(r4["total"], economia["c_t"])
            C_PM = costos.c_pm(C_P, economia["i"], economia["a"], economia["m"])
            S_M = costos.s_m(C_L, C_PM, C_RL)

        soluciones.append(Solucion(
            medidas=combinacion,
            riesgo=r["total"],
            R_T=r["R_T"],
            cumple=r["cumple"],
            costo=C_P,
            C_L=C_L, C_RL=C_RL, C_PM=C_PM, S_M=S_M,
        ))

    if economia is not None:
        # Primero las que cumplen, y entre ellas la de mayor ahorro anual
        soluciones.sort(key=lambda s: (not s.cumple, -s.S_M, len(s.medidas)))
    else:
        soluciones.sort(key=lambda s: (not s.cumple, s.costo, len(s.medidas), s.riesgo))
    return soluciones