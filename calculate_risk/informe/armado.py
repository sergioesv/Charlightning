"""
Paso 61a: el informe armado desde el caso.

    caso + resultados  ->  armar()  ->  Documento (bloques)  ->  pdf.dibujar()

Este módulo NO calcula nada: recibe los resultados que ya dio el motor (los mismos que
muestra el panel) y los escribe. Ni un factor, ni un R, ni una probabilidad se recalculan
aquí; solo se formatean. Si el número del informe difiere del de la pantalla, el error
está en el formato, y las pruebas lo vigilan.

Lo que sí decide es QUÉ se dice: de dónde sale N_G (la ficha del dato o la fuente
declarada), qué se evaluó y qué no, y una conclusión que se deduce de los números y no
de una plantilla.

Es el heredero de norma/memoria.py: el desarrollo del cálculo y la tabla «de dónde viene
R» vienen de allí.
"""
from calculate_risk.informe import documento as d
from calculate_risk.informe.documento import escapar
from calculate_risk.norma import etiquetas, riesgos

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
    1: "R<sub>1</sub> — Pérdida de vidas humanas",
    2: "R<sub>2</sub> — Pérdida de servicio público esencial",
    3: "R<sub>3</sub> — Pérdida de patrimonio cultural",
    4: "R<sub>4</sub> — Pérdida económica",
}

# Cada componente: su ecuación en la norma y de qué factores sale. R = N x P x L
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

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")

MEDIDAS_QUE_SE_MUESTRAN = 10


# ---------------------------------------------------------------------------
# Formato: coma decimal y notación científica. Solo presentan, no calculan.
# ---------------------------------------------------------------------------

def _partes_cientificas(valor, cifras):
    mantisa, exponente = f"{valor:.{cifras}e}".split("e")
    return mantisa.rstrip("0").rstrip("."), int(exponente)


def cientifico(valor, cifras=3) -> str:
    """2,506 × 10<super>-5</super>, con coma decimal (para texto y tablas)."""
    if valor == 0:
        return "0"
    mantisa, exponente = _partes_cientificas(valor, cifras)
    mantisa = mantisa.replace(".", ",")
    if exponente == 0:
        return mantisa
    return f"{mantisa} × 10<super>{exponente}</super>"


def tex_cientifico(valor, cifras=3) -> str:
    """Lo mismo, en la sintaxis de las fórmulas: 2{,}506 \\times 10^{-5}."""
    if valor == 0:
        return "0"
    mantisa, exponente = _partes_cientificas(valor, cifras)
    mantisa = mantisa.replace(".", "{,}")
    if exponente == 0:
        return mantisa
    return f"{mantisa} \\times 10^{{{exponente}}}"


def _plano_base(valor, cifras):
    texto = f"{valor:,.{cifras}f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto or "0"


def plano(valor, cifras=4) -> str:
    """Una magnitud corriente (metros, N_G, un coeficiente): 15; 0,5; 2 577,88."""
    return _plano_base(valor, cifras).replace(",", "&nbsp;").replace(".", ",")


def tex_plano(valor, cifras=4) -> str:
    return _plano_base(valor, cifras).replace(",", "\\,").replace(".", "{,}")


def corriente(valor) -> str:
    """Un factor de tabla: 0,5 o 1 tal cual, y notación científica solo si es muy chico."""
    if valor == 0 or 0.001 <= abs(valor) < 1000:
        return plano(valor)
    return cientifico(valor)


def medida(nombre) -> str:
    """El nombre de una medida como lo ve el usuario en la pantalla (etiquetas.py)."""
    try:
        return escapar(etiquetas.texto_de_medida(nombre))
    except (KeyError, ValueError):
        return escapar(nombre)


def coma(valor, decimales=1) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def fecha_larga(fecha) -> str:
    """date -> «28 de septiembre de 2026»."""
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def grados(valor, positivo, negativo) -> str:
    return f"{coma(abs(valor), 3)}° {positivo if valor >= 0 else negativo}"


def _sub(componente) -> str:
    """'R_V' -> R<sub>V</sub>."""
    base, indice = componente.split("_")
    return f"{base}<sub>{indice}</sub>"


