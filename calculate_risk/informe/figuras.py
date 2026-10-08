"""
Paso 60: las figuras del informe, con matplotlib y sin LaTeX.

Cada función escribe un PNG y devuelve su ruta. Ninguna calcula riesgo ni conoce la
norma: reciben los números YA calculados (área de captación, aportes, riesgos) y los
dibujan. Así una figura nunca puede contradecir al panel.

  mapa_del_sitio()            mapa NASA de N_G con la ubicación en el país
  area_de_captacion()         planta de la estructura con su A_D
  aporte_de_componentes()     de dónde viene el riesgo
  riesgo_contra_tolerable()   el riesgo (antes/después) frente al tolerable

Se usa `Figure` y no `pyplot`: no hay estado global ni ventanas, y no cambia el backend
de quien ya use matplotlib (la pantalla del programa, por ejemplo). Estilo del informe
académico: la misma serif que el PDF (STIX Two), trazos finos en azul oscuro, y rojo o
verde solo para decir si un riesgo cumple, siempre con el valor escrito al lado.

matplotlib es opcional para el informe: quien lo llame captura ImportError y el informe
sale sin figuras, diciéndolo.
"""
import json
import math
from pathlib import Path

import numpy as np
from matplotlib import font_manager, rc_context
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.path import Path as Camino

AZUL = "#2a78d6"
NARANJA = "#eb6834"
GRIS = "#555555"
TINTA = "#0F172A"
TRAZO = "#1E293B"
PIZARRA = "#475569"
LINEA = "#E2E8F0"
ROJO = "#DC2626"
VERDE = "#16A34A"
PALETA = LinearSegmentedColormap.from_list(
    "rayos", ["#f7fbff", "#c6dbef", "#6baed6", AZUL, "#f2a35e", NARANJA, "#8c2d04"])

RUTA_PAISES = str(Path(__file__).resolve().parent.parent.parent / "archivos" / "paises.geojson")
DPI = 300
CARPETA_FUENTES = Path(__file__).resolve().parent / "fuentes"
for _archivo in ("STIXTwoText-Regular", "STIXTwoText-Bold", "STIXTwoText-Italic",
                 "STIXTwoText-BoldItalic"):
    if (CARPETA_FUENTES / f"{_archivo}.ttf").exists():
        font_manager.fontManager.addfont(str(CARPETA_FUENTES / f"{_archivo}.ttf"))
ESTILO = {"font.family": "serif", "font.serif": ["STIX Two Text", "DejaVu Serif"],
          "mathtext.fontset": "stix", "hatch.linewidth": 0.45,
          "axes.edgecolor": "#888888", "axes.labelcolor": TINTA, "text.color": TINTA,
          "xtick.color": PIZARRA, "ytick.color": PIZARRA}


def _coma(numero: float, decimales: int = 1) -> str:
    return f"{numero:.{decimales}f}".replace(".", ",")


def _cientifico(numero: float) -> str:
    """1e-05 -> '1,0 × 10$^{-5}$' (mathtext), con coma decimal."""
    mantisa, exponente = f"{numero:.1e}".split("e")
    return f"{mantisa.replace('.', ',')} × 10$^{{{int(exponente)}}}$"


def _guardar(figura, ruta, transparente=False):
    figura.savefig(str(ruta), dpi=DPI, transparent=transparente)
    return str(ruta)


def aspecto_geografico(lat: float) -> float:
    """Un grado de longitud mide cos(latitud) veces lo que uno de latitud; sin esta
    corrección el mapa sale estirado y el país no se reconoce."""
    return 1.0 / math.cos(math.radians(lat))


# ---------------------------------------------------------------------------
# Fronteras
# ---------------------------------------------------------------------------

def contornos(ruta: str = RUTA_PAISES) -> list:
    """[(nombre, [arreglo Nx2, ...])]: los contornos exteriores de cada país."""
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    paises = []
    for pais in datos["features"]:
        geometria = pais["geometry"]
        piezas = ([geometria["coordinates"]] if geometria["type"] == "Polygon"
                  else geometria["coordinates"])
        paises.append((pais["properties"].get("NAME", ""),
                       [np.array(pieza[0]) for pieza in piezas]))
    return paises


