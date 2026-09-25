"""
Modelo de datos de un caso de evaluación de riesgo (NTC 4552-2:2023).

Cada campo guarda ya el VALOR resuelto del factor (por ejemplo C_D=1.0),
no la llave de la tabla; tablas.py se usa para resolver esos valores antes
de construir estos objetos.
"""

from dataclasses import dataclass, field


@dataclass
class Estructura:
    """Estructura a proteger (también se usa para la estructura adyacente)."""
    L: float
    W: float
    H: float
    H_p: float = 0.0        # altura de protrusión en el techo (0 si no hay)
    C_D: float = 1.0        # Tabla A.1
    n_t: float = 1.0        # personas totales en la estructura
    c_t: float = 1.0        # valor total de la estructura (para L4)

    # Habilitan componentes condicionales (numeral 4.3)
    riesgo_explosion_o_vital: bool = False   # habilita R_C, R_M, R_W, R_Z en R1
    hay_animales: bool = False               # habilita R_A, R_U en R4


@dataclass
class Linea:
    """Línea (o sección de línea) conectada a la estructura."""
    nombre: str
    L_L: float = 1000.0     # longitud de la sección [m]
    C_I: float = 1.0        # Tabla A.2
    C_T: float = 1.0        # Tabla A.3
    C_E: float = 1.0        # Tabla A.4
    U_W: float = 2.5        # tensión soportada al impulso [kV]

    C_LD: float = 1.0       # Tabla B.4
    C_LI: float = 1.0       # Tabla B.4
    P_LD: float = 1.0       # Tabla B.8
    P_LI: float = 1.0       # Tabla B.9
    P_EB: float = 1.0       # Tabla B.7

    adyacente: Estructura = None   # estructura conectada en el extremo lejano (ec. A.5)
    C_DJ: float = 1.0              # Tabla A.1, para la estructura adyacente


@dataclass
class SistemaInterno:
    """Sistema interno dentro de una zona, alimentado por una línea."""
    nombre: str
    linea: str = ""          # nombre de la Linea que lo alimenta (para su C_LD)
    K_S3: float = 1.0        # Tabla B.5
    U_W: float = 2.5         # -> K_S4 = 1/U_W
    P_DPS: float = 1.0       # Tabla B.3


@dataclass
class Zona:
    """Zona Z_S de características homogéneas dentro de la estructura."""
    nombre: str

    P_TA: float = 1.0        # Tabla B.1
    P_TU: float = 1.0        # Tabla B.6
    P_B: float = 1.0         # Tabla B.2
    K_S1: float = 1.0        # 0,12 x w_m1 (ec. B.5)
    K_S2: float = 1.0        # 0,12 x w_m2 (ec. B.6)

    sistemas_internos: list = field(default_factory=list)   # list[SistemaInterno]

    r_t: float = 1.0         # Tabla C.3
    r_p: float = 1.0         # Tabla C.4
    r_f: float = 1.0         # Tabla C.5
    h_z: float = 1.0         # Tabla C.6

    L_T: float = 0.0         # Tabla C.2 / C.12
    L_F: float = 0.0         # Tabla C.2 / C.8 / C.10 / C.12
    L_O: float = 0.0         # Tabla C.2 / C.8 / C.12

    n_z: float = 0.0         # personas o usuarios en la zona
    t_z: float = 8760.0      # horas/año de presencia

    c_z: float = 0.0         # valor de patrimonio cultural en la zona (L3)
    c_a: float = 0.0         # valor de animales (L4)
    c_b: float = 0.0         # valor del edificio (L4)
    c_c: float = 0.0         # valor del contenido (L4)
    c_s: float = 0.0         # valor de los sistemas internos (L4)

    exterior_sin_personas: bool = False   # anula R_A y R_U (numeral B.6)


@dataclass
class Caso:
    """Un caso completo: la estructura, sus zonas y sus líneas."""
    estructura: Estructura
    zonas: list = field(default_factory=list)    # list[Zona]
    lineas: list = field(default_factory=list)   # list[Linea]