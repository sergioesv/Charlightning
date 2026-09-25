"""
Modelo de datos de un caso de evaluación de riesgo (NTC 4552-2:2023).

Estas clases solo almacenan los datos de entrada; el cálculo de N, P, L
y R se hace aparte, con las funciones de frecuencias.py, probabilidades.py
y perdidas.py (Pasos 29-30), a partir de estos datos.
"""

from dataclasses import dataclass, field


@dataclass
class Estructura:
    """Estructura a proteger."""
    L: float          # longitud [m]
    W: float          # ancho [m]
    H: float          # altura [m]
    ubicacion: str    # llave de tablas.CD: "aislada", "rodeada_objetos_mas_altos", ...
    H_min: float = None   # altura mínima, si tiene protrusión (Figura A.2)
    H_p: float = None     # altura de la protrusión


@dataclass
class EstructuraAdyacente:
    """Estructura conectada en el extremo lejano de una línea (N_DJ, ec. A.5)."""
    L: float
    W: float
    H: float
    ubicacion: str    # llave de tablas.CD


@dataclass
class SeccionLinea:
    """Un tramo de línea, con su propio trazado y longitud (Anexo A/B)."""
    longitud: float    # L_L [m]; 1000 si se desconoce
    instalacion: str   # llave de tablas.CI: "aerea", "subterranea", ...
    tipo: str          # llave de tablas.CT: "bt_datos_telecomunicacion", "at_con_transformador"
    entorno: str       # llave de tablas.CE: "rural", "suburbano", "urbano", "urbano_edificios_altos"
    blindaje: str      # llave de tablas.CLD_CLI


@dataclass
class Linea:
    """Una línea entrante a la estructura; puede tener varias secciones."""
    secciones: list = field(default_factory=list)          # list[SeccionLinea]
    estructura_adyacente: EstructuraAdyacente = None


@dataclass
class SistemaInterno:
    """Sistema interno conectado a una línea (para P_M, P_U, P_V, P_W, P_Z)."""
    uw: float          # tensión soportada al impulso [kV]: 1, 1.5, 2.5, 4 o 6
    tipo_linea: str    # "potencia" o "telecomunicacion", para tablas.PLD/PLI


@dataclass
class Zona:
    """Una zona de la estructura, con sus propios parámetros de riesgo."""
    nombre: str
    nz: float          # personas en la zona
    tz: float          # horas anuales de presencia
    superficie: str    # llave de tablas.N_SUPERFICIE (factor rt)


@dataclass
class PerdidasZona:
    """Valores económicos/culturales de una zona (para L3 y L4)."""
    ca: float = 0.0    # animales
    cb: float = 0.0    # edificio
    cc: float = 0.0    # contenido
    cs: float = 0.0    # sistemas internos


@dataclass
class Caso:
    """Un caso completo: la estructura, sus zonas y sus líneas."""
    estructura: Estructura
    zonas: list = field(default_factory=list)   # list[Zona]
    lineas: list = field(default_factory=list)  # list[Linea]