"""
Paso 40: memoria de cálculo en LaTeX (reemplaza el informe PDF viejo).

Genera el documento que se entrega en un proyecto: datos de entrada, áreas y
frecuencias, componentes de riesgo, veredicto contra el riesgo tolerable y,
si se le pasan, las medidas de protección recomendadas (Paso 38) y las
figuras de sensibilidad (Paso 39).

Cubre lo mismo que el informe viejo (PDF_Creator.py) y agrega lo que ese no
tenía: los cuatro riesgos con su R_T real, las medidas recomendadas con su
costo-beneficio, y las figuras.

Sobre LaTeX: el texto que escribe el usuario en la pantalla (nombre del
proyecto, dirección...) puede traer caracteres que LaTeX interpreta como
órdenes (&, %, _, $...). Por eso TODO texto de entrada pasa por `escapar()`.
"""
import os
import subprocess

from calculate_risk.norma import riesgos

# Los componentes, con el nombre que les da la norma
NOMBRES_COMPONENTES = {
    "R_A": "Lesiones a seres vivos por descarga en la estructura",
    "R_B": "Daño físico por descarga en la estructura",
    "R_C": "Falla de sistemas internos por descarga en la estructura",
    "R_M": "Falla de sistemas internos por descarga cerca de la estructura",
    "R_U": "Lesiones a seres vivos por descarga en una línea",
    "R_V": "Daño físico por descarga en una línea",
    "R_W": "Falla de sistemas internos por descarga en una línea",
    "R_Z": "Falla de sistemas internos por descarga cerca de una línea",
}

NOMBRES_RIESGOS = {
    1: "$R_1$ — Pérdida de vidas humanas",
    2: "$R_2$ — Pérdida de servicio público esencial",
    3: "$R_3$ — Pérdida de patrimonio cultural",
    4: "$R_4$ — Pérdida económica",
}

