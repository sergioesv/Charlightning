"""
Un contexto de ejemplo para la plantilla memoria.html (los números del Ejemplo E.4 de la
norma, hospital) y la forma de rellenarla. Es la guía para el backend: el día que el PDF
salga de esta plantilla, `contexto()` lo arma armado.py con los números del motor.

    python -m calculate_risk.informe.plantilla.ejemplo salida.html
"""
import base64
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

CARPETA = Path(__file__).resolve().parent
FUENTES = CARPETA.parent / "fuentes"


def _qr(texto: str):
    """(svg, data-uri). El ejemplo usa zxing-cpp; en producción, segno u otro."""
    import zxingcpp
    svg = zxingcpp.create_barcode(texto, zxingcpp.BarcodeFormat.QRCode).to_svg()
    svg = svg[svg.index("<svg"):]
    lado = re.search(r'width="(\d+)"', svg).group(1)
    # Sin viewBox el QR no se escala: se quita el tamaño fijo y se deja la caja.
    svg = re.sub(r'(width|height)="\d+"', "", svg, count=2).replace(
        "<svg", f'<svg viewBox="0 0 {lado} {lado}" shape-rendering="crispEdges"', 1)
    en_pie = svg.replace("<svg", '<svg width="9mm" height="9mm"', 1)
    uri = "data:image/svg+xml;base64," + base64.b64encode(en_pie.encode()).decode()
    return svg, uri


def contexto() -> dict:
    codigo = "CHL-2026-0892"
    svg, uri = _qr(f"https://charlightning.org/verify/{codigo}")
    cien = lambda n: f"{n:.1f} %".replace(".", ",")
    comps = [("R<sub>B</sub>", "Daño físico por descarga en la estructura", 4.26e-4),
             ("R<sub>C</sub>", "Falla de sistemas internos por descarga en la estructura", 1.206e-4),
             ("R<sub>V</sub>", "Daño físico por descarga en una línea", 9.245e-5),
             ("R<sub>M</sub>", "Falla de sistemas internos por descarga cerca de la estructura", 3.429e-5),
             ("R<sub>W</sub>", "Falla de sistemas internos por descarga en una línea", 2.617e-5),
             ("R<sub>A</sub>", "Lesiones a seres vivos por descarga en la estructura", 9.815e-8)]
    total = 6.996e-4
    cient = lambda v: f"{v:.3e}".replace(".", ",").replace("e-0", " × 10<sup>-").replace("e-", " × 10<sup>-") + "</sup>"
    return dict(
        marca="™", version="1.0", fuentes_url=FUENTES.as_uri(), codigo=codigo,
        huella="3F9A21C07B", qr_svg=svg, qr_uri=uri, verify_url="charlightning.org/verify",
        proyecto=dict(nombre="Hospital de prueba (Ejemplo E.4)", ubicacion="Quibdó, Chocó",
                      coordenadas="5,692° N · 76,658° O", disenador="Ing. Nombre Apellido",
                      matricula="", fecha="7 de octubre de 2026"),
        veredicto=dict(cumple=False, titulo="NO CUMPLE — REQUIERE MEDIDAS DE PROTECCIÓN",
                       detalle=("<span class='mono'>R<sub>1</sub> = 6,996 × 10<sup>-4</sup> &gt; "
                                "R<sub>T</sub> = 1 × 10<sup>-5</sup></span>. El componente "
                                "dominante es R<sub>B</sub> (60,9 %). Ver numeral 5.")),
        riesgos=[dict(id=1, nombre="Pérdida de vidas humanas", calculado="6,996 × 10<sup>-4</sup>",
                      tolerable="1 × 10<sup>-5</sup>", cumple=False)],
        emplazamiento=dict(N_G="2,91", fuente="Climatología LIS/OTD de la NASA (coordenadas)",
                           ficha=dict(celda="2,450° N, 76,650° O", distancia="4,6 km",
                                      destellos="11,64", fraccion="0,250", horas="158 h",
                                      producto="LIS/OTD VHRFC 1998–2013")),
        estructura=dict(L=50, W=150, H=10, Hp=0, CD="1", nt="1 000", ct="1"),
        A_D="22 327,4", N_D="8,931 × 10<sup>-2</sup>",
        lineas=[dict(nombre="potencia", L=500, CI="0,5", CT="0,2", CE="0,5", UW="2,5"),
                dict(nombre="telecom", L=300, CI="0,5", CT="1", CE="0,5", UW="1,5")],
        zonas=[dict(nombre="Z1", nz=10, tz="8 760", PB=1, rf=0, rp=1, LF=0),
               dict(nombre="Z2", nz=950, tz="8 760", PB=1, rf="0,01", rp=1, LF="0,1"),
               dict(nombre="Z3", nz=35, tz="8 760", PB=1, rf="0,001", rp=1, LF="0,1")],
        desarrollo=dict(
            riesgo=1,
            ecuaciones=["R<sub>B</sub> = (N<sub>D</sub> × P<sub>B</sub> × L<sub>B</sub>) = 8,931×10<sup>-2</sup> × 1 × 4,8×10<sup>-3</sup> = <b>4,26×10<sup>-4</sup></b>",
                        "R<sub>C</sub> = (N<sub>D</sub> × P<sub>C</sub> × L<sub>C</sub>) = <b>1,206×10<sup>-4</sup></b>"],
            componentes=[dict(id=i, descripcion=d, valor=cient(v), parte=100 * v / total,
                              parte_texto=cien(100 * v / total)) for i, d, v in comps],
            total=cient(total)),
        medidas=[dict(n=2, texto="Techo metálico o captación completa con armadura continua (Tabla B.2) + DPS de NPR I (Tabla B.3)", reduce="99,4 %"),
                 dict(n=3, texto="Techo metálico con armadura continua + cable blindado dentro de un conducto metálico (Tabla B.5)", reduce="99,939 %")],
        conclusion=("La estructura evaluada <b>no cumple</b> el criterio de riesgo tolerable de la "
                    "NTC 4552-2:2023 para R<sub>1</sub>. R<sub>1</sub> = 6,996 × 10<sup>-4</sup>; "
                    "la primera combinación de medidas de la tabla del numeral 5 lo deja en "
                    "4,355 × 10<sup>-6</sup>, frente a un tolerable de 1 × 10<sup>-5</sup>."),
    )


def renderizar(datos: dict = None) -> str:
    entorno = Environment(loader=FileSystemLoader(str(CARPETA)),
                          autoescape=select_autoescape(["html"]))
    return entorno.get_template("memoria.html").render(**(datos or contexto()))


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(renderizar(), encoding="utf-8")
