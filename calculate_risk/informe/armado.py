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
from dataclasses import fields, is_dataclass

from calculate_risk.informe import documento as d
from calculate_risk.informe.documento import escapar
from calculate_risk.norma import etiquetas, medidas, probabilidades, riesgos, tablas

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

def _fila_de_tabla(tabla, valor, preferir="") -> str:
    
    """El texto de la fila de la tabla que da ese valor.

    Si varias filas dan el mismo valor, se prefieren las que contienen `preferir` (en la
    Tabla B.4, «aerea» o «subterranea» según la línea) y, si siguen siendo varias, se
    nombran todas con «o»: la norma no las distingue. Si ninguna fila da ese valor (un
    P_TA que es producto de dos previsiones, un P_DPS mejor que NPR I), se escribe «valor
    declarado»."""
    llaves = [llave for llave, v in getattr(tablas, tabla).items() if v == valor]
    elegidas = [llave for llave in llaves if preferir and preferir in llave] or llaves
    if not elegidas:
        return "Valor declarado"
    return escapar(" o ".join(etiquetas.texto(tabla, llave) for llave in elegidas))


def _ninguna(tabla):
    """El valor de la primera fila de la tabla: la que dice «sin medidas»."""
    return next(iter(getattr(tablas, tabla).values()))


def _medidas_adoptadas(zonas, lineas):
    """Las medidas de protección que el caso YA tiene: el informe dice con qué se calculó.

    Solo salen las que difieren de la fila «sin medidas» de su tabla; lo que no aparece
    vale 1 (o el par 1 y 1 de la Tabla B.4)."""
    filas = [["Dónde", "Medida (tabla de la norma)", "Lo adoptado", "Factor"]]

    def fila(donde, tabla, valor, factor, preferir=""):
        numero, titulo = etiquetas.NOMBRES[tabla]
        filas.append([escapar(donde), f"{escapar(titulo)} ({numero})",
                      _fila_de_tabla(tabla, valor, preferir), factor])

    for z in zonas:
        for tabla, campo in (("PB", "P_B"), ("PTA", "P_TA"), ("PTU", "P_TU"), ("RP", "r_p")):
            valor = getattr(z, campo)
            if valor != _ninguna(tabla):
                fila(z.nombre, tabla, valor, f"{_simbolo(campo)} = {corriente(valor)}")
        for campo in ("K_S1", "K_S2"):
            k = getattr(z, campo)
            if k != 1:
                filas.append([escapar(z.nombre), "Blindaje espacial en malla (ec. B.5 y B.6)",
                              f"Malla de {plano(probabilidades.w_m_desde_k_s(k), 2)} m",
                              f"{_simbolo(campo)} = {corriente(k)}"])
        for si in z.sistemas_internos:
            donde = f"{z.nombre}, {si.nombre}"
            if si.P_DPS != _ninguna("PDPS"):
                fila(donde, "PDPS", si.P_DPS, f"P<sub>DPS</sub> = {corriente(si.P_DPS)}")
            if si.K_S3 != _ninguna("KS3"):
                fila(donde, "KS3", si.K_S3, f"K<sub>S3</sub> = {corriente(si.K_S3)}")

    for ln in lineas:
        if ln.P_EB != _ninguna("PEB"):
            fila(ln.nombre, "PEB", ln.P_EB, f"P<sub>EB</sub> = {corriente(ln.P_EB)}")
        par = {"CLD": ln.C_LD, "CLI": ln.C_LI}
        if par != _ninguna("CLD_CLI"):
            tipo_de_linea = "aerea" if ln.C_I == tablas.CI["aerea"] else "subterranea"
            fila(ln.nombre, "CLD_CLI", par,
                 f"C<sub>LD</sub> = {corriente(ln.C_LD)}<br/>C<sub>LI</sub> = {corriente(ln.C_LI)}",
                 preferir=tipo_de_linea)

    bloques = [d.Titulo("Medidas de protección adoptadas", 2)]
    if len(filas) == 1:
        return bloques + [d.Parrafo(
            "El caso no tiene ninguna medida de protección: todos los factores de las "
            "Tablas B.1 a B.7 y C.4 están en su fila «sin medidas».")]
    bloques += [
        d.Tabla(filas, anchos=(30, 52, 60, 24), derecha=(3,)),
        d.Parrafo("Lo que no aparece en la tabla no tiene medida de protección: su factor "
                  "es el de la fila «sin medidas» de la tabla correspondiente.", "nota"),
    ]
    for aviso in riesgos.avisos_sin_spcr(zonas):
        bloques.append(d.Parrafo(f"<b>Advertencia de la norma.</b> {escapar(aviso)}"))
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
                  "C<sub>E</sub>", "Estructura vecina"]]
        for ln in lineas:
            filas.append([escapar(ln.nombre), plano(ln.L_L), corriente(ln.C_I),
                          corriente(ln.C_T), corriente(ln.C_E),
                          "sí" if ln.adyacente is not None else "no"])
        protegidas = [["Línea", "U<sub>W</sub> [kV]", "P<sub>LD</sub>", "P<sub>LI</sub>",
                       "C<sub>LD</sub>", "C<sub>LI</sub>", "P<sub>EB</sub>"]]
        for ln in lineas:
            protegidas.append([escapar(ln.nombre), plano(ln.U_W), corriente(ln.P_LD),
                               corriente(ln.P_LI), corriente(ln.C_LD), corriente(ln.C_LI),
                               corriente(ln.P_EB)])
        bloques += [d.Titulo(f"Líneas ({len(lineas)})", 2),
                    d.Tabla(filas, anchos=(46, 24, 20, 20, 20, 36),
                            derecha=(1, 2, 3, 4)),
                    d.Espacio(3),
                    d.Tabla(protegidas, anchos=(46, 20, 20, 20, 20, 20, 20),
                            derecha=(1, 2, 3, 4, 5, 6))]
    else:
        bloques += [d.Titulo("Líneas", 2), d.Parrafo(
            "La estructura no tiene líneas de servicio conectadas, así que los componentes "
            "R<sub>U</sub>, R<sub>V</sub>, R<sub>W</sub> y R<sub>Z</sub> no intervienen.")]
    
    bloques += _medidas_adoptadas(zonas, lineas)
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

