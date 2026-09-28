"""
Paso 59: el dibujante PDF. Toma un `Documento` y escribe el archivo con reportlab.

No hace ninguna cuenta ni conoce la norma: solo compone. Tres cosas que cuidan al lector
y que el programa viejo (LaTeX) no hacía:

  * NUNCA deja un cuadro negro en silencio. Las fuentes base del PDF solo traen
    Latin-1/WinAnsi; un carácter fuera de eso (Σ, ≈, →…) se sustituye por algo legible
    y queda anotado en `Resultado.advertencias`.
  * Una figura que falta, o una fórmula sin matplotlib, no rompen el informe: salen como
    un aviso en su sitio y en `advertencias`.
  * El índice y el «página X de N» son reales: se compone dos veces (la primera para
    saber en qué página cae cada sección).

matplotlib se importa DENTRO de la fórmula, y sin pyplot, para no tocar el backend de
quien ya lo esté usando.
"""
import io
import os
from dataclasses import dataclass, field

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, Image, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

from calculate_risk.informe import documento as d

AZUL = colors.HexColor("#2a78d6")
NARANJA = colors.HexColor("#eb6834")
GRIS = colors.HexColor("#555555")
GRIS_CLARO = colors.HexColor("#999999")
FONDO_AZUL = colors.HexColor("#f2f7fd")
FONDO_NARANJA = colors.HexColor("#fdf4ef")

MARGEN = 22 * mm
ANCHO_UTIL = 166 * mm
DPI_FORMULA = 600

CUERPO = ParagraphStyle("cuerpo", fontName="Times-Roman", fontSize=10.5, leading=14.5,
                        alignment=TA_JUSTIFY, spaceAfter=6)
NOTA = ParagraphStyle("nota", fontName="Times-Italic", fontSize=8.8, leading=11.5,
                      textColor=GRIS, spaceAfter=4, alignment=TA_JUSTIFY)
SECCION = ParagraphStyle("seccion", fontName="Times-Bold", fontSize=12.5, leading=16,
                         spaceBefore=14, spaceAfter=6)
SUBSECCION = ParagraphStyle("subseccion", fontName="Times-Bold", fontSize=10.8, leading=14,
                            spaceBefore=9, spaceAfter=4)
