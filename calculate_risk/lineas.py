"""Áreas colectoras y número de eventos en las líneas de servicio."""

import math



def calcular_A_l_aerea(L_c, H, H_a, H_c):
    """Área colectora para impactos DIRECTOS a una línea aérea, en m².

    L_c: longitud de la línea (m).
    H: altura de la estructura (m).
    H_a: altura de la estructura en el otro extremo de la línea (m).
    H_c: altura de los conductores sobre el suelo (m).
    A la longitud se le descuenta 3·H + 3·H_a; si queda negativa, se toma 0.
    Tabla 12, pág. 37.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    longitud_util = max(0.0, L_c - 3 * H - 3 * H_a)
    return 6 * H_c * longitud_util


def calcular_A_i_aerea(L_c, D_L):
    """Área colectora para impactos CERCA de una línea aérea, en m².

    L_c: longitud de la línea (m).
    D_L: distancia (m) a cada lado de la línea. La versión original usa 500 m.
    Tabla 12, pág. 38.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    return 2 * D_L * L_c


def calcular_N_L(N_g, A_l, C_t, C_d):
    """Número de impactos directos a la línea por año.

    C_t: factor por transformador. C_d: factor de ubicación.
    PENDIENTE: verificar con IEC 62305-2:2024 (N_SG reemplaza a N_g).
    """
    return N_g * A_l * C_t * C_d * 1e-6


def calcular_N_I(N_g, A_i, C_t, C_e):
    """Número de impactos cerca de la línea por año.

    C_t: factor por transformador. C_e: factor ambiental.
    PENDIENTE: verificar con IEC 62305-2:2024 (N_SG reemplaza a N_g).
    """
    return N_g * A_i * C_t * C_e * 1e-6


def calcular_A_l_subterranea(L_c, H, H_a, rho):
    """Área colectora para impactos DIRECTOS a una línea subterránea, en m².

    L_c: longitud de la línea (m).
    H: altura de la estructura (m).
    H_a: altura de la estructura en el otro extremo de la línea (m).
    rho: resistividad del terreno (Ω·m).
    Si la longitud útil queda negativa, se toma 0.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    longitud_util = max(0.0, L_c - 3 * (H_a + H))
    return longitud_util * math.sqrt(rho)


def calcular_A_i_subterranea(L_c, rho):
    """Área colectora para impactos CERCA de una línea subterránea, en m².

    L_c: longitud de la línea (m).
    rho: resistividad del terreno (Ω·m).
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    return 25 * L_c * math.sqrt(rho)