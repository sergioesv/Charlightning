"""
Paso 59: el dibujante PDF. Toma un `Documento` y escribe el archivo con reportlab.

Estilo académico sobrio (informe técnico / paper): Carta, serif incrustada (STIX Two), tablas
al estilo «booktabs» (solo líneas horizontales), un recuadro de veredicto y, si el documento
trae `verificacion`, un QR en la portada y en el pie de cada página. Todo en Python: no
hace falta instalar LaTeX ni un navegador.

No hace ninguna cuenta ni conoce la norma: solo compone. Tres cosas que cuidan al lector:

  * NUNCA deja un cuadro negro en silencio. Un carácter que la fuente no trae (≈, →…) se
    sustituye por algo legible y queda anotado en `Resultado.advertencias`.
  * Una figura que falta, o una fórmula sin matplotlib, no rompen el informe: salen como
    un aviso en su sitio y en `advertencias`.
  * El índice y el «Página X de N» son reales: se compone dos veces (la primera para
    saber en qué página cae cada sección).

matplotlib se importa DENTRO de la fórmula, y sin pyplot, para no tocar el backend de
quien ya lo esté usando.
"""
import io
import os
from dataclasses import dataclass, field
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

from calculate_risk.informe import documento as d

# ---------------------------------------------------------------------------
# Fuentes: STIX Two (serif de aspecto LaTeX) y JetBrains Mono, incrustadas. Si los
# archivos no están, se cae a las fuentes base del PDF y el informe sale igual.
# ---------------------------------------------------------------------------