def _por_riesgo(valor, tipo) -> dict:
    """Soluciones o figura del veredicto: un dict {riesgo: x} se usa tal cual; cualquier
    otra cosa (una lista, una ruta) vale para el riesgo desarrollado. None = nada."""
    if isinstance(valor, dict):
        return dict(valor)
    return {} if valor is None else {tipo: valor}


def _reduccion(base, riesgo) -> str:
    """Cuánto del riesgo sin medidas quita la combinación, en %. Solo presenta."""
    if not base:
        return "—"
    pct = (1 - riesgo / base) * 100
    return f"{coma(pct, 3 if pct >= 99.9 else 1)} %"


FORMAS_DE_MEDIDAS = ("completa", "con_factor", "solo_porcentaje")


def _simbolo(campo) -> str:
    """'P_EB' -> P<sub>EB</sub>; 'r_p' -> r<sub>p</sub>."""
    base, _, indice = campo.partition("_")
    return f"{base}<sub>{indice}</sub>" if indice else base


def _numeros_que_cambian(antes, despues, cambios):
    """Recorre dos objetos del modelo y anota cada número que la combinación cambió."""
    if isinstance(antes, (list, tuple)):
        for a, b in zip(antes, despues):
            _numeros_que_cambian(a, b, cambios)
        return
    if not is_dataclass(antes):
        return
    for campo in fields(antes):
        a, b = getattr(antes, campo.name), getattr(despues, campo.name)
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            if a != b:
                cambios.setdefault((campo.name, a, b), None)
        else:
            _numeros_que_cambian(a, b, cambios)


def factores_que_cambian(caso, combinacion) -> str:
    """Los factores del caso que la combinación modifica: 'P_EB: de 1 a 0,05'.

    Se obtienen aplicando la combinación al caso y comparando antes con después, así que
    dicen lo que el motor de verdad recibe; no hay una tabla aparte que pueda desalinearse.
    """
    e, l, z = medidas.aplicar(caso["estructura"], caso["lineas"], caso["zonas"], combinacion)
    cambios = {}
    _numeros_que_cambian(caso["estructura"], e, cambios)
    _numeros_que_cambian(caso["lineas"], l, cambios)
    _numeros_que_cambian(caso["zonas"], z, cambios)
    return "<br/>".join(f"{_simbolo(c)}: de {corriente(a)} a {corriente(b)}"
                        for c, a, b in cambios) or "—"


