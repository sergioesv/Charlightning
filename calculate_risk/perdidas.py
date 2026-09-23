"""Factores de pérdida (L) para cada componente del riesgo."""


def calcular_L_A(r_a, L_t):
    """Pérdida por tensiones de paso y contacto (lesiones a seres vivos).

    r_a: factor de reducción según el tipo de suelo.
    L_t: pérdida típica por lesiones.
    Ecuación (16), pág. 49.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    return r_a * L_t


def calcular_L_B(r, h_z, r_f, L_f):
    """Pérdida por daño físico (incendio, explosión...).

    r: reducción por medidas contra incendio.
    h_z: aumento por peligros especiales (pánico, evacuación difícil...).
    r_f: reducción según el riesgo de incendio de la estructura.
    L_f: pérdida típica por daño físico.
    PENDIENTE: verificar con IEC 62305-2:2024.
    """
    return r * h_z * r_f * L_f