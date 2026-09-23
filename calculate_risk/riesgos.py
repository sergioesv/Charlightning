"""Componentes del riesgo: R = N · P · L."""


def calcular_componente(N, P, L):
    """Un componente de riesgo es el producto de tres factores.

    N: número de eventos peligrosos por año.
    P: probabilidad de que un evento cause daño.
    L: pérdida que produce ese daño.
    """
    return N * P * L


def calcular_X(lineas):
    """Suma n · N · P de todas las líneas que llegan a la estructura.

    lineas: lista de tríos (n, N, P), uno por cada tipo de línea:
        n = cuántas líneas de ese tipo hay,
        N = eventos peligrosos por año en cada una,
        P = probabilidad de que un evento cause daño.
    """
    total = 0
    for n, N, P in lineas:
        total = total + n * N * P
    return total