def _medidas(tipo, soluciones, figura, numero_de_figura, base, caso=None, forma="solo_porcentaje"):
    """Las medidas de UN riesgo: la tabla de combinaciones y, si hay, su figura.

    forma: "completa" (medidas, R resultante, % que reduce), "con_factor" (agrega el factor
    que cambia cada combinación) o "solo_porcentaje" (medidas y % que reduce).
    """
    if forma not in FORMAS_DE_MEDIDAS:
        raise ValueError(f"Forma de la tabla de medidas desconocida: {forma!r}.")
    bloques = [d.Titulo(f"Medidas de protección para R<sub>{tipo}</sub>", 2)]
    if not soluciones:
        bloques.append(d.Parrafo(
            "<b>Ninguna combinación de las medidas contempladas lleva el riesgo por debajo "
            "del valor tolerable.</b> Hay que revisar el caso: reducir la longitud o la "
            "exposición de las líneas, dividir la estructura en zonas, o reconsiderar los "
            "valores de pérdida adoptados."))
        return bloques

    con_economia = soluciones[0].S_M is not None
    con_costo = any(sol.costo for sol in soluciones)
    dinero = lambda v: f"{v:,.0f}".replace(",", "&nbsp;")          # noqa: E731

    # (título, ancho, a la derecha, cómo se escribe la celda de una solución)
    columnas = [("N.º", 10, False, lambda sol: str(len(sol.nombres))),
                ("Medidas", None, False,
                 lambda sol: " + ".join(medida(n) for n in sol.nombres) or "(sin medidas)")]
    if forma == "con_factor":
        columnas.append(("Factor que cambia", 40, False,
                         lambda sol: factores_que_cambian(caso, sol.medidas)))
    if forma != "solo_porcentaje":
        columnas.append((f"R<sub>{tipo}</sub> resultante", 28, True,
                         lambda sol: cientifico(sol.riesgo)))
    columnas.append(("Reduce", 20, True, lambda sol: _reduccion(base, sol.riesgo)))
    if con_costo:
        columnas.append(("Costo", 22, True, lambda sol: dinero(sol.costo)))
    if con_economia:
        columnas.append(("S<sub>M</sub>", 22, True, lambda sol: dinero(sol.S_M)))

    ancho_libre = 166 - sum(c[1] for c in columnas if c[1])
    filas = [[c[0] for c in columnas]]
    for sol in soluciones[:MEDIDAS_QUE_SE_MUESTRAN]:
        filas.append([c[3](sol) for c in columnas])
    orden = ("según el análisis del Anexo D (mayor ahorro anual primero)" if con_economia
             else "por costo y, con el mismo costo, de menos a más medidas" if con_costo
             else "de menos a más medidas (columna N.º) y, con la misma cantidad, de "
                  + ("mayor a menor reducción" if forma == "solo_porcentaje"
                     else "menor a mayor riesgo resultante")
                  + "; no se cargaron costos")
    bloques += [
        d.Parrafo("Combinaciones que llevan el riesgo por debajo del valor tolerable, "
                  f"ordenadas {orden}. «Reduce» es la parte del riesgo sin medidas "
                  f"(R<sub>{tipo}</sub> = {cientifico(base)}) que la combinación quita."),
        d.Tabla(filas, anchos=tuple(c[1] or ancho_libre for c in columnas),
                derecha=tuple(i for i, c in enumerate(columnas) if c[2])),
    ]
    if figura:
        bloques.append(d.Figura(
            figura, 140,
            f"Figura {numero_de_figura}. R<sub>{tipo}</sub> sin medidas y con la primera "
            "combinación de la tabla, frente al riesgo tolerable."))
    return bloques


def _veredicto(por_tipo, tipos, soluciones, figuras_veredicto, casos=None, forma="solo_porcentaje"):
    """soluciones y figuras_veredicto: {riesgo: ...}. Cada riesgo que no cumple tiene su
    sección de medidas; si no se buscaron, se dice."""
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

    numero_de_figura = 4
    for t in tipos:
        if t in soluciones:
            figura = figuras_veredicto.get(t)
            bloques += _medidas(t, soluciones[t], figura, numero_de_figura,
                                por_tipo[t]["total"], casos[t] if casos else None, forma)
            numero_de_figura += 1 if figura else 0
        elif t in incumplen:
            bloques += [d.Titulo(f"Medidas de protección para R<sub>{t}</sub>", 2),
                        d.Parrafo(f"No se buscaron medidas de protección para R<sub>{t}</sub>.",
                                  "nota")]
    return bloques


# ---------------------------------------------------------------------------
# 7. Conclusión y firma
# ---------------------------------------------------------------------------