def pais_que_contiene(paises: list, lat: float, lon: float):
    """El país cuyo contorno contiene el punto; None si cae en el mar."""
    for nombre, anillos in paises:
        for anillo in anillos:
            if Camino(anillo).contains_point((lon, lat)):
                return nombre
    return None


def _extremos(paises, nombre, centro, margen, eje):
    for pais, anillos in paises:
        if pais == nombre:
            valores = np.concatenate([anillo[:, eje] for anillo in anillos])
            return valores.min() - margen, valores.max() + margen
    return centro - 10, centro + 10


# ---------------------------------------------------------------------------
# 1. El mapa
# ---------------------------------------------------------------------------

def mapa_del_sitio(lat: float, lon: float, nombre: str, ruta: str,
                   fraccion_nube_tierra: float = None, ruta_nc: str = None,
                   ruta_paises: str = RUTA_PAISES, margen: float = 4.0) -> str:
    """N_G alrededor del sitio (NASA LIS) y, a la derecha, dónde está en su país.

    La etiqueta de N_G sale de la misma ficha que usa el informe, así que no puede
    diferir. Lanza FueraDeCobertura si el sitio queda fuera de ±38°.
    """
    from netCDF4 import Dataset

    from calculate_risk.norma import densidad
    from calculate_risk.norma.modelo import Emplazamiento

    fraccion = (Emplazamiento().fraccion_nube_tierra
                if fraccion_nube_tierra is None else fraccion_nube_tierra)
    ruta_nc = ruta_nc or densidad.RUTA_POR_DEFECTO
    ficha = densidad.ficha_desde_lat_lon(lat, lon, fraccion, ruta_nc)
    lon = ficha.lon

    with Dataset(ruta_nc, "r") as datos:
        lats = np.array(datos.variables["Latitude"][:])
        lons = np.array(datos.variables["Longitude"][:])
        frd = np.array(datos.variables["VHRFC_LIS_FRD"][:]) * fraccion

    i = np.abs(lats - lat) <= margen
    j = np.abs(lons - lon) <= margen
    recorte = frd[np.ix_(i, j)]
    paises = contornos(ruta_paises)
    pais_del_sitio = pais_que_contiene(paises, lat, lon)

    with rc_context(ESTILO):
        figura = Figure(figsize=(6.4, 4.6))
        ax = figura.add_axes([0.07, 0.10, 0.60, 0.82])

        tope = float(np.percentile(recorte, 97)) or 1.0
        imagen = ax.pcolormesh(lons[j], lats[i], recorte, cmap=PALETA, shading="auto",
                               vmin=0, vmax=tope)
        niveles = [n for n in (2, 4, 6, 8, 12) if recorte.min() < n < recorte.max()]
        if niveles:
            lineas = ax.contour(lons[j], lats[i], recorte, levels=niveles,
                                colors="#444444", linewidths=0.35, alpha=0.5)
            ax.clabel(lineas, fmt="%.0f", fontsize=6)
        for _, anillos in paises:
            for anillo in anillos:
                ax.plot(anillo[:, 0], anillo[:, 1], color="#222222", lw=0.9, zorder=6)

        ax.plot(lon, lat, marker="o", ms=8, mfc="none", mec="#111111", mew=1.7, zorder=8)
        ax.plot(lon, lat, marker="+", ms=12, color="#111111", mew=1.2, zorder=8)
        ax.annotate(f"{nombre}\n$N_G$ = {_coma(ficha.N_G, 2)} rayos/km²·año",
                    xy=(lon, lat), xytext=(14, 16), textcoords="offset points",
                    fontsize=8, color="#111111", zorder=9,
                    bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#777777",
                              lw=0.6, alpha=0.92),
                    arrowprops=dict(arrowstyle="-", color="#444444", lw=0.8))

        ax.set_xlim(lon - margen, lon + margen)
        ax.set_ylim(lat - margen, lat + margen)
        ax.set_aspect(aspecto_geografico(lat))
        ax.set_xlabel("longitud [°]", fontsize=8)
        ax.set_ylabel("latitud [°]", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title("Densidad de descargas a tierra en el emplazamiento",
                     fontsize=9.5, color="#333333", pad=8)
        barra = figura.colorbar(imagen, ax=ax, fraction=0.05, pad=0.02, extend="max")
        barra.set_label("$N_G$ [rayos/km²·año]", fontsize=8)
        barra.ax.tick_params(labelsize=7)

        # Dónde está, en su país
        loc = figura.add_axes([0.775, 0.42, 0.20, 0.50])
        for pais, anillos in paises:
            propio = pais == pais_del_sitio
            for anillo in anillos:
                loc.fill(anillo[:, 0], anillo[:, 1],
                         color="#cfe0f2" if propio else "#ececec", zorder=0)
                loc.plot(anillo[:, 0], anillo[:, 1], color="#777777",
                         lw=0.7 if propio else 0.4, zorder=1)
        loc.add_patch(Rectangle((lon - margen, lat - margen), 2 * margen, 2 * margen,
                                fill=False, ec=ROJO, lw=1.3, zorder=10))
        loc.plot(lon, lat, marker="o", ms=3.5, color=ROJO, zorder=11)
        loc.set_xlim(*_extremos(paises, pais_del_sitio, lon, 1.5, 0))
        loc.set_ylim(*_extremos(paises, pais_del_sitio, lat, 1.5, 1))
        loc.set_aspect(aspecto_geografico(lat))
        loc.set_xticks([])
        loc.set_yticks([])
        loc.set_title("Ubicación", fontsize=8, color="#333333", pad=3)
        for lado in loc.spines.values():
            lado.set_color("#999999")
            lado.set_linewidth(0.6)

        figura.text(0.775, 0.30,
                    f"Fuente: NASA LIS/OTD\nVHRFC 1998–2013\nFracción nube-tierra:\n"
                    f"{_coma(fraccion, 3)}\n\nFronteras: Natural\nEarth (dominio\npúblico)",
                    fontsize=6.8, color="#666666", va="top")
        return _guardar(figura, ruta)


# ---------------------------------------------------------------------------
# 2. El área de captación
# ---------------------------------------------------------------------------

def _cota(ax, p, q, texto, lado, desvio, rotar=False):
    """Una cota de plano: dos líneas de extensión finas, la línea de cota con flechas en
    los extremos y el valor en el medio. `lado` y `desvio` dicen hacia dónde y cuánto se
    separa de la pieza (unidades del dibujo)."""
    (x1, y1), (x2, y2) = p, q
    horizontal = abs(y2 - y1) < abs(x2 - x1)
    if horizontal:
        y = (y1 + lado * desvio)
        for x, y0 in ((x1, y1), (x2, y2)):
            ax.plot([x, x], [y0, y + lado * desvio * 0.12], color=PIZARRA, lw=0.45, zorder=2)
        a, b = (x1, y), (x2, y)
    else:
        x = (x1 + lado * desvio)
        for y, x0 in ((y1, x1), (y2, x2)):
            ax.plot([x0, x + lado * desvio * 0.12], [y, y], color=PIZARRA, lw=0.45, zorder=2)
        a, b = (x, y1), (x, y2)
    ax.annotate("", xy=b, xytext=a, zorder=4,
                arrowprops=dict(arrowstyle="<|-|>", color=TRAZO, lw=0.6,
                                shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, texto, fontsize=7.4, color=TRAZO,
            ha="center", va="center", rotation=90 if rotar else 0, zorder=5,
            bbox=dict(boxstyle="square,pad=0.18", fc="white", ec="none"))


def area_de_captacion(L: float, W: float, H: float, A_D: float, ruta: str,
                      lineas=(), saliente_gobierna: bool = False) -> str:
    """Planta de la estructura y su área de captación equivalente, como un plano.

    Trazos finos, cotas con líneas de extensión y flechas, y la envolvente de A_D achurada.
    Se dibuja la ampliación de 3H en todo el contorno (ec. A.2). Si el saliente del
    techo es lo que fija A_D (ec. A.3) se dibuja el círculo de área A_D en su lugar.
    `A_D` llega calculado: la figura solo lo escribe.
    """
    d = 3 * H
    with rc_context(ESTILO):
        figura = Figure(figsize=(6.2, 4.3), facecolor="white")
        ax = figura.add_axes([0.0, 0.0, 1.0, 1.0])
        ax.set_axis_off()

        if saliente_gobierna:
            radio = math.sqrt(A_D / math.pi)
            t = np.linspace(0, 2 * math.pi, 200)
            x = L / 2 + radio * np.cos(t)
            y = W / 2 + radio * np.sin(t)
        else:
            # Rectángulo con esquinas redondeadas, recorrido en sentido antihorario.
            partes_x, partes_y = [], []
            for (cx, cy), (desde, hasta) in (((L, 0), (-90, 0)), ((L, W), (0, 90)),
                                             ((0, W), (90, 180)), ((0, 0), (180, 270))):
                angulo = np.radians(np.linspace(desde, hasta, 40))
                partes_x.append(cx + d * np.cos(angulo))
                partes_y.append(cy + d * np.sin(angulo))
            x, y = np.concatenate(partes_x), np.concatenate(partes_y)
            x, y = np.append(x, x[0]), np.append(y, y[0])
        x_min, x_max, y_min, y_max = x.min(), x.max(), y.min(), y.max()
        ax.fill(x, y, fill=False, hatch="//////", edgecolor="#94A3B8", linewidth=0, zorder=1)
        ax.plot(x, y, color=TRAZO, lw=0.8, ls=(0, (5, 3)), zorder=2)

        ax.add_patch(Rectangle((0, 0), L, W, facecolor="white", edgecolor=TRAZO,
                               lw=1.3, zorder=3))
        vertical = W > 1.6 * L
        ax.text(L / 2, W / 2, f"ESTRUCTURA\n{L:g} × {W:g} × {H:g} m", ha="center", va="center",
                fontsize=7.2, color=TRAZO, zorder=4, linespacing=1.5,
                rotation=90 if vertical else 0)

        paso = max(x_max - x_min, y_max - y_min)
        if not saliente_gobierna:
            _cota(ax, (L, W / 2), (L + d, W / 2), f"3H = {d:g} m", +1, 0.0)
        _cota(ax, (0, 0), (L, 0), f"L = {L:g} m", -1, -y_min + 0.10 * paso)
        _cota(ax, (0, 0), (0, W), f"W = {W:g} m", -1, -x_min + 0.07 * paso, rotar=True)
        ax.text(x_max + 0.08 * paso, y_max + 0.03 * paso,
                f"$A_D$ = {_coma(A_D, 1)} m²" + (" (saliente)" if saliente_gobierna else ""),
                fontsize=8.6, color=TINTA, ha="right", va="bottom", zorder=6,
                bbox=dict(boxstyle="square,pad=0.4", fc="white", ec=TRAZO, lw=0.7))

        for k, nombre in enumerate(lineas):
            y0 = W * (0.78 - 0.16 * k)
            ax.annotate("", xy=(x_min - 0.02 * paso, y0), xytext=(x_min - 0.30 * paso, y0),
                        arrowprops=dict(arrowstyle="-|>", color=TRAZO, lw=0.8,
                                        shrinkA=0, shrinkB=0, mutation_scale=7))
            ax.text(x_min - 0.30 * paso, y0 + 0.012 * paso, f"línea: {nombre}", fontsize=7.2,
                    color=TRAZO, ha="left", va="bottom")

        ax.set_aspect("equal")
        ax.set_xlim(x_min - 0.42 * paso, x_max + 0.12 * paso)
        ax.set_ylim(y_min - 0.20 * paso, max(y_max, W) + 0.16 * paso)
        figura.add_artist(Rectangle((0.004, 0.004), 0.992, 0.992, fill=False, ec=TRAZO,
                                    lw=0.8, transform=figura.transFigure))
        figura.text(0.016, 0.02, "PLANTA · COTAS EN METROS · SIN ESCALA NUMÉRICA", fontsize=5.8,
                    color=PIZARRA)
        return _guardar(figura, ruta)


# ---------------------------------------------------------------------------
# 3. De dónde viene el riesgo
# ---------------------------------------------------------------------------

def aporte_de_componentes(aportes, ruta: str, tipo: int = 1) -> str:
    """Barras horizontales redondeadas con la parte que aporta cada componente.

    `aportes` es una lista de (rótulo, valor [1/año]); los ceros no se dibujan. El porcentaje
    va dentro de la barra (fuera si la barra es muy corta) y no hay eje numérico. La
    mayor va en rojo: es donde una medida de protección rinde.
    """
    aportes = sorted(((r, v) for r, v in aportes if v > 0), key=lambda a: -a[1])
    if not aportes:
        raise ValueError("No hay ningún componente con riesgo mayor que cero.")
    total = sum(v for _, v in aportes)
    partes = [100 * v / total for _, v in aportes]
    n = len(aportes)

    with rc_context(ESTILO):
        alto = max(1.5, 0.40 * n + 0.45)
        figura = Figure(figsize=(6.2, alto), facecolor="white")
        izq, ancho_ejes, abajo, alto_ejes = 0.075, 0.915, 0.04, 0.92
        ax = figura.add_axes([izq, abajo, ancho_ejes, alto_ejes])
        largo = 116.0                      # 100 de barra + el valor en 1/año a la derecha
        ax.set_xlim(0, largo)
        ax.set_ylim(n - 0.5, -0.5)
        # el redondeo se mide en pulgadas: el mismo alto y ancho de esquina en x y en y
        x_por_pulgada = largo / (6.2 * ancho_ejes)
        y_por_pulgada = n / (alto * alto_ejes)
        aspecto = y_por_pulgada / x_por_pulgada
        medio_alto = 0.30
        radio = medio_alto / aspecto

        def barra(y, ancho, color):
            ancho = max(ancho, 2 * radio)
            ax.add_patch(FancyBboxPatch((0, y - medio_alto), ancho, 2 * medio_alto,
                                        boxstyle=f"round,pad=0,rounding_size={radio}",
                                        mutation_aspect=aspecto, fc=color, ec="none"))

        for i, ((rotulo, valor), parte) in enumerate(zip(aportes, partes)):
            barra(i, 100, LINEA)
            barra(i, parte, ROJO if i == 0 else PIZARRA)
            porcentaje = "< 0,1 %" if parte < 0.1 else f"{_coma(parte, 1)} %"
            if parte >= 14:
                ax.text(parte - 1.6, i, porcentaje, ha="right", va="center", fontsize=8,
                        color="white", fontweight="bold")
            else:
                ax.text(max(parte, 2 * radio) + 1.6, i, porcentaje, ha="left", va="center",
                        fontsize=8, color=TINTA, fontweight="bold")
            ax.text(largo, i, f"{valor:.2e} 1/año".replace(".", ","), ha="right", va="center",
                    fontsize=7.2, color=PIZARRA)
        ax.set_yticks(range(n))
        ax.set_yticklabels([r for r, _ in aportes], fontsize=9)
        ax.tick_params(length=0, pad=3)
        ax.set_xticks([])
        for lado in ax.spines.values():
            lado.set_visible(False)
        return _guardar(figura, ruta)


# ---------------------------------------------------------------------------
# 4. El veredicto
# ---------------------------------------------------------------------------

def riesgo_contra_tolerable(barras, tolerable: float, ruta: str, tipo: int = 1) -> str:
    """El riesgo de cada escenario frente al tolerable, en escala logarítmica.

    `barras` es una lista de (rótulo, riesgo). Rojo si supera el tolerable, verde si no; el
    valor va escrito sobre cada barra y no hay eje numérico.
    """
    if not barras or tolerable <= 0 or any(v <= 0 for _, v in barras):
        raise ValueError("Hacen falta riesgos y un tolerable mayores que cero.")
    valores = [v for _, v in barras]
    with rc_context(ESTILO):
        figura = Figure(figsize=(6.2, 2.4), facecolor="white")
        ax = figura.add_axes([0.03, 0.17, 0.94, 0.78])
        rectas = ax.bar([r for r, _ in barras], valores, width=0.42,
                        color=[VERDE if v <= tolerable else ROJO for v in valores])
        ax.axhline(tolerable, color=TRAZO, lw=0.9, ls=(0, (5, 3)))
        ax.text(0.995, tolerable * 1.18, f"$R_T$ = {_cientifico(tolerable)}",
                transform=ax.get_yaxis_transform(), fontsize=8, color=TRAZO, ha="right")
        for recta, valor in zip(rectas, valores):
            ax.text(recta.get_x() + recta.get_width() / 2, valor * 1.18,
                    _cientifico(valor), ha="center", fontsize=8.4, color=TINTA)
        ax.set_yscale("log")
        ax.set_ylim(min(valores + [tolerable]) / 4, max(valores + [tolerable]) * 5)
        ax.set_yticks([])
        ax.minorticks_off()
        ax.tick_params(axis="x", length=0, labelsize=8.4)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color("#94A3B8")
        return _guardar(figura, ruta)