PIE_FIGURA = ParagraphStyle("pie_figura", fontName="Times-Roman", fontSize=8.8, leading=11.5,
                            textColor=GRIS, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
AVISO = ParagraphStyle("aviso", fontName="Times-Italic", fontSize=9, leading=12,
                       textColor=NARANJA, spaceAfter=6)

# Lo que las fuentes base no traen y tiene un equivalente honesto en texto.
SUSTITUTOS = {"≈": "~", "→": "->", "←": "<-", "≤": "<=", "≥": ">=",
              "−": "-", "–": "-", "—": "-", "Σ": "suma", "π": "pi",
              "Ω": "ohm", " ": " ", " ": " "}


@dataclass
class Resultado:
    ruta: str
    paginas: int = 0
    secciones: list = field(default_factory=list)      # [(titulo, pagina)]
    advertencias: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Texto seguro
# ---------------------------------------------------------------------------

def _legible(texto: str, advertencias: list) -> str:
    """Cambia lo que Times-Roman no dibuja; lo que no tiene sustituto va como «?»."""
    salida = []
    for caracter in str(texto):
        try:
            caracter.encode("cp1252")
            salida.append(caracter)
            continue
        except UnicodeEncodeError:
            pass
        cambio = SUSTITUTOS.get(caracter)
        if cambio is None:
            cambio = "?"
        salida.append(cambio)
        nota = f"Carácter «{caracter}» (U+{ord(caracter):04X}) no disponible en el PDF; salió como «{cambio}»."
        if nota not in advertencias:
            advertencias.append(nota)
    return "".join(salida)


class _Encabezado(Paragraph):
    """Un título que sabe su nivel, para que el dibujante anote en qué página cae."""

    def __init__(self, texto, estilo, nivel, plano):
        super().__init__(texto, estilo)
        self.nivel = nivel
        self.plano = plano


class _Documento(BaseDocTemplate):
    def __init__(self, *argumentos, **nombrados):
        super().__init__(*argumentos, **nombrados)
        self.secciones = []

    def afterFlowable(self, flowable):
        if isinstance(flowable, _Encabezado) and flowable.nivel == 1:
            self.secciones.append((flowable.plano, self.page))


# ---------------------------------------------------------------------------
# Bloques -> flowables
# ---------------------------------------------------------------------------

def _celda(texto, advertencias, negrita=False, derecha=False):
    estilo = ParagraphStyle("celda", fontName="Times-Bold" if negrita else "Times-Roman",
                            fontSize=9.5, leading=12, alignment=2 if derecha else 0)
    return Paragraph(_legible(texto, advertencias), estilo)


def _tabla(bloque, advertencias):
    columnas = len(bloque.filas[0])
    pesos = bloque.anchos or (1,) * columnas
    total = float(sum(pesos))
    anchos = [ANCHO_UTIL * peso / total for peso in pesos]
    datos = [[_celda(texto, advertencias, negrita=bloque.cabecera and i == 0,
                     derecha=j in bloque.derecha)
              for j, texto in enumerate(fila)]
             for i, fila in enumerate(bloque.filas)]
    tabla = Table(datos, colWidths=anchos, repeatRows=1 if bloque.cabecera else 0)
    estilo = [("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LINEABOVE", (0, 0), (-1, 0), 0.9, colors.black),
              ("LINEBELOW", (0, -1), (-1, -1), 0.9, colors.black)]
    if bloque.cabecera:
        estilo.append(("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def _recuadro(bloque, advertencias):
    color = AZUL if bloque.cumple else NARANJA
    fondo = FONDO_AZUL if bloque.cumple else FONDO_NARANJA
    texto = Paragraph(_legible(bloque.texto, advertencias), ParagraphStyle(
        "veredicto", fontName="Times-Bold", fontSize=11, leading=15.5, textColor=color))
    tabla = Table([[texto]], colWidths=[ANCHO_UTIL])
    tabla.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, color), ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return tabla


def _figura(bloque, advertencias):
    pie = Paragraph(_legible(bloque.pie, advertencias), PIE_FIGURA) if bloque.pie else None
    try:
        ancho, alto = ImageReader(bloque.ruta).getSize()
    except Exception:
        advertencias.append(f"Falta la figura «{os.path.basename(str(bloque.ruta))}»; "
                            "el informe sale sin ella.")
        aviso = Paragraph(_legible(f"[Figura no disponible: {bloque.pie or bloque.ruta}]",
                                   []), AVISO)
        return [aviso]
    ancho_pt = bloque.ancho_mm * mm
    imagen = Image(bloque.ruta, width=ancho_pt, height=alto * ancho_pt / ancho, hAlign="CENTER")
    return [imagen] + ([pie] if pie else [])


def _formula(bloque, advertencias):
    """La ecuación como imagen (mathtext). Sin matplotlib, o si la sintaxis falla,
    sale el texto de la fórmula y queda la advertencia."""
    try:
        from matplotlib import rc_context
        from matplotlib.figure import Figure
        with rc_context({"mathtext.fontset": "stix", "font.family": "serif"}):
            figura = Figure(figsize=(0.01, 0.01))
            figura.text(0, 0, f"${bloque.tex}$", fontsize=bloque.tam)
            memoria = io.BytesIO()
            figura.savefig(memoria, format="png", dpi=DPI_FORMULA, transparent=True,
                           bbox_inches="tight", pad_inches=0.02)
        memoria.seek(0)
        ancho, alto = ImageReader(memoria).getSize()
        memoria.seek(0)
        escala = 72.0 / DPI_FORMULA
        return Image(memoria, width=ancho * escala, height=alto * escala, hAlign="CENTER")
    except Exception as error:      # ImportError, o mathtext que no entiende la sintaxis
        advertencias.append(f"No se pudo componer la fórmula «{bloque.tex}»: "
                            f"{type(error).__name__}.")
        return Paragraph(_legible(d.escapar(bloque.tex), []), ParagraphStyle(
            "formula_plana", fontName="Courier", fontSize=9.5, leading=12, alignment=TA_CENTER))


def _contenido(bloque, paginas, advertencias, secciones):
    filas = []
    for i, texto in enumerate(secciones):
        filas.append([texto, str(paginas[i]) if i < len(paginas) else ""])
    titulo = Paragraph(_legible(bloque.titulo, advertencias), SECCION)
    if not filas:
        return [titulo]
    tabla = _tabla(d.Tabla(filas, anchos=(140, 26), derecha=(1,), cabecera=False), advertencias)
    return [titulo, tabla]


def _flujo(bloques, paginas, advertencias, secciones):
    flujo = []
    for bloque in bloques:
        if isinstance(bloque, d.Titulo):
            estilo = SECCION if bloque.nivel == 1 else SUBSECCION
            texto = _legible(bloque.texto, advertencias)
            flujo.append(_Encabezado(texto, estilo, bloque.nivel, texto))
        elif isinstance(bloque, d.Parrafo):
            estilo = CUERPO if bloque.estilo == "cuerpo" else NOTA
            flujo.append(Paragraph(_legible(bloque.texto, advertencias), estilo))
        elif isinstance(bloque, d.Formula):
            flujo += [_formula(bloque, advertencias), Spacer(1, 3)]
        elif isinstance(bloque, d.Tabla):
            flujo += [_tabla(bloque, advertencias), Spacer(1, 6)]
        elif isinstance(bloque, d.Figura):
            flujo += _figura(bloque, advertencias)
        elif isinstance(bloque, d.Recuadro):
            flujo += [_recuadro(bloque, advertencias), Spacer(1, 6)]
        elif isinstance(bloque, d.Espacio):
            flujo.append(Spacer(1, bloque.mm * mm))
        elif isinstance(bloque, d.Salto):
            flujo.append(PageBreak())
        elif isinstance(bloque, d.Contenido):
            flujo += _contenido(bloque, paginas, advertencias, secciones)
        else:
            raise TypeError(f"Bloque desconocido: {type(bloque).__name__}")
    return flujo


def _portada(documento, advertencias):
    def estilo(nombre, **nombrados):
        return ParagraphStyle(nombre, **nombrados)

    flujo = [Spacer(1, 10 * mm)]
    if documento.sobretitulo:
        espaciado = " &nbsp; ".join(" ".join(palabra) for palabra in
                                    _legible(documento.sobretitulo.upper(), advertencias).split())
        flujo.append(Paragraph(espaciado, estilo("sobretitulo", fontName="Times-Roman",
                                                 fontSize=9.5, textColor=AZUL, spaceAfter=10)))
    flujo.append(Paragraph(_legible(documento.titulo, advertencias), estilo(
        "titulo", fontName="Times-Bold", fontSize=26, leading=31, spaceAfter=8)))
    if documento.subtitulo:
        flujo.append(Paragraph(_legible(documento.subtitulo, advertencias), estilo(
            "subtitulo", fontName="Times-Italic", fontSize=11.5, leading=15,
            textColor=GRIS, spaceAfter=14)))
    return flujo + _flujo(documento.portada, [], advertencias, [])


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def _marcos(documento, total, advertencias):
    izq = _legible(documento.encabezado_izq, advertencias)
    der = _legible(documento.encabezado_der, advertencias)
    pie = _legible(documento.pie, advertencias)
    pie_portada = _legible(documento.pie_portada or documento.pie, advertencias)

    def portada(lienzo, doc):
        lienzo.saveState()
        lienzo.setStrokeColor(AZUL)
        lienzo.setLineWidth(2.2)
        lienzo.line(MARGEN, 268 * mm, MARGEN + ANCHO_UTIL, 268 * mm)
        lienzo.setStrokeColor(GRIS_CLARO)
        lienzo.setLineWidth(0.5)
        lienzo.line(MARGEN, 266 * mm, MARGEN + ANCHO_UTIL, 266 * mm)
        lienzo.line(MARGEN, 28 * mm, MARGEN + ANCHO_UTIL, 28 * mm)
        lienzo.setFont("Times-Roman", 8.5)
        lienzo.setFillColor(GRIS)
        lienzo.drawString(MARGEN, 22 * mm, pie_portada)
        lienzo.drawRightString(MARGEN + ANCHO_UTIL, 22 * mm, f"{doc.page} de {total}")
        lienzo.restoreState()

    def normal(lienzo, doc):
        lienzo.saveState()
        lienzo.setFont("Times-Roman", 8.5)
        lienzo.setFillColor(GRIS)
        lienzo.drawString(MARGEN, 285 * mm, izq)
        lienzo.drawRightString(MARGEN + ANCHO_UTIL, 285 * mm, der)
        lienzo.setStrokeColor(colors.HexColor("#bbbbbb"))
        lienzo.setLineWidth(0.5)
        lienzo.line(MARGEN, 283 * mm, MARGEN + ANCHO_UTIL, 283 * mm)
        lienzo.line(MARGEN, 17 * mm, MARGEN + ANCHO_UTIL, 17 * mm)
        lienzo.drawString(MARGEN, 12 * mm, pie)
        lienzo.drawRightString(MARGEN + ANCHO_UTIL, 12 * mm, f"{doc.page} de {total}")
        lienzo.restoreState()

    return portada, normal


def _componer(documento, destino, paginas, total):
    """Una pasada. Devuelve (documento reportlab, advertencias)."""
    advertencias = []
    doc = _Documento(destino, pagesize=A4, leftMargin=MARGEN, rightMargin=MARGEN,
                     topMargin=26 * mm, bottomMargin=22 * mm,
                     title=_legible(documento.titulo, advertencias),
                     author=_legible(documento.autor, advertencias))
    en_portada, en_pagina = _marcos(documento, total, advertencias)
    plantillas = [
        PageTemplate(id="portada", onPage=en_portada, frames=[Frame(
            MARGEN, 30 * mm, ANCHO_UTIL, 232 * mm, id="p",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)]),
        PageTemplate(id="normal", onPage=en_pagina, frames=[Frame(
            doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")]),
    ]
    doc.addPageTemplates(plantillas)
    flujo = _portada(documento, advertencias)
    flujo += [NextPageTemplate("normal"), PageBreak()]
    flujo += _flujo(documento.bloques, paginas, advertencias, documento.secciones())
    doc.build(flujo)
    return doc, advertencias


def dibujar(documento: d.Documento, ruta: str) -> Resultado:
    """Escribe el PDF en `ruta` y dice cuántas páginas salieron, en cuál cae cada
    sección y qué tuvo que avisar por el camino."""
    paginas, total = [], 0
    for _ in range(3):                    # la 1.ª mide; la 2.ª casi siempre ya coincide
        memoria = io.BytesIO()
        doc, advertencias = _componer(documento, memoria, paginas, total)
        medidas = [pagina for _, pagina in doc.secciones]
        if medidas == paginas and doc.page == total:
            break
        paginas, total = medidas, doc.page
    with open(ruta, "wb") as archivo:
        archivo.write(memoria.getvalue())
    return Resultado(ruta=str(ruta), paginas=doc.page, secciones=list(doc.secciones),
                     advertencias=advertencias)