def _frase_de_riesgo(por_tipo, t, soluciones):
    """Lo que hay que decir de un riesgo que no cumple: qué lo causa y qué lo baja."""
    frase = f"R<sub>{t}</sub> = {cientifico(por_tipo[t]['total'])}"
    aportes = aportes_de(por_tipo[t])
    if aportes:
        c, _, pct = aportes[0]
        frase += (f": el componente dominante es {_sub(c)} "
                  f"({escapar(NOMBRES_COMPONENTES[c].lower())}), con {coma(pct, 1)} % del total")
    if t in soluciones:
        if soluciones[t]:
            mejor = soluciones[t][0]
            frase += (f". La primera combinación de medidas de la tabla del numeral 6 "
                      f"({' + '.join(medida(n) for n in mejor.nombres) or 'sin medidas'}) deja "
                      f"R<sub>{t}</sub> en {cientifico(mejor.riesgo)}, frente a un tolerable de "
                      f"{cientifico(mejor.R_T)}")
        else:
            frase += (". Ninguna combinación de las medidas contempladas lo lleva por debajo "
                      "del tolerable; hay que revisar el caso")
    return frase + "."


def _conclusion(por_tipo, tipos, soluciones, proyecto):
    incumplen = [t for t in tipos if not por_tipo[t]["cumple"]]
    if not incumplen:
        principal = (f"La estructura evaluada <b>cumple</b> el criterio de riesgo tolerable de "
                     f"la NTC 4552-2:2023 para los riesgos {_lista_de_riesgos(tipos)}.")
    else:
        principal = (f"La estructura evaluada <b>no cumple</b> el criterio de riesgo tolerable "
                     f"de la NTC 4552-2:2023 para {_lista_de_riesgos(incumplen)}.")

    quien = escapar((proyecto or {}).get("Diseñador", "") or "Diseñador")
    return (
        [d.Titulo("7. Conclusión y firma"), d.Parrafo(principal)]
        + [d.Parrafo(_frase_de_riesgo(por_tipo, t, soluciones)) for t in incumplen]
        + [d.Espacio(14),
           d.Tabla([["_" * 34, "", "_" * 34],
                    [quien, "", "Revisó"]], anchos=(70, 26, 70), cabecera=False)]
    )


# ---------------------------------------------------------------------------
# 8. Referencias
# ---------------------------------------------------------------------------

def _referencias(usa_nasa, usa_mapa):
    refs = [
        "ICONTEC. <i>NTC 4552-2:2023 — Protección contra el rayo. Parte 2: Evaluación del "
        "riesgo</i> (E: Protection against lightning. Part 2: Risk management).",
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
          fecha=None, medidas_como: str = "solo_porcentaje") -> d.Documento:
    """El informe completo como Documento.

    casos: {tipo: {"estructura", "lineas", "zonas", "N_G", "emplazamiento"}}, lo que
        devuelve EditorCaso.casos_por_tipo().
    por_tipo: {tipo: resultado}, lo que devuelve EditorCaso.evaluar(): los MISMOS números
        que muestra el panel.
    ficha: la FichaNG del sitio (solo si N_G salió de coordenadas); sin ella el informe
        lo dice en vez de inventarla.
    soluciones: las medidas de medidas.explorar(). Un dict {riesgo: lista} da las de cada
        riesgo que no cumple; una lista sola vale para el riesgo desarrollado. None = no se
        buscaron. Una lista vacía SÍ se informa: no hay ninguna combinación que baste.
    figuras: {"mapa", "area", "aporte", "veredicto"} -> ruta PNG; "veredicto" puede ser un
        dict {riesgo: ruta}. Las que falten no salen.
    tipo: el riesgo que se desarrolla; por omisión, el más bajo de los evaluados.
    medidas_como: la tabla de medidas. Por omisión "solo_porcentaje" (medidas y % que
        reduce); también "completa" (además el R resultante) y "con_factor" (además el
        factor que cambia cada combinación).
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
    soluciones = _por_riesgo(soluciones, tipo)
    bloques += _veredicto(por_tipo, tipos, soluciones,
                          _por_riesgo(figuras.get("veredicto"), tipo), casos, medidas_como)
    bloques += _conclusion(por_tipo, tipos, soluciones, proyecto)
    bloques += _referencias(
        usa_nasa=emplazamiento is not None and emplazamiento.modo == "coordenadas",
        usa_mapa=bool(figuras.get("mapa")))

    return d.Documento(
        titulo="Evaluación del riesgo por descargas<br/>eléctricas atmosféricas",
        subtitulo="NTC 4552-2:2023 — Protección contra el rayo. "
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