def _lista_de_riesgos(tipos) -> str:
    nombres = [f"R<sub>{t}</sub>" for t in tipos]
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


# ---------------------------------------------------------------------------
# Portada
# ---------------------------------------------------------------------------

def _tabla_del_proyecto(proyecto, coordenadas=None):
    filas = [[f"<b>{escapar(k)}</b>", escapar(v)]
             for k, v in (proyecto or {}).items() if str(v).strip()]
    if coordenadas:
        filas.append(["<b>Coordenadas</b>", coordenadas])
    if not filas:
        return []
    return [d.Tabla(filas, anchos=(38, 128), cabecera=False)]


def _coordenadas_del(emplazamiento) -> str:
    if emplazamiento is None or emplazamiento.lat is None or emplazamiento.lon is None:
        return ""
    return (f"{grados(emplazamiento.lat, 'N', 'S')}   "
            f"{grados(emplazamiento.lon, 'E', 'O')}")


# ---------------------------------------------------------------------------
# 1 y 2. Alcance, términos y notación
# ---------------------------------------------------------------------------

def _alcance(tipos):
    riesgos_txt = _lista_de_riesgos(tipos)
    return [
        d.Titulo("1. Alcance y base normativa"),
        d.Parrafo(
            "Este documento contiene la evaluación del riesgo debido a descargas "
            "eléctricas atmosféricas para la estructura identificada en la portada, "
            "realizada conforme al procedimiento de la <b>NTC 4552-2:2023</b> "
            "(equivalente a la IEC 62305-2). Se evalúan los riesgos "
            f"{riesgos_txt}, cada uno comparado con su riesgo tolerable R<sub>T</sub> "
            "de la Tabla 4 de la norma, y, cuando alguno lo supera, se buscan "
            "las medidas de protección que lo llevan por debajo de ese valor."),
        d.Parrafo(
            "<b>No forman parte de este alcance</b> el diseño detallado del sistema de "
            "protección (ubicación de puntas captadoras, bajantes y puestas a tierra, "
            "que corresponden a la NTC 4552-3), la coordinación de aislamiento, ni la "
            "verificación del estado de las instalaciones existentes."),
    ]


def _terminos():
    return [
        d.Titulo("2. Términos, responsabilidad y notación"),
        d.Parrafo(
            "Los resultados dependen íntegramente de los datos de entrada declarados en "
            "los numerales 3 y 4. El programa no verifica que esos datos correspondan a "
            "la instalación real: esa verificación es responsabilidad del profesional "
            "que firma la memoria. Los factores empleados son los que el diseñador "
            "declaró a partir de las tablas de los Anexos A, B y C de la norma."),
        d.Parrafo(
            "El riesgo R es una magnitud <i>anual y probabilística</i>: un valor por "
            "debajo del tolerable no significa que la estructura no pueda ser "
            "impactada, sino que la pérdida esperada es aceptable según el criterio "
            "de la norma."),
        d.Titulo("Notación empleada", 2),
        d.Tabla([
            ["Símbolo", "Significado", "Unidad"],
            ["N<sub>G</sub>", "Densidad de descargas a tierra", "1/km<super>2</super>·año"],
            ["A<sub>D</sub>", "Área de captación equivalente de la estructura",
             "m<super>2</super>"],
            ["N<sub>D</sub>", "Número de eventos peligrosos a la estructura", "1/año"],
            ["N<sub>L</sub>, N<sub>I</sub>", "Eventos peligrosos en una línea y cerca de ella",
             "1/año"],
            ["P<sub>X</sub>", "Probabilidad de daño del componente X", "—"],
            ["L<sub>X</sub>", "Pérdida asociada al componente X", "—"],
            ["R<sub>X</sub>", "Componente de riesgo X", "1/año"],
            ["R<sub>T</sub>", "Riesgo tolerable (Tabla 4)", "1/año"],
        ], anchos=(24, 116, 26)),
    ]


# ---------------------------------------------------------------------------
# 3. Emplazamiento y densidad de descargas
# ---------------------------------------------------------------------------

