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
    if soluciones is None:            # no se pidieron
        return ""
    if not soluciones:                # se pidieron y NO hay: hay que decirlo,
        return (                      # callarlo haria pensar que no hacen falta
            "\\section{Medidas de protección recomendadas}\n"
            "\\textbf{Ninguna combinación de las medidas contempladas lleva el "
            "riesgo por debajo del valor tolerable.} Hay que revisar el caso: "
            "reducir la longitud o la exposición de las líneas, dividir la "
            "estructura en zonas, o reconsiderar los valores de pérdida "
            "adoptados.\n\n"
        )
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


# Densidades de descarga para la curva de sensibilidad del informe: de muy baja
# a muy alta actividad, para ver con cuánto margen cumple (o deja de cumplir).
N_G_SENSIBILIDAD = (0.5, 1, 2, 4, 8, 16, 32)

# ---------------------------------------------------------------------------
# Paso 50: la memoria desde un caso del modelo, con varias zonas y líneas
# ---------------------------------------------------------------------------

def _llaves_planas(por_tipo: dict) -> dict:
    """{tipo: resultado} -> las llaves planas que usan las tablas de arriba.

    Las tablas de componentes y de veredicto nacieron leyendo el diccionario
    de la pantalla vieja (R_A1, R_1, R_T1...). En vez de reescribirlas, se
    traduce: el contenido es el mismo.
    """
    planas = {}
    for tipo, r in por_tipo.items():
        for componente in riesgos.COMPONENTES:
            planas[f"{componente}{tipo}"] = r[componente]
        planas[f"R_{tipo}"] = r["total"]
        planas[f"R_T{tipo}"] = r["R_T"]
    return planas