CARPETA_FUENTES = Path(__file__).resolve().parent / "fuentes"
SERIF, SERIF_N, SERIF_I, SERIF_NI, MONO, MONO_N = (
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic", "Courier", "Courier-Bold")
_CARACTERES = None          # los caracteres que la serif incrustada sabe dibujar


def _registrar_fuentes():
    global SERIF, SERIF_N, SERIF_I, SERIF_NI, MONO, MONO_N, _CARACTERES
    try:
        for nombre, archivo in (("STIX", "STIXTwoText-Regular"), ("STIX-Bold", "STIXTwoText-Bold"),
                                ("STIX-Italic", "STIXTwoText-Italic"),
                                ("STIX-BoldItalic", "STIXTwoText-BoldItalic"),
                                ("JBMono", "JetBrainsMono-Regular"),
                                ("JBMono-Bold", "JetBrainsMono-Bold")):
            pdfmetrics.registerFont(TTFont(nombre, str(CARPETA_FUENTES / f"{archivo}.ttf")))
        pdfmetrics.registerFontFamily("STIX", normal="STIX", bold="STIX-Bold",
                                      italic="STIX-Italic", boldItalic="STIX-BoldItalic")
        pdfmetrics.registerFontFamily("JBMono", normal="JBMono", bold="JBMono-Bold",
                                      italic="JBMono", boldItalic="JBMono-Bold")
    except Exception:
        return
    SERIF, SERIF_N, SERIF_I, SERIF_NI, MONO, MONO_N = (
        "STIX", "STIX-Bold", "STIX-Italic", "STIX-BoldItalic", "JBMono", "JBMono-Bold")
    try:
        from fontTools.ttLib import TTFont as Tipografia
        tipo = Tipografia(str(CARPETA_FUENTES / "STIXTwoText-Regular.ttf"), lazy=True)
        _CARACTERES = set(tipo.getBestCmap())
        tipo.close()
    except Exception:
        _CARACTERES = None


_registrar_fuentes()

# ---------------------------------------------------------------------------
# Colores, medidas y estilos
# ---------------------------------------------------------------------------

TINTA = colors.HexColor("#0F172A")          # texto principal (slate / navy)
GRIS = colors.HexColor("#475569")
GRIS_CLARO = colors.HexColor("#94A3B8")
LINEA = colors.HexColor("#E2E8F0")
ROJO = colors.HexColor("#DC2626")
FONDO_ROJO = colors.HexColor("#FEF2F2")
BORDE_ROJO = colors.HexColor("#FCA5A5")
VERDE = colors.HexColor("#16A34A")
FONDO_VERDE = colors.HexColor("#F0FDF4")
BORDE_VERDE = colors.HexColor("#86EFAC")

PAGINA = LETTER
ANCHO_PAGINA, ALTO_PAGINA = PAGINA
MARGEN = 22 * mm
ANCHO_UTIL = ANCHO_PAGINA - 2 * MARGEN
DPI_FORMULA = 600
LADO_QR_PIE = 9.5 * mm
LADO_QR_PORTADA = 28 * mm

CUERPO = ParagraphStyle("cuerpo", fontName=SERIF, fontSize=10, leading=13.6,
                        alignment=TA_JUSTIFY, spaceAfter=5, textColor=TINTA)
NOTA = ParagraphStyle("nota", fontName=SERIF_I, fontSize=8.5, leading=11,
                      textColor=GRIS, spaceAfter=3, alignment=TA_JUSTIFY)
SECCION = ParagraphStyle("seccion", fontName=SERIF_N, fontSize=12.5, leading=16,
                         spaceBefore=12, spaceAfter=5, textColor=TINTA)
SUBSECCION = ParagraphStyle("subseccion", fontName=SERIF_NI, fontSize=10.5, leading=13.5,
                            spaceBefore=7, spaceAfter=3, textColor=TINTA)
PIE_FIGURA = ParagraphStyle("pie_figura", fontName=SERIF, fontSize=8.8, leading=11.5,
                            textColor=GRIS, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
AVISO = ParagraphStyle("aviso", fontName=SERIF_I, fontSize=9, leading=12,
                       textColor=ROJO, spaceAfter=6)

# Lo que la serif no trae y tiene un equivalente honesto en texto.
SUSTITUTOS = {"≈": "~", "→": "->", "←": "<-", "≤": "<=", "≥": ">=",
              "−": "-", "–": "-", "—": "-", "Σ": "suma", "π": "pi",
              "Ω": "ohm", " ": " ", " ": " "}


@dataclass
class Resultado:
    ruta: str
    paginas: int = 0
    secciones: list = field(default_factory=list)      # [(titulo, pagina)]
    advertencias: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Texto seguro
# ---------------------------------------------------------------------------

def _se_dibuja(caracter: str) -> bool:
    if _CARACTERES is not None:
        return ord(caracter) in _CARACTERES or caracter in "\n\t"
    try:
        caracter.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def _legible(texto: str, advertencias: list) -> str:
    """Cambia lo que la fuente no dibuja; lo que no tiene sustituto va como «?»."""
    salida = []
    for caracter in str(texto):
        if _se_dibuja(caracter) and caracter not in "≈≤≥→←":
            salida.append(caracter)
            continue
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
    estilo = ParagraphStyle("celda", fontName=SERIF_N if negrita else SERIF, fontSize=9.1,
                            leading=11.4, alignment=2 if derecha else 0, textColor=TINTA)
    return Paragraph(_legible(texto, advertencias), estilo)


def _tabla(bloque, advertencias):
    """Estilo «booktabs»: regla gruesa arriba y abajo, fina bajo la cabecera, y entre las
    filas solo una línea muy tenue. Nunca líneas verticales."""
    columnas = len(bloque.filas[0])
    pesos = bloque.anchos or (1,) * columnas
    total = float(sum(pesos))
    anchos = [ANCHO_UTIL * peso / total for peso in pesos]
    datos = [[_celda(texto, advertencias, negrita=bloque.cabecera and i == 0,
                     derecha=j in bloque.derecha)
              for j, texto in enumerate(fila)]
             for i, fila in enumerate(bloque.filas)]
    tabla = Table(datos, colWidths=anchos, repeatRows=1 if bloque.cabecera else 0)
    ultima = len(datos) - 1
    estilo = [("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LINEABOVE", (0, 0), (-1, 0), 1.1, TINTA),
              ("LINEBELOW", (0, ultima), (-1, ultima), 1.1, TINTA)]
    if len(datos) > 2:
        estilo.append(("LINEBELOW", (0, 1 if bloque.cabecera else 0), (-1, ultima - 1),
                       0.3, LINEA))
    if bloque.cabecera:
        estilo.append(("LINEBELOW", (0, 0), (-1, 0), 0.55, TINTA))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def _recuadro(bloque, advertencias):
    """La tarjeta del veredicto: borde y fondo rojos o verdes, y la palabra en grande."""
    color, fondo, borde = ((VERDE, FONDO_VERDE, BORDE_VERDE) if bloque.cumple
                           else (ROJO, FONDO_ROJO, BORDE_ROJO))
    etiqueta = bloque.etiqueta or ("CUMPLE" if bloque.cumple else "NO CUMPLE")
    titulo = Paragraph(_legible(f"VEREDICTO · {etiqueta}", advertencias), ParagraphStyle(
        "veredicto_titulo", fontName=SERIF_N, fontSize=12, leading=15, textColor=color,
        spaceAfter=3))
    texto = Paragraph(_legible(bloque.texto, advertencias), ParagraphStyle(
        "veredicto", fontName=SERIF, fontSize=10.2, leading=14, textColor=TINTA))
    tabla = Table([[[titulo, texto]]], colWidths=[ANCHO_UTIL])
    tabla.setStyle(TableStyle([
        ("ROUNDEDCORNERS", [3, 3, 3, 3]), ("BOX", (0, 0), (-1, -1), 1.1, color), ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return tabla


def _dibujo_qr(url: str, lado: float) -> Drawing:
    """El QR de `url` como dibujo vectorial de `lado` puntos."""
    codigo = qr.QrCodeWidget(url)
    x0, y0, x1, y1 = codigo.getBounds()
    dibujo = Drawing(lado, lado, transform=[lado / (x1 - x0), 0, 0, lado / (y1 - y0), 0, 0])
    dibujo.add(codigo)
    return dibujo


def _verificacion(verificacion, advertencias):
    """El recuadro de la portada: el QR y lo que hay que comparar."""
    estilo = ParagraphStyle("verificar", fontName=SERIF, fontSize=9.4, leading=13, textColor=TINTA)
    codigo = ParagraphStyle("verificar_codigo", fontName=MONO, fontSize=8, leading=12, textColor=GRIS)
    lineas = [Paragraph(_legible(
        "<b>Escanee para verificar autenticidad en charlightning.org/verify</b>", advertencias), estilo),
        Spacer(1, 2),
        Paragraph(_legible(f"Registro {verificacion.id}<br/>Huella de datos {verificacion.huella}",
                           advertencias), codigo),
        Spacer(1, 2),
        Paragraph(_legible("La huella cambia si cambia cualquiera de los datos de entrada. "
                           "Compare el veredicto y los riesgos de esta memoria con los del registro.",
                           advertencias), NOTA)]
    tabla = Table([[_dibujo_qr(verificacion.url, LADO_QR_PORTADA), lineas]],
                  colWidths=[LADO_QR_PORTADA + 8 * mm, ANCHO_UTIL - LADO_QR_PORTADA - 8 * mm])
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOX", (0, 0), (-1, -1), 0.6, LINEA),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return tabla


def _campo(rotulo, valor, advertencias):
    estilo = ParagraphStyle("campo", fontName=SERIF, fontSize=10, leading=13, textColor=TINTA)
    return Paragraph(f'<font name="{SERIF}" size="7" color="#475569">{_legible(rotulo.upper(), advertencias)}</font>'
                     f'<br/>{_legible(valor, advertencias) if valor else "&nbsp;"}', estilo)


def _firma(bloque, advertencias):
    """El cajetín de cierre: a la izquierda quien firma, a la derecha la autoría del motor."""
    cabecera = ParagraphStyle("cajetin_cab", fontName=SERIF_N, fontSize=8, leading=10,
                              textColor=TINTA)
    pequeno = ParagraphStyle("cajetin_decl", fontName=SERIF_I, fontSize=8, leading=10.4,
                             textColor=GRIS, alignment=TA_JUSTIFY)
    autoria = ParagraphStyle("cajetin_autoria", fontName=SERIF, fontSize=9.6, leading=13,
                             textColor=TINTA, alignment=TA_JUSTIFY)
    sello = ParagraphStyle("cajetin_sello", fontName=MONO, fontSize=7.6, leading=11.2, textColor=GRIS)
    derecha = [Paragraph(_legible(bloque.autoria, advertencias), autoria)]
    if bloque.sello:
        derecha += [Spacer(1, 6), Paragraph(_legible(bloque.sello, advertencias), sello)]
    filas = [
        [Paragraph("FIRMA DEL PROYECTISTA RESPONSABLE", cabecera),
         Paragraph("DESARROLLO Y VALIDACIÓN DEL MOTOR", cabecera)],
        [_campo("Nombre completo", bloque.proyectista, advertencias), derecha],
        [_campo("Matrícula profesional", bloque.matricula, advertencias), ""],
        [_campo("Firma o sello", "", advertencias), ""],
        [Paragraph(_legible(bloque.declaracion, advertencias), pequeno), ""],
    ]
    mitad = ANCHO_UTIL / 2
    tabla = Table(filas, colWidths=[mitad, mitad], rowHeights=[None, None, None, 24 * mm, None])
    tabla.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, TINTA), ("LINEAFTER", (0, 0), (0, -1), 0.55, TINTA),
        ("LINEBELOW", (0, 0), (-1, 0), 0.55, TINTA), ("BACKGROUND", (0, 0), (-1, 0), LINEA),
        ("LINEBELOW", (0, 1), (0, 2), 0.3, GRIS_CLARO),
        ("SPAN", (1, 1), (1, 4)), ("LINEABOVE", (0, 4), (0, 4), 0.3, GRIS_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
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
            figura.text(0, 0, f"${bloque.tex}$", fontsize=bloque.tam, color="#0F172A")
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
            "formula_plana", fontName=MONO, fontSize=9, leading=12, alignment=TA_CENTER))


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
            flujo += [Spacer(1, 2), _recuadro(bloque, advertencias), Spacer(1, 8)]
        elif isinstance(bloque, d.Firma):
            flujo += [KeepTogether([Spacer(1, 6), _firma(bloque, advertencias)])]
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

    flujo = [Spacer(1, 4 * mm)]
    if documento.sobretitulo:
        espaciado = " &nbsp; ".join(" ".join(palabra) for palabra in
                                    _legible(documento.sobretitulo.upper(), advertencias).split())
        flujo.append(Paragraph(espaciado, estilo("sobretitulo", fontName=SERIF, fontSize=9,
                                                 textColor=GRIS, alignment=TA_CENTER, spaceAfter=9)))
    flujo.append(Paragraph(_legible(documento.titulo, advertencias), estilo(
        "titulo", fontName=SERIF_N, fontSize=23, leading=28, spaceAfter=7,
        alignment=TA_CENTER, textColor=TINTA)))
    if documento.subtitulo:
        flujo.append(Paragraph(_legible(documento.subtitulo, advertencias), estilo(
            "subtitulo", fontName=SERIF_I, fontSize=11.3, leading=15, textColor=GRIS,
            alignment=TA_CENTER, spaceAfter=9)))
    if documento.credito:
        flujo.append(Table([[""]], colWidths=[ANCHO_UTIL], rowHeights=[2],
                           style=[("LINEABOVE", (0, 0), (-1, 0), 0.6, TINTA)]))
        flujo.append(Paragraph(_legible(documento.credito, advertencias), estilo(
            "credito", fontName=SERIF, fontSize=10, leading=14, textColor=TINTA,
            alignment=TA_CENTER, spaceBefore=4, spaceAfter=10)))
    flujo += _flujo(documento.portada, [], advertencias, [])
    if documento.verificacion is not None:
        flujo += [Spacer(1, 6), _verificacion(documento.verificacion, advertencias)]
    return flujo


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def _marcos(documento, total, advertencias):
    izq = _legible(documento.encabezado_izq, advertencias)
    der = _legible(documento.encabezado_der, advertencias)
    pie = _legible(documento.pie, advertencias)
    qr_pie = (_dibujo_qr(documento.verificacion.url, LADO_QR_PIE)
              if documento.verificacion is not None else None)

    def pagina(lienzo, doc):
        lienzo.saveState()
        # Encabezado: la marca del motor, sobria, en todas las páginas.
        lienzo.setFont(SERIF_I, 8)
        lienzo.setFillColor(GRIS)
        lienzo.drawString(MARGEN, ALTO_PAGINA - 14 * mm, izq)
        lienzo.drawRightString(MARGEN + ANCHO_UTIL, ALTO_PAGINA - 14 * mm, der)
        lienzo.setStrokeColor(TINTA)
        lienzo.setLineWidth(0.6)
        lienzo.line(MARGEN, ALTO_PAGINA - 16.5 * mm, MARGEN + ANCHO_UTIL, ALTO_PAGINA - 16.5 * mm)
        # Pie: qué documento es, quién lo hizo y «Página X de Y».
        lienzo.setStrokeColor(GRIS_CLARO)
        lienzo.setLineWidth(0.4)
        lienzo.line(MARGEN, 20 * mm, MARGEN + ANCHO_UTIL, 20 * mm)
        lienzo.setFont(SERIF, 8)
        lienzo.drawString(MARGEN, 14.5 * mm, pie)
        derecho = MARGEN + ANCHO_UTIL - (LADO_QR_PIE + 3 * mm if qr_pie is not None else 0)
        lienzo.setFillColor(TINTA)
        lienzo.drawRightString(derecho, 14.5 * mm, f"Página {doc.page} de {total}")
        if qr_pie is not None:
            renderPDF.draw(qr_pie, lienzo, MARGEN + ANCHO_UTIL - LADO_QR_PIE, 9.5 * mm)
        lienzo.restoreState()

    return pagina


def _componer(documento, destino, paginas, total):
    """Una pasada. Devuelve (documento reportlab, advertencias)."""
    advertencias = []
    doc = _Documento(destino, pagesize=PAGINA, leftMargin=MARGEN, rightMargin=MARGEN,
                     topMargin=24 * mm, bottomMargin=25 * mm,
                     title=_legible(documento.titulo, advertencias),
                     author=_legible(documento.autor, advertencias))
    en_pagina = _marcos(documento, total, advertencias)
    marco = dict(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    plantillas = [
        PageTemplate(id="portada", onPage=en_pagina, frames=[Frame(
            MARGEN, 25 * mm, ANCHO_UTIL, ALTO_PAGINA - 49 * mm, id="p", **marco)]),
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