_ESPECIALES = {
    "\\": r"\textbackslash{}",
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def escapar(texto) -> str:
    """Deja un texto listo para meter en LaTeX sin que rompa la compilación."""
    salida = []
    for caracter in str(texto):
        salida.append(_ESPECIALES.get(caracter, caracter))
    return "".join(salida)


def numero(valor, cifras=3) -> str:
    """Un número en notación científica y con coma decimal: 2,51 x 10^{-5}."""
    if valor == 0:
        return "0"
    texto = f"{valor:.{cifras}e}"          # "2.506e-05"
    mantisa, exponente = texto.split("e")
    mantisa = mantisa.rstrip("0").rstrip(".").replace(".", "{,}")
    exp = int(exponente)
    if exp == 0:
        return mantisa
    return f"{mantisa} \\times 10^{{{exp}}}"


def plano(valor, cifras=4) -> str:
    """Una magnitud normal (metros, N_G, un coeficiente): 15, 0,5, 2577,88.

    numero() es para los riesgos, que se mueven en ordenes de magnitud; poner
    "1,5 x 10^1" donde dice 15 m solo estorba.
    """
    texto = f"{valor:,.{cifras}f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(",", " ").replace(".", "{,}")


def _fila(etiqueta, valor) -> str:
    """OJO: no escapa. Las etiquetas son LaTeX escrito por nosotros (llevan
    $A_D$, $N_G$...). El texto que viene del usuario se escapa en su sitio."""
    return f"{etiqueta} & {valor} \\\\\n"


def _tabla_datos_proyecto(proyecto) -> str:
    if not proyecto:
        return ""
    filas = "".join(_fila(escapar(k), escapar(v)) for k, v in proyecto.items())
    return (
        "\\section{Datos del proyecto}\n"
        "\\begin{tabular}{@{}lp{9cm}@{}}\n\\toprule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_entrada(datos) -> str:
    filas = (
        _fila("Longitud de la estructura $L$ [m]", f"${plano(datos['L'])}$")
        + _fila("Ancho de la estructura $W$ [m]", f"${plano(datos['W'])}$")
        + _fila("Altura de la estructura $H$ [m]", f"${plano(datos['H'])}$")
        + _fila("Altura del saliente $H_P$ [m]", f"${plano(datos['H_P'])}$")
        + _fila("Densidad de descargas $N_G$ [1/km$^2\\cdot$año]", f"${plano(datos['DDT'])}$")
        + _fila("Factor de localización $C_D$ (Tabla A.1)", f"${plano(datos['C_d'])}$")
        + _fila("Factor ambiental $C_E$ (Tabla A.4)", f"${plano(datos['C_e'])}$")
        + _fila("Probabilidad $P_B$ (Tabla B.2, según el SPCR)", f"${plano(1 - datos['E'])}$")
    )
    return (
        "\\section{Datos de entrada}\n"
        "\\begin{tabular}{@{}lr@{}}\n\\toprule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_areas(resultados) -> str:
    filas = (
        _fila("$A_D$ — colección de la estructura (ec. A.2) [m$^2$]",
              f"${plano(resultados['A_d'], 2)}$")
        + _fila("$A_M$ — descargas cerca de la estructura (ec. A.7) [m$^2$]",
                f"${plano(resultados['A_m'], 2)}$")
        + _fila("$N_D$ — descargas en la estructura (ec. A.4) [1/año]",
                f"${numero(resultados['N_D'])}$")
        + _fila("$N_M$ — descargas cerca de la estructura (ec. A.6) [1/año]",
                f"${numero(resultados['N_M'])}$")
        + _fila("$N_L$ — descargas en la línea aérea (ec. A.8) [1/año]",
                f"${numero(resultados['N_L1'])}$")
        + _fila("$N_I$ — descargas cerca de la línea aérea (ec. A.10) [1/año]",
                f"${numero(resultados['N_I1'])}$")
    )
    return (
        "\\section{Áreas de colección y frecuencia de eventos}\n"
        "\\begin{tabular}{@{}lr@{}}\n\\toprule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_componentes(resultados, tipos=(1, 2, 3, 4)) -> str:
    cabecera = " & ".join(f"$R_{t}$" for t in tipos)
    filas = ""
    for componente in riesgos.COMPONENTES:
        valores = " & ".join(
            f"${numero(resultados[f'{componente}{t}'])}$" for t in tipos
        )
        filas += (f"${componente.replace('_', '_{')}}}$ & "
                  f"{escapar(NOMBRES_COMPONENTES[componente])} & {valores} \\\\\n")
    return (
        "\\section{Componentes de riesgo}\n"
        "\\begin{tabular}{@{}llrrrr@{}}\n\\toprule\n"
        f" & Componente & {cabecera} \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_veredicto(resultados, tipos=(1, 2, 3, 4)) -> str:
    filas = ""
    for t in tipos:
        R = resultados[f"R_{t}"]
        R_T = resultados[f"R_T{t}"]
        veredicto = "Cumple" if R <= R_T else "\\textbf{No cumple}"
        filas += (f"{NOMBRES_RIESGOS[t]} & ${numero(R)}$ & "
                  f"${numero(R_T)}$ & {veredicto} \\\\\n")
    return (
        "\\section{Resultado}\n"
        "\\begin{tabular}{@{}lrrl@{}}\n\\toprule\n"
        "Riesgo & Calculado & Tolerable & Veredicto \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_soluciones(soluciones, cuantas=10) -> str:
    if not soluciones:
        return ""
    con_economia = soluciones[0].S_M is not None
    columnas = "@{}p{8cm}rrr@{}" if con_economia else "@{}p{9cm}rr@{}"
    cabecera = ("Medidas & $R$ & Costo & $S_M$ \\\\" if con_economia
                else "Medidas & $R$ & Costo \\\\")

    filas = ""
    for s in soluciones[:cuantas]:
        nombres = escapar(" + ".join(s.nombres) or "(sin medidas)")
        # OJO: el separador de miles se cambia SOLO en el dinero. Si se aplica
        # a toda la fila, se come la coma decimal de numero() ("2{,}233").
        costo = f"{s.costo:,.0f}".replace(",", "~")
        filas += f"{nombres} & ${numero(s.riesgo)}$ & {costo}"
        if con_economia:
            filas += " & " + f"{s.S_M:,.0f}".replace(",", "~")
        filas += " \\\\\n"

    return (
        "\\section{Medidas de protección recomendadas}\n"
        "Combinaciones que llevan el riesgo por debajo del valor tolerable, "
        "ordenadas según el análisis del Anexo D.\n\n"
        f"\\begin{{tabular}}{{{columnas}}}\n\\toprule\n"
        f"{cabecera}\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _figuras(figuras) -> str:
    if not figuras:
        return ""
    bloques = ""
    for ruta, pie in figuras:
        nombre = os.path.basename(str(ruta))
        bloques += (
            "\\begin{figure}[h]\n\\centering\n"
            f"\\includegraphics[width=0.85\\textwidth]{{{nombre}}}\n"
            f"\\caption{{{escapar(pie)}}}\n"
            "\\end{figure}\n\n"
        )
    return "\\section{Análisis de sensibilidad}\n" + bloques



# Cada componente: su ecuación en la norma y de qué factores sale.
# R = N x P x L
DESARROLLO = {
    "R_A": ("6", "N_D", "P_A", "L_A"),
    "R_B": ("7", "N_D", "P_B", "L_B"),
    "R_C": ("8", "N_D", "P_C", "L_C"),
    "R_M": ("9", "N_M", "P_M", "L_M"),
    "R_U": ("10", "N_L + N_{DJ}", "P_U", "L_U"),
    "R_V": ("11", "N_L + N_{DJ}", "P_V", "L_V"),
    "R_W": ("12", "N_L + N_{DJ}", "P_W", "L_W"),
    "R_Z": ("13", "N_I", "P_Z", "L_Z"),
}


def _valor_factor(nombre, detalle, linea):
    """Busca un factor en el detalle: primero en la zona, luego en la línea."""
    if nombre == "N_L + N_{DJ}":
        return linea["N_L"] + linea["N_DJ"]
    if nombre in detalle:
        return detalle[nombre]
    return linea[nombre]


def _desarrollo(detalle, R, tipo) -> str:
    """El cálculo paso a paso: la fórmula de cada componente con sus números.

    Esto es lo que diferencia una memoria de cálculo de una hoja de
    resultados: se ve de dónde sale cada valor.
    """
    lineas = list(detalle["lineas"].items())
    nombre_linea, linea = lineas[0] if lineas else (None, {})

    texto = (
        "\\section{Desarrollo del cálculo}\n"
        "Cada componente es el producto de tres factores: la frecuencia de "
        "eventos $N$, la probabilidad de daño $P$ y la pérdida $L$.\n\n"
    )
    if nombre_linea and len(lineas) > 1:
        texto += (f"Los componentes de línea se desarrollan para "
                  f"\\textit{{{escapar(nombre_linea)}}}; el valor final suma "
                  f"las {len(lineas)} líneas.\n\n")

    for componente, (ec, n, p, l) in DESARROLLO.items():
        letra = componente[2]
        if componente not in detalle["aplica"]:
            texto += (f"$R_{{{letra}}}$ no interviene en $R_{tipo}$ "
                      f"(numeral 4.3).\n\n")
            continue
        try:
            vn = _valor_factor(n, detalle, linea)
            vp = _valor_factor(p, detalle, linea)
            vl = _valor_factor(l, detalle, linea)
        except KeyError:
            continue
        texto += (
            f"$R_{{{letra}}}$ — ecuación ({ec}):\n"
            "\\begin{equation*}\n"
            f"R_{{{letra}}} = ({n}) \\times {p} \\times {l}"
            f" = {numero(vn)} \\times {numero(vp)} \\times {numero(vl)}"
            f" = \\mathbf{{{numero(R[componente])}}}\n"
            "\\end{equation*}\n\n"
        )
    return texto


def _de_donde_viene(R, tipo) -> str:
    """Qué componente aporta cuánto: lo primero que mira un diseñador."""
    total = R["total"]
    if not total:
        return ""
    ordenados = sorted(
        ((c, v) for c, v in R.items() if c in NOMBRES_COMPONENTES and v),
        key=lambda cv: -cv[1],
    )
    filas = ""
    for componente, valor in ordenados:
        porcentaje = valor / total * 100
        filas += (f"${componente.replace('_', '_{')}}}$ & "
                  f"${numero(valor)}$ & ${porcentaje:.1f}$\\,\\% \\\\\n")
    return (
        f"\\subsection*{{De dónde viene $R_{tipo}$}}\n"
        "\\begin{tabular}{@{}lrr@{}}\n\\toprule\n"
        "Componente & Valor & Participación \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )



PREAMBULO = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6em}
"""


def memoria_tex(datos, resultados, proyecto=None, soluciones=None, figuras=None,
                tipos=(1, 2, 3, 4), detalle=None, R_zona=None,
                tipo_desarrollado=1) -> str:
    """Arma el documento LaTeX completo y lo devuelve como texto.

    datos: el diccionario de la pantalla (VAR).
    resultados: lo que devuelve adaptador.resultados_pantalla(datos).
    proyecto: {"Proyecto": ..., "Dirección": ...} (opcional).
    soluciones: lo que devuelve medidas.explorar() (opcional).
    figuras: [(ruta_png, pie_de_figura), ...] (opcional).
    detalle, R_zona: el "_detalle" y los componentes de una zona, para escribir
        el desarrollo del cálculo (lo que hace que sea una memoria y no una
        hoja de resultados). Salen de riesgos.evaluar(...)[tipo]["zonas"][nombre].
    """
    cuerpo = (
        _tabla_datos_proyecto(proyecto)
        + _tabla_entrada(datos)
        + _tabla_areas(resultados)
        + _tabla_componentes(resultados, tipos)
        + _tabla_veredicto(resultados, tipos)
        + (_desarrollo(detalle, R_zona, tipo_desarrollado)
           if detalle and R_zona else "")
        + (_de_donde_viene(R_zona, tipo_desarrollado) if R_zona else "")
        + _tabla_soluciones(soluciones)
        + _figuras(figuras)
    )
    return (
        PREAMBULO
        + "\\title{Memoria de cálculo de riesgo por rayo\\\\"
          "\\large NTC 4552-2:2023}\n\\date{\\today}\n"
          "\\begin{document}\n\\maketitle\n\n"
        + cuerpo
        + "\\end{document}\n"
    )


def escribir_memoria(ruta, datos, resultados, **kwargs) -> str:
    """Escribe el .tex en disco y devuelve su ruta."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(memoria_tex(datos, resultados, **kwargs))
    return str(ruta)


def compilar(ruta_tex, salida=None) -> str:
    """Compila el .tex a PDF con pdflatex. Devuelve la ruta del PDF.

    Se corre dos veces porque LaTeX necesita la segunda pasada para las
    referencias. Si pdflatex no está instalado, avisa claramente.
    """
    ruta_tex = str(ruta_tex)
    carpeta = salida or os.path.dirname(ruta_tex) or "."
    try:
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", carpeta, ruta_tex],
                check=True, capture_output=True,
            )
    except FileNotFoundError:
        raise RuntimeError("No se encontró pdflatex: hay que instalar LaTeX") from None
    except subprocess.CalledProcessError as error:
        salida_latex = error.stdout.decode("utf-8", "replace")[-2000:]
        raise RuntimeError(f"pdflatex falló:\n{salida_latex}") from None

    return os.path.join(carpeta,
                        os.path.basename(ruta_tex).replace(".tex", ".pdf"))


def memoria_desde_pantalla(ruta, datos, proyecto=None, tipo_desarrollado=1,
                           soluciones=None, figuras=None) -> str:
    """Escribe la memoria directamente desde el diccionario de la pantalla.

    Hace por dentro los tres pasos (resultados, caso, detalle de la zona) para
    que la pantalla solo tenga que llamar a una función.
    """
    from calculate_risk.norma import riesgos
    from calculate_risk.norma.adaptador import caso_desde_pantalla, resultados_pantalla

    resultados = resultados_pantalla(datos)
    caso = caso_desde_pantalla(datos, tipo=tipo_desarrollado)
    r = riesgos.evaluar(caso["estructura"], caso["lineas"], caso["zonas"],
                        caso["N_G"], tipos=(tipo_desarrollado,))[tipo_desarrollado]
    zona = r["zonas"][caso["zonas"][0].nombre]

    return escribir_memoria(ruta, datos, resultados, proyecto=proyecto,
                            detalle=zona["_detalle"], R_zona=zona,
                            tipo_desarrollado=tipo_desarrollado,
                            soluciones=soluciones, figuras=figuras)