def _emplazamiento(emplazamiento, N_G, ficha):
    """De dónde sale N_G. Nunca se imprime solo: siempre con su procedencia."""
    bloques = [d.Titulo("3. Emplazamiento y densidad de descargas")]
    n_g = f"{plano(N_G)} rayos/km<super>2</super>·año"

    if emplazamiento is None:
        bloques.append(d.Parrafo(
            f"Este caso <b>no registra de dónde sale</b> la densidad de descargas: se usó "
            f"N<sub>G</sub> = {n_g}. Antes de firmar la memoria hay que documentar su fuente."))
        return bloques

    if emplazamiento.modo == "declarado":
        fuente = escapar(emplazamiento.fuente) if emplazamiento.fuente else \
            "<b>(no se indicó fuente)</b>"
        bloques += [
            d.Parrafo("La densidad de descargas a tierra N<sub>G</sub> fue <b>declarada por el "
                      "diseñador</b>; no se calculó con el programa."),
            d.Tabla([["Dato", "Valor"],
                     ["N<sub>G</sub> adoptada", n_g],
                     ["Fuente declarada", fuente]], anchos=(40, 126)),
        ]
        return bloques

    lugar = _coordenadas_del(emplazamiento)
    if ficha is None:
        bloques.append(d.Parrafo(
            f"N<sub>G</sub> se calculó para las coordenadas del proyecto ({lugar}) con la "
            "climatología satelital LIS/OTD de la NASA. En este momento no se pudo leer la "
            f"ficha del dato; el valor usado fue N<sub>G</sub> = {n_g}."))
        return bloques

    bloques += [
        d.Parrafo(
            "La densidad de descargas a tierra N<sub>G</sub> se obtuvo de la climatología "
            "satelital LIS/OTD de la NASA, tomando la celda de la grilla más cercana a las "
            "coordenadas del proyecto y aplicando la fracción de destellos que llegan a "
            "tierra. La ficha siguiente permite reproducir el valor."),
        d.Tabla([
            ["Dato", "Valor"],
            ["Producto", escapar(f"{ficha.producto}, {ficha.version}".rstrip(", "))],
            ["Plataforma", escapar(ficha.plataforma)],
            ["Procesamiento", escapar(ficha.procesamiento)],
            ["Sitio del proyecto",
             f"{grados(ficha.lat, 'N', 'S')}   {grados(ficha.lon, 'E', 'O')}"],
            ["Celda de la grilla",
             f"{grados(ficha.celda_lat, 'N', 'S')}   {grados(ficha.celda_lon, 'E', 'O')}"],
            ["Distancia sitio–celda", f"{coma(ficha.distancia_km, 1)} km"],
            ["Destellos totales (intranube y a tierra)",
             f"{coma(ficha.destellos_totales, 2)} destellos/km<super>2</super>·año"],
            ["Tiempo de observación de la celda", f"{coma(ficha.horas_observadas, 0)} h"],
            ["Fracción nube-tierra adoptada",
             f"{coma(ficha.fraccion_nube_tierra, 3)} (relación intranube:tierra "
             f"Z = {coma(ficha.relacion_ic_cg, 1)})"],
            ["<b>N<sub>G</sub> adoptada</b>", f"<b>{n_g}</b>"],
        ], anchos=(62, 104)),
        d.Parrafo(
            "La fracción nube-tierra es un valor <b>adoptado por el diseñador</b>: el sensor "
            "mide destellos totales y la norma pide descargas a tierra, y esa fracción es "
            "la que los relaciona. No es un dato de la norma ni del producto de la NASA, y "
            "N<sub>G</sub> cambia en la misma proporción si se cambia. El tiempo de "
            "observación indica cuánto miró el sensor esa celda: a menos horas, "
            "más incierto el dato.", "nota"),
    ]
    return bloques


# ---------------------------------------------------------------------------
# 4. Datos de la estructura, las zonas y las líneas
# ---------------------------------------------------------------------------

def _si_no(valor) -> str:
    return "Sí" if valor else "No"


