"""
Paso 39b: figuras de los barridos, en PNG, para el artículo.

Dos figuras, las mismas dos tablas del Paso 39a:

1. `curva_sensibilidad()` -- R contra un parámetro (N_G, altura, longitud de
   línea...), con la línea del riesgo tolerable R_T.
2. `dispersion_costo_riesgo()` -- una nube de puntos con el costo de cada
   combinación de medidas contra el riesgo que deja.

Decisiones de diseño (no son gusto, son legibilidad):
  - Eje Y logarítmico: el riesgo se mueve en órdenes de magnitud, y en escala
    lineal las soluciones buenas quedarían todas pegadas al cero.
  - Colores azul/naranja en vez de verde/rojo: verde y rojo son justo el par
    que no distingue una persona con daltonismo (el más común).
  - Cumple / no cumple va además por forma de marcador y por leyenda, para que
    el color nunca sea lo único que lleva el significado.
  - La línea de R_T va en gris oscuro punteado: es una referencia, no una
    serie de datos, y así no compite con los puntos.
"""
import matplotlib

matplotlib.use("Agg")          # sin ventana: solo escribe archivos
import matplotlib.pyplot as plt         # noqa: E402
from matplotlib.ticker import FuncFormatter   # noqa: E402

# Paleta verificada para daltonismo y para contraste sobre fondo claro
AZUL = "#2a78d6"
NARANJA = "#eb6834"
TINTA = "#0b0b0b"
TINTA_SUAVE = "#52514e"
GRILLA = "#e1e0d9"

FIGSIZE = (7.0, 4.3)
DPI = 200


def _miles(valor, _pos):
    """12000000 -> "12 000 000" (sin el 1e7 en la esquina, que no se entiende)."""
    return f"{valor:,.0f}".replace(",", " ")


def _ejes(titulo, etiqueta_x, etiqueta_y):
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_title(titulo, color=TINTA, fontsize=11, loc="left", pad=12)
    ax.set_xlabel(etiqueta_x, color=TINTA_SUAVE, fontsize=9)
    ax.set_ylabel(etiqueta_y, color=TINTA_SUAVE, fontsize=9)
    ax.set_yscale("log")
    ax.grid(True, which="major", color=GRILLA, linewidth=0.8)
    ax.grid(True, which="minor", color=GRILLA, linewidth=0.4, alpha=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#c3c2b7")
    ax.tick_params(colors=TINTA_SUAVE, labelsize=8)
    return fig, ax


def _linea_tolerable(ax, R_T):
    ax.axhline(R_T, color=TINTA_SUAVE, linestyle="--", linewidth=1.2, zorder=1)
    ax.annotate(f"$R_T$ = {R_T:.0e}", xy=(0.995, R_T), xycoords=("axes fraction", "data"),
                ha="right", va="bottom", fontsize=8, color=TINTA_SUAVE)


def curva_sensibilidad(puntos, ruta, etiqueta_x="parámetro",
                       titulo="Sensibilidad del riesgo", tipo=1,
                       escala_x="linear") -> str:
    """Grafica R contra el parámetro barrido (lo que devuelve barridos.barrer).

    escala_x="log" deja los dos ejes logarítmicos: ahí una proporcionalidad
    (como la de R con N_G) se ve como una recta, que es lo que se quiere
    mostrar en el artículo.
    """
    x = [p.valor for p in puntos]
    y = [p.riesgo for p in puntos]
    R_T = puntos[0].R_T

    fig, ax = _ejes(titulo, etiqueta_x, f"$R_{tipo}$  [1/año]")
    if escala_x == "log":
        ax.set_xscale("log")
    ax.plot(x, y, color=AZUL, linewidth=2, marker="o", markersize=5,
            markeredgecolor="white", markeredgewidth=0.8, zorder=3)
    _linea_tolerable(ax, R_T)

    fig.tight_layout()
    fig.savefig(ruta, facecolor="#fcfcfb")
    plt.close(fig)
    return str(ruta)


def dispersion_costo_riesgo(soluciones, ruta,
                            titulo="Costo de las medidas frente al riesgo",
                            tipo=1) -> str:
    """Grafica el costo de cada combinación de medidas contra el riesgo que deja."""
    R_T = soluciones[0].R_T
    cumplen = [s for s in soluciones if s.cumple]
    no_cumplen = [s for s in soluciones if not s.cumple]

    fig, ax = _ejes(titulo, "Costo de instalación", f"$R_{tipo}$  [1/año]")
    if no_cumplen:
        ax.scatter([s.costo for s in no_cumplen], [s.riesgo for s in no_cumplen],
                   s=42, marker="X", color=NARANJA, edgecolor="white", linewidth=0.8,
                   label="No cumple", zorder=3)
    if cumplen:
        ax.scatter([s.costo for s in cumplen], [s.riesgo for s in cumplen],
                   s=42, marker="o", color=AZUL, edgecolor="white", linewidth=0.8,
                   label="Cumple", zorder=4)
    _linea_tolerable(ax, R_T)

    ax.xaxis.set_major_formatter(FuncFormatter(_miles))
    # La leyenda va debajo del marco: dentro siempre termina tapando puntos.
    leyenda = ax.legend(frameon=False, fontsize=8, ncol=2,
                        loc="upper center", bbox_to_anchor=(0.5, -0.18))
    for texto in leyenda.get_texts():
        texto.set_color(TINTA_SUAVE)

    fig.tight_layout()
    fig.savefig(ruta, facecolor="#fcfcfb")
    plt.close(fig)
    return str(ruta)