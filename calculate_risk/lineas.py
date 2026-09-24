"""Áreas colectoras y número de eventos en las líneas de servicio."""


def calcular_A_l_aerea(L_c):
    """Área colectora para impactos DIRECTOS a una línea aérea, en m².

    L_c: longitud de la línea (m).
    Ecuación (A.9), Anexo A: A_L = 40·L_c. En esta edición de la norma
    esta área no depende de la altura de la estructura ni de los
    conductores; la diferencia entre línea aérea y subterránea se
    aplica luego, con el factor C_I, en calcular_N_L / calcular_N_I.
    Corregido: antes dependía de H, H_a y H_c (fórmula de otra edición).
    """
    return 40 * L_c


def calcular_A_i_aerea(L_c, D_L):
    """Área colectora para impactos CERCA de una línea aérea, en m².

    L_c: longitud de la línea (m).
    Ecuación (A.11), Anexo A: A_I = 4000·L_c.
    Corregido: antes usaba una distancia D_L = 500 m variable
    (fórmula de otra edición de la norma).
    """
    return 4000 * L_c


def calcular_N_L(N_g, A_l, C_I, C_E, C_T):
    """Número de impactos directos a la línea por año.

    C_I: factor de instalación (Tabla A.2: aérea = 1, subterránea = 0,5).
    C_E: factor ambiental (Tabla A.4). C_T: factor de tipo de línea (Tabla A.3).
    Ecuación (A.8), Anexo A.
    Corregido: antes usaba C_t (transformador) y C_d (ubicación de la
    estructura, que no interviene aquí); ahora usa C_I, C_E y C_T.
    """
    return N_g * A_l * C_I * C_E * C_T * 1e-6


def calcular_N_I(N_g, A_i, C_I, C_E, C_T):
    """Número de impactos cerca de la línea por año.

    C_I: factor de instalación (Tabla A.2). C_E: factor ambiental (Tabla A.4).
    C_T: factor de tipo de línea (Tabla A.3).
    Ecuación (A.10), Anexo A.
    Corregido: antes usaba C_t y C_e, sin C_I; ahora usa los tres factores
    de la norma.
    """
    return N_g * A_i * C_I * C_E * C_T * 1e-6


def calcular_A_l_subterranea(L_c, H, H_a, rho):
    """Área colectora para impactos DIRECTOS a una línea subterránea, en m².

    L_c: longitud de la línea (m).
    Misma fórmula que la línea aérea (Ecuación A.9): A_L = 40·L_c.
    Corregido: antes dependía de la resistividad del terreno (√ρ),
    fórmula de otra edición de la norma; en esta edición la resistividad
    no interviene en el área colectora.
    """
    return return 40 * L_c

def calcular_A_i_subterranea(L_c, rho):
    """Área colectora para impactos CERCA de una línea subterránea, en m².

    L_c: longitud de la línea (m).
    Misma fórmula que la línea aérea (Ecuación A.11): A_I = 4000·L_c.
    Corregido: antes dependía de la resistividad del terreno (√ρ).
    """
    return 4000 * L_c


def calcular_delta_N(N_I, N_L):
    """Impactos cerca de la línea que NO son impactos directos a ella.

    Se resta N_L de N_I; si el resultado es negativo, se toma 0.
    """
    return max(0.0, N_I - N_L)