def _datos(caso, figura_area):
    e = caso["estructura"]
    zonas = caso["zonas"]
    lineas = caso["lineas"]

    bloques = [
        d.Titulo("4. Datos de la estructura, las zonas y las líneas"),
        d.Titulo("Estructura", 2),
        d.Tabla([
            ["Parámetro", "Valor"],
            ["Longitud L [m]", plano(e.L)],
            ["Ancho W [m]", plano(e.W)],
            ["Altura H [m]", plano(e.H)],
            ["Altura del saliente H<sub>P</sub> [m]", plano(e.H_p)],
            ["Factor de localización C<sub>D</sub> (Tabla A.1)", plano(e.C_D)],
            ["Personas en la estructura n<sub>t</sub>", plano(e.n_t)],
            ["Riesgo de explosión o para la vida por falla de sistemas internos",
             _si_no(e.riesgo_explosion_o_vital)],
        ], anchos=(120, 46), derecha=(1,)),
    ]

    filas = [["Zona", "n<sub>z</sub>", "t<sub>z</sub> [h]", "P<sub>B</sub>",
              "r<sub>f</sub>", "r<sub>p</sub>", "L<sub>F</sub>"]]
    for z in zonas:
        filas.append([escapar(z.nombre), plano(z.n_z), plano(z.t_z), corriente(z.P_B),
                      corriente(z.r_f), corriente(z.r_p), corriente(z.L_F)])
    bloques += [d.Titulo(f"Zonas ({len(zonas)})", 2),
                d.Tabla(filas, anchos=(46, 16, 20, 20, 20, 20, 24),
                        derecha=(1, 2, 3, 4, 5, 6))]

    if lineas:
        filas = [["Línea", "L<sub>L</sub> [m]", "C<sub>I</sub>", "C<sub>T</sub>",
                  "C<sub>E</sub>", "U<sub>W</sub> [kV]", "P<sub>LD</sub>",
                  "P<sub>LI</sub>", "Vecina"]]
        for ln in lineas:
            filas.append([escapar(ln.nombre), plano(ln.L_L), corriente(ln.C_I),
                          corriente(ln.C_T), corriente(ln.C_E), plano(ln.U_W),
                          corriente(ln.P_LD), corriente(ln.P_LI),
                          "sí" if ln.adyacente is not None else "no"])
        bloques += [d.Titulo(f"Líneas ({len(lineas)})", 2),
                    d.Tabla(filas, anchos=(34, 20, 14, 14, 14, 18, 16, 16, 14),
                            derecha=(1, 2, 3, 4, 5, 6, 7))]
    else:
        bloques += [d.Titulo("Líneas", 2), d.Parrafo(
            "La estructura no tiene líneas de servicio conectadas, así que los componentes "
            "R<sub>U</sub>, R<sub>V</sub>, R<sub>W</sub> y R<sub>Z</sub> no intervienen.")]

    if figura_area:
        bloques.append(d.Figura(
            figura_area, 122,
            "Figura 2. Planta de la estructura y su área de captación equivalente "
            "A<sub>D</sub> (ecuaciones A.2 y A.3 de la norma)."))
    return bloques


# ---------------------------------------------------------------------------
# 5. Frecuencia de impactos y componentes del riesgo
# ---------------------------------------------------------------------------

def _valor_factor(nombre, detalle, linea):
    """Un factor del desarrollo: primero en la zona, luego en la línea."""
    if nombre == "N_L + N_{DJ}":
        return linea["N_L"] + linea["N_DJ"]
    if nombre in detalle:
        return detalle[nombre]
    return linea[nombre]


def _frecuencias(detalle):
    filas = [["Magnitud", "Valor"],
             ["A<sub>D</sub> — área de captación de la estructura (ec. A.2) [m<super>2</super>]",
              plano(detalle["A_D"], 2)],
             ["N<sub>D</sub> — descargas en la estructura (ec. A.4) [1/año]",
              cientifico(detalle["N_D"])],
             ["N<sub>M</sub> — descargas cerca de la estructura (ec. A.6) [1/año]",
              cientifico(detalle["N_M"])]]
    bloques = [d.Titulo("Áreas de captación y frecuencia de eventos", 2),
               d.Tabla(filas, anchos=(130, 36), derecha=(1,))]
    if detalle["lineas"]:
        por_linea = [["Línea", "N<sub>L</sub> (ec. A.8)", "N<sub>I</sub> (ec. A.10)",
                      "N<sub>DJ</sub> (ec. A.5)"]]
        for nombre, ln in detalle["lineas"].items():
            por_linea.append([escapar(nombre), cientifico(ln["N_L"]),
                              cientifico(ln["N_I"]), cientifico(ln["N_DJ"])])
        bloques.append(d.Tabla(por_linea, anchos=(46, 40, 40, 40), derecha=(1, 2, 3)))
    return bloques