def _tabla_estructura(estructura, N_G) -> str:
    filas = (
        _fila("Longitud de la estructura $L$ [m]", f"${plano(estructura.L)}$")
        + _fila("Ancho de la estructura $W$ [m]", f"${plano(estructura.W)}$")
        + _fila("Altura de la estructura $H$ [m]", f"${plano(estructura.H)}$")
        + _fila("Altura del saliente $H_P$ [m]", f"${plano(estructura.H_p)}$")
        + _fila("Densidad de descargas $N_G$ [1/km$^2\\cdot$año]", f"${plano(N_G)}$")
        + _fila("Factor de localización $C_D$ (Tabla A.1)", f"${plano(estructura.C_D)}$")
        + _fila("Personas en la estructura $n_t$", f"${plano(estructura.n_t)}$")
    )
    return (
        "\\section{Datos de entrada}\n\\subsection*{Estructura}\n"
        "\\begin{tabular}{@{}lr@{}}\n\\toprule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_zonas(zonas) -> str:
    """Una fila por zona. Con una sola zona sigue teniendo sentido."""
    filas = ""
    for zona in zonas:
        filas += (f"{escapar(zona.nombre)} & ${plano(zona.n_z)}$ & "
                  f"${plano(zona.t_z)}$ & ${numero(zona.P_B)}$ & "
                  f"${numero(zona.r_f)}$ & ${numero(zona.r_p)}$ & "
                  f"${numero(zona.L_F)}$ \\\\\n")
    return (
        f"\\subsection*{{Zonas ({len(zonas)})}}\n"
        "\\begin{tabular}{@{}lrrrrrr@{}}\n\\toprule\n"
        "Zona & $n_z$ & $t_z$ [h] & $P_B$ & $r_f$ & $r_p$ & $L_F$ \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_lineas(lineas) -> str:
    if not lineas:
        return ("\\subsection*{Líneas}\n"
                "La estructura no tiene líneas de servicio conectadas, así que "
                "los componentes $R_U$, $R_V$, $R_W$ y $R_Z$ no intervienen.\n\n")
    filas = ""
    for linea in lineas:
        vecina = "sí" if linea.adyacente is not None else "no"
        filas += (f"{escapar(linea.nombre)} & ${plano(linea.L_L)}$ & "
                  f"${numero(linea.C_I)}$ & ${numero(linea.C_T)}$ & "
                  f"${numero(linea.C_E)}$ & ${plano(linea.U_W)}$ & "
                  f"${numero(linea.P_LD)}$ & ${numero(linea.P_LI)}$ & "
                  f"{vecina} \\\\\n")
    return (
        f"\\subsection*{{Líneas ({len(lineas)})}}\n"
        "\\begin{tabular}{@{}lrrrrrrrl@{}}\n\\toprule\n"
        "Línea & $L_L$ [m] & $C_I$ & $C_T$ & $C_E$ & $U_W$ [kV] & "
        "$P_{LD}$ & $P_{LI}$ & Vecina \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def _tabla_areas_caso(detalle) -> str:
    """Áreas y frecuencias sacadas del _detalle que devuelve el motor.

    Ahí ya están A_D, N_D y N_M de la estructura, y N_L, N_I y N_DJ de cada
    línea por separado: no hay que suponer que hay una sola.
    """
    filas = (
        _fila("$A_D$ — colección de la estructura (ec. A.2) [m$^2$]",
              f"${plano(detalle['A_D'], 2)}$")
        + _fila("$N_D$ — descargas en la estructura (ec. A.4) [1/año]",
                f"${numero(detalle['N_D'])}$")
        + _fila("$N_M$ — descargas cerca de la estructura (ec. A.6) [1/año]",
                f"${numero(detalle['N_M'])}$")
    )
    por_linea = ""
    for nombre, linea in detalle["lineas"].items():
        por_linea += (f"{escapar(nombre)} & ${numero(linea['N_L'])}$ & "
                      f"${numero(linea['N_I'])}$ & ${numero(linea['N_DJ'])}$ \\\\\n")
    tabla_lineas = ""
    if por_linea:
        tabla_lineas = (
            "\\begin{tabular}{@{}lrrr@{}}\n\\toprule\n"
            "Línea & $N_L$ (ec. A.8) & $N_I$ (ec. A.10) & $N_{DJ}$ (ec. A.5) \\\\\n"
            "\\midrule\n"
            f"{por_linea}"
            "\\bottomrule\n\\end{tabular}\n\n"
        )
    return (
        "\\section{Áreas de colección y frecuencia de eventos}\n"
        "\\begin{tabular}{@{}lr@{}}\n\\toprule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
        f"{tabla_lineas}"
    )


def _tabla_por_zona(por_tipo: dict, tipos) -> str:
    """Cuánto aporta cada zona a cada riesgo. Con una sola zona no aporta nada."""
    primera = por_tipo[tipos[0]]
    if len(primera["zonas"]) < 2:
        return ""
    cabecera = " & ".join(f"$R_{t}$" for t in tipos)
    filas = ""
    for nombre in primera["zonas"]:
        valores = " & ".join(
            f"${numero(por_tipo[t]['zonas'][nombre]['total'])}$" for t in tipos)
        filas += f"{escapar(nombre)} & {valores} \\\\\n"
    columnas = "l" + "r" * len(tipos)
    return (
        "\\subsection*{Aporte de cada zona}\n"
        f"\\begin{{tabular}}{{@{{}}{columnas}@{{}}}}\n\\toprule\n"
        f"Zona & {cabecera} \\\\\n\\midrule\n"
        f"{filas}"
        "\\bottomrule\n\\end{tabular}\n\n"
    )


def memoria_tex_caso(casos: dict, por_tipo: dict, proyecto=None, soluciones=None,
                     figuras=None, tipo_desarrollado=1) -> str:
    """El documento completo a partir de un caso del modelo.

    casos: {tipo: {"estructura", "lineas", "zonas", "N_G"}}, lo que devuelve
        EditorCaso.casos_por_tipo().
    por_tipo: {tipo: resultado}, lo que devuelve EditorCaso.evaluar().

    El contenido es el mismo que el de memoria_tex, pero las tablas de
    entrada y de áreas ya no suponen una zona y una línea.
    """
    tipos = sorted(por_tipo)
    caso = casos[tipos[0]]
    planas = _llaves_planas(por_tipo)

    desarrollada = por_tipo.get(tipo_desarrollado, por_tipo[tipos[0]])
    nombre_zona = next(iter(desarrollada["zonas"]))
    zona = desarrollada["zonas"][nombre_zona]

    cuerpo = (
        _tabla_datos_proyecto(proyecto)
        + _tabla_estructura(caso["estructura"], caso["N_G"])
        + _tabla_zonas(caso["zonas"])
        + _tabla_lineas(caso["lineas"])
        + _tabla_areas_caso(zona["_detalle"])
        + _tabla_componentes(planas, tipos)
        + _tabla_veredicto(planas, tipos)
        + _tabla_por_zona(por_tipo, tipos)
        + _desarrollo(zona["_detalle"], zona, tipo_desarrollado)
        + _de_donde_viene(zona, tipo_desarrollado)
        + _tabla_soluciones(soluciones)
        + _figuras(figuras)
    )
    if len(caso["zonas"]) > 1:
        cuerpo = cuerpo.replace(
            "\\section{Desarrollo del cálculo}\n",
            "\\section{Desarrollo del cálculo}\n"
            f"Se desarrolla la zona \\textit{{{escapar(nombre_zona)}}}; "
            f"el riesgo total suma las {len(caso['zonas'])} zonas.\n\n")

    return (
        PREAMBULO
        + "\\title{Memoria de cálculo de riesgo por rayo\\\\"
          "\\large NTC 4552-2:2023}\n\\date{\\today}\n"
          "\\begin{document}\n\\maketitle\n\n"
        + cuerpo
        + "\\end{document}\n"
    )


def escribir_memoria_caso(ruta, casos, por_tipo, **kwargs) -> str:
    """Escribe el .tex de un caso del modelo y devuelve su ruta."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(memoria_tex_caso(casos, por_tipo, **kwargs))
    return str(ruta)


def _figuras_de(carpeta, puntos, soluciones, tipo) -> list:
    """Las figuras PNG del informe. Sin matplotlib devuelve [] y sigue.

    El programa se instala en PCs que no tienen por qué tener matplotlib.
    Perder las figuras es aceptable; perder la memoria entera, no.
    """
    try:
        from calculate_risk.norma import graficos
    except ImportError:
        return []

    ruta = os.path.join(carpeta, "memoria_sensibilidad.png")
    graficos.curva_sensibilidad(
        puntos, ruta, etiqueta_x="$N_G$  [descargas/km$^2\\cdot$año]",
        titulo="Riesgo frente a la densidad de descargas", tipo=tipo,
        escala_x="log")
    figuras = [(ruta, "Riesgo frente a la densidad de descargas del sitio")]

    if soluciones:
        ruta = os.path.join(carpeta, "memoria_costo_riesgo.png")
        graficos.dispersion_costo_riesgo(soluciones, ruta, tipo=tipo)
        figuras.append((ruta, "Costo de las medidas frente al riesgo residual"))
    return figuras


def informe_completo_caso(carpeta, casos, por_tipo, proyecto=None,
                          nombre="Memoria de calculo", tipo=None, precios=None):
    """El informe entero a partir de un caso del modelo: .tex, PDF, figuras y CSV.

    Es el equivalente de informe_completo() para la pantalla nueva. Devuelve
    (ruta_tex, ruta_pdf); ruta_pdf es None si no hay LaTeX instalado, y el
    .tex queda escrito igual para compilarlo en otro lado.

    tipo: el riesgo que se desarrolla paso a paso y sobre el que se buscan
        medidas. Por omisión, el más bajo de los evaluados.
    precios: {nombre de la medida: costo}. Sin precios las medidas salen
        igual, pero ordenadas por cantidad en vez de por plata.

    Las medidas solo se buscan si ese riesgo NO cumple: recorrer el catálogo
    entero tarda, y en un caso que ya cumple la tabla no diría nada.
    """
    from calculate_risk.norma import barridos, medidas

    carpeta = str(carpeta)
    tipo = sorted(por_tipo)[0] if tipo is None else tipo
    caso = casos[tipo]
    args = (caso["estructura"], caso["lineas"], caso["zonas"], caso["N_G"])

    soluciones = None
    if not por_tipo[tipo]["cumple"]:
        soluciones = medidas.explorar(
            *args, tipo=tipo, catalogo_medidas=medidas.catalogo(costos=precios))
        barridos.exportar_soluciones(
            soluciones, os.path.join(carpeta, "memoria_medidas.csv"))

    puntos = barridos.barrer(*args, valores=N_G_SENSIBILIDAD, destino="N_G",
                             tipo=tipo)
    barridos.exportar_barrido(
        puntos, os.path.join(carpeta, "memoria_sensibilidad.csv"), "N_G")

    ruta_tex = escribir_memoria_caso(
        os.path.join(carpeta, f"{nombre}.tex"), casos, por_tipo,
        proyecto=proyecto, soluciones=soluciones,
        figuras=_figuras_de(carpeta, puntos, soluciones, tipo),
        tipo_desarrollado=tipo)

    try:
        return ruta_tex, compilar(ruta_tex)
    except RuntimeError:
        return ruta_tex, None