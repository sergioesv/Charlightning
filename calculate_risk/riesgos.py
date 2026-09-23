"""Componentes del riesgo: R = N · P · L."""


def calcular_componente(N, P, L):
    """Un componente de riesgo es el producto de tres factores.

    N: número de eventos peligrosos por año.
    P: probabilidad de que un evento cause daño.
    L: pérdida que produce ese daño.
    """
    return N * P * L