def _desarrollo(zona, tipo, nombre_zona, cuantas_zonas):
    """El cálculo paso a paso: cada componente con sus números.

    Es lo que distingue una memoria de una hoja de resultados: se ve de dónde sale cada
    valor. `zona` es la primera zona del riesgo desarrollado.
    """
    detalle = zona["_detalle"]
    lineas = list(detalle["lineas"].items())
    nombre_linea, linea = lineas[0] if lineas else (None, {})

    bloques = [
        d.Titulo(f"Desarrollo del cálculo de R<sub>{tipo}</sub>", 2),
        d.Parrafo("Cada componente es el producto de tres factores: la frecuencia de eventos "
                  "N, la probabilidad de daño P y la pérdida L."),
    ]
    if cuantas_zonas > 1:
        bloques.append(d.Parrafo(
            f"Se desarrolla la zona <i>{escapar(nombre_zona)}</i>; el riesgo total suma las "
            f"{cuantas_zonas} zonas.", "nota"))
    if nombre_linea and len(lineas) > 1:
        bloques.append(d.Parrafo(
            f"Los componentes de línea se desarrollan para <i>{escapar(nombre_linea)}</i>; "
            f"el valor final suma las {len(lineas)} líneas.", "nota"))

    ausentes = []
    for componente, (ecuacion, n, p, l) in DESARROLLO.items():
        letra = componente[2]
        if componente not in detalle["aplica"]:
            ausentes.append(_sub(componente))
            continue
        try:
            vn = _valor_factor(n, detalle, linea)
            vp = _valor_factor(p, detalle, linea)
            vl = _valor_factor(l, detalle, linea)
        except KeyError:
            continue
        bloques += [
            d.Parrafo(f"{_sub(componente)} — ecuación ({ecuacion}):"),
            d.Formula(f"R_{{{letra}}} = ({n}) \\times {p} \\times {l} = "
                      f"{tex_cientifico(vn)} \\times {tex_cientifico(vp)} \\times "
                      f"{tex_cientifico(vl)} = \\mathbf{{{tex_cientifico(zona[componente])}}}"),
        ]
    if ausentes:
        bloques.append(d.Parrafo(
            f"{', '.join(ausentes)}: no intervienen en R<sub>{tipo}</sub> (numeral 4.3).",
            "nota"))
    return bloques


def _tabla_de_componentes(por_tipo, tipos):
    filas = [["", "Componente"] + [f"R<sub>{t}</sub>" for t in tipos]]
    for c in riesgos.COMPONENTES:
        filas.append([_sub(c), escapar(NOMBRES_COMPONENTES[c])]
                     + [cientifico(por_tipo[t][c]) for t in tipos])
    filas.append(["<b>Total</b>", "<b>Suma de los componentes [1/año]</b>"]
                 + [f"<b>{cientifico(por_tipo[t]['total'])}</b>" for t in tipos])
    ancho_valor = 90 / len(tipos)
    return [d.Titulo("Componentes de riesgo [1/año]", 2),
            d.Tabla(filas, anchos=(12, 64) + (ancho_valor,) * len(tipos),
                    derecha=tuple(range(2, 2 + len(tipos))))]


def aportes_de(resultado):
    """[(componente, valor, porcentaje)] de mayor a menor; los ceros no salen."""
    total = resultado["total"]
    if not total:
        return []
    ordenados = sorted(((c, resultado[c]) for c in riesgos.COMPONENTES if resultado[c]),
                       key=lambda cv: -cv[1])
    return [(c, v, v / total * 100) for c, v in ordenados]


def _de_donde_viene(resultado, tipo, figura):
    aportes = aportes_de(resultado)
    if not aportes:
        return []
    filas = [["Componente", "Valor [1/año]", "Participación"]]
    for c, v, pct in aportes:
        filas.append([_sub(c), cientifico(v), f"{coma(pct, 1)} %"])
    bloques = [d.Titulo(f"De dónde viene R<sub>{tipo}</sub>", 2),
               d.Tabla(filas, anchos=(40, 70, 56), derecha=(1, 2))]
    if figura:
        bloques.append(d.Figura(
            figura, 150,
            f"Figura 3. Participación de cada componente en R<sub>{tipo}</sub>. El mayor "
            "es donde una medida de protección rinde más."))
    return bloques


def _calculo(por_tipo, tipos, tipo, figura_aporte):
    desarrollada = por_tipo[tipo]
    nombre_zona = next(iter(desarrollada["zonas"]))
    zona = desarrollada["zonas"][nombre_zona]
    return (
        [d.Titulo("5. Frecuencia de impactos y componentes del riesgo"),
         d.Parrafo("El número anual de descargas peligrosas a la estructura sale del "
                   "área de captación y del factor de localización, y cada componente de "
                   "riesgo del producto de la frecuencia, la probabilidad y la pérdida:"),
         d.Formula("N_D = N_G \\cdot A_D \\cdot C_D \\cdot 10^{-6}"),
         d.Formula("R_X = N_X \\cdot P_X \\cdot L_X")]
        + _frecuencias(zona["_detalle"])
        + _desarrollo(zona, tipo, nombre_zona, len(desarrollada["zonas"]))
        + _tabla_de_componentes(por_tipo, tipos)
        + _de_donde_viene(desarrollada, tipo, figura_aporte)
    )


# ---------------------------------------------------------------------------
# 6. Veredicto y medidas
# ---------------------------------------------------------------------------

def _veredicto(por_tipo, tipos, tipo, soluciones, figura_veredicto):
    filas = [["Riesgo", "Calculado", "Tolerable", "Veredicto"]]
    incumplen = []
    for t in tipos:
        r = por_tipo[t]
        if not r["cumple"]:
            incumplen.append(t)
        filas.append([NOMBRES_RIESGOS[t], cientifico(r["total"]), cientifico(r["R_T"]),
                      "Cumple" if r["cumple"] else "<b>No cumple</b>"])

    if incumplen:
        primero = por_tipo[incumplen[0]]
        detalle = (f"R<sub>{incumplen[0]}</sub> = {cientifico(primero['total'])} &gt; "
                   f"R<sub>T</sub> = {cientifico(primero['R_T'])}")
        resumen = f"{detalle} · NO CUMPLE"
        if len(incumplen) > 1:
            resumen += f" ({_lista_de_riesgos(incumplen)})"
        resumen += " — se requieren medidas de protección (numeral 5, Figura 1)."
    else:
        resumen = (f"Los riesgos {_lista_de_riesgos(tipos)} son iguales o menores que su "
                   "riesgo tolerable · CUMPLE.")

    bloques = [d.Titulo("6. Veredicto y medidas de protección"),
               d.Tabla(filas, anchos=(90, 28, 28, 20), derecha=(1, 2)),
               d.Espacio(3),
               d.Recuadro(resumen, cumple=not incumplen)]

    if soluciones is None:
        return bloques
    bloques.append(d.Titulo(f"Medidas de protección para R<sub>{tipo}</sub>", 2))
    if not soluciones:
        bloques.append(d.Parrafo(
            "<b>Ninguna combinación de las medidas contempladas lleva el riesgo por debajo "
            "del valor tolerable.</b> Hay que revisar el caso: reducir la longitud o la "
            "exposición de las líneas, dividir la estructura en zonas, o reconsiderar los "
            "valores de pérdida adoptados."))
        return bloques

    con_economia = soluciones[0].S_M is not None
    con_costo = any(sol.costo for sol in soluciones)
    cabecera = ["Medidas", f"R<sub>{tipo}</sub> resultante"]
    if con_costo:
        cabecera.append("Costo")
    if con_economia:
        cabecera.append("S<sub>M</sub>")
    filas = [cabecera]
    for sol in soluciones[:MEDIDAS_QUE_SE_MUESTRAN]:
        fila = [" + ".join(medida(n) for n in sol.nombres) or "(sin medidas)",
                cientifico(sol.riesgo)]
        if con_costo:
            fila.append(f"{sol.costo:,.0f}".replace(",", "&nbsp;"))
        if con_economia:
            fila.append(f"{sol.S_M:,.0f}".replace(",", "&nbsp;"))
        filas.append(fila)
    ancho = {2: (128, 38), 3: (108, 34, 24), 4: (84, 34, 24, 24)}[len(cabecera)]
    orden = ("según el análisis del Anexo D" if con_economia
             else "por costo" if con_costo else "de menos a más medidas (no se cargaron costos)")
    bloques += [
        d.Parrafo("Combinaciones que llevan el riesgo por debajo del valor tolerable, "
                  f"ordenadas {orden}."),
        d.Tabla(filas, anchos=ancho, derecha=tuple(range(1, len(cabecera)))),
    ]
    if figura_veredicto:
        bloques.append(d.Figura(
            figura_veredicto, 140,
            f"Figura 4. R<sub>{tipo}</sub> sin medidas y con la primera combinación de la "
            "tabla, frente al riesgo tolerable."))
    return bloques


# ---------------------------------------------------------------------------
# 7. Conclusión y firma
# ---------------------------------------------------------------------------

def _conclusion(por_tipo, tipos, tipo, soluciones, proyecto):
    incumplen = [t for t in tipos if not por_tipo[t]["cumple"]]
    if not incumplen:
        texto = (f"La estructura evaluada <b>cumple</b> el criterio de riesgo tolerable de la "
                 f"NTC 4552-2:2023 para los riesgos {_lista_de_riesgos(tipos)}.")
    else:
        texto = (f"La estructura evaluada <b>no cumple</b> el criterio de riesgo tolerable de "
                 f"la NTC 4552-2:2023 para {_lista_de_riesgos(incumplen)}.")
        aportes = aportes_de(por_tipo[tipo])
        if aportes:
            c, _, pct = aportes[0]
            texto += (f" En R<sub>{tipo}</sub>, el componente dominante es {_sub(c)} "
                      f"({escapar(NOMBRES_COMPONENTES[c].lower())}), con {coma(pct, 1)} % "
                      "del total.")
        if soluciones:
            mejor = soluciones[0]
            texto += (f" La primera combinación de medidas de la tabla del numeral 6 "
                      f"({' + '.join(medida(n) for n in mejor.nombres) or 'sin medidas'}) deja "
                      f"R<sub>{tipo}</sub> en {cientifico(mejor.riesgo)}, frente a un tolerable "
                      f"de {cientifico(mejor.R_T)}.")
        elif soluciones is not None:
            texto += (" Ninguna combinación de las medidas contempladas lleva el riesgo por "
                      "debajo del tolerable; hay que revisar el caso.")

    quien = escapar((proyecto or {}).get("Diseñador", "") or "Diseñador")
    return [
        d.Titulo("7. Conclusión y firma"),
        d.Parrafo(texto),
        d.Espacio(14),
        d.Tabla([["_" * 34, "", "_" * 34],
                 [quien, "", "Revisó"]], anchos=(70, 26, 70), cabecera=False),
    ]


# ---------------------------------------------------------------------------
# 8. Referencias
# ---------------------------------------------------------------------------

def _referencias(usa_nasa, usa_mapa):
    refs = [
        "ICONTEC. <i>NTC 4552-2:2023 — Protección contra descargas eléctricas atmosféricas "
        "(rayos). Parte 2: Evaluación del riesgo</i>.",
    ]
    if usa_nasa:
        refs += [
            "NASA/MSFC/GHRC. <i>LIS 0.1 Degree Very High Resolution Gridded Lightning Full "
            "Climatology (VHRFC) V1</i>. Global Hydrology Resource Center DAAC. "
            "doi:10.5067/LIS/LIS/DATA301.",
            "Albrecht, R. I.; Goodman, S. J.; Buechler, D. E.; Blakeslee, R. J.; "
            "Christian, H. J. (2016). «Where Are the Lightning Hotspots on Earth?». "
            "<i>Bulletin of the American Meteorological Society</i>, 97(11), 2051–2068. "
            "doi:10.1175/BAMS-D-14-00193.1.",
        ]
    if usa_mapa:
        refs.append("Natural Earth. <i>Admin 0 – Countries, 1:50 m</i>. Dominio público. "
                    "naturalearthdata.com.")
    return [d.Titulo("8. Referencias")] + [
        d.Parrafo(f"[{i}] {texto}") for i, texto in enumerate(refs, 1)]


# ---------------------------------------------------------------------------
# El informe
# ---------------------------------------------------------------------------

def armar(casos: dict, por_tipo: dict, proyecto: dict = None, ficha=None,
          soluciones=None, figuras: dict = None, tipo: int = None,
          fecha=None) -> d.Documento:
    """El informe completo como Documento.

    casos: {tipo: {"estructura", "lineas", "zonas", "N_G", "emplazamiento"}}, lo que
        devuelve EditorCaso.casos_por_tipo().
    por_tipo: {tipo: resultado}, lo que devuelve EditorCaso.evaluar(): los MISMOS números
        que muestra el panel.
    ficha: la FichaNG del sitio (solo si N_G salió de coordenadas); sin ella el informe
        lo dice en vez de inventarla.
    soluciones: las medidas de medidas.explorar(); None si no se buscaron (todo cumple).
        Una lista vacía SÍ se informa: no hay ninguna combinación que baste.
    figuras: {"mapa", "area", "aporte", "veredicto"} -> ruta PNG. Las que falten no salen.
    tipo: el riesgo que se desarrolla; por omisión, el más bajo de los evaluados.
    """
    tipos = sorted(por_tipo)
    tipo = tipos[0] if tipo is None else tipo
    figuras = figuras or {}
    caso = casos[tipo]
    emplazamiento = caso.get("emplazamiento")
    proyecto = proyecto or {}

    portada = []
    if figuras.get("mapa"):
        portada.append(d.Figura(
            figuras["mapa"], 150,
            "Figura 1. Densidad de descargas a tierra alrededor del sitio (climatología "
            "satelital LIS/OTD de la NASA) y su ubicación en el país."))
    portada += [d.Espacio(2)]
    portada += _tabla_del_proyecto(proyecto, _coordenadas_del(emplazamiento))
    if fecha is not None:
        portada += [d.Espacio(6), d.Parrafo(fecha_larga(fecha), "nota")]

    nombre = str(proyecto.get("Proyecto", "")).strip()
    bloques = [d.Contenido()]
    bloques += _alcance(tipos) + _terminos() + [d.Salto()]
    bloques += _emplazamiento(emplazamiento, caso["N_G"], ficha)
    bloques += _datos(caso, figuras.get("area"))
    bloques += _calculo(por_tipo, tipos, tipo, figuras.get("aporte"))
    bloques += _veredicto(por_tipo, tipos, tipo, soluciones, figuras.get("veredicto"))
    bloques += _conclusion(por_tipo, tipos, tipo, soluciones, proyecto)
    bloques += _referencias(
        usa_nasa=emplazamiento is not None and emplazamiento.modo == "coordenadas",
        usa_mapa=bool(figuras.get("mapa")))

    return d.Documento(
        titulo="Evaluación del riesgo por descargas<br/>eléctricas atmosféricas",
        subtitulo="NTC 4552-2:2023 — Protección contra descargas eléctricas atmosféricas. "
                  "Parte 2: Evaluación del riesgo",
        sobretitulo="Memoria de cálculo",
        autor=str(proyecto.get("Diseñador", "")),
        encabezado_izq="Memoria de cálculo del riesgo por rayos · NTC 4552-2:2023",
        encabezado_der=nombre,
        pie="Generado por Charlightning",
        pie_portada="Charlightning · motor de cálculo verificado contra los ejemplos del "
                    "Anexo E de la norma",
        portada=portada,
        bloques=bloques,
    )