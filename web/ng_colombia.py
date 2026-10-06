"""
La página «N_G en Colombia por ciudad»: la densidad de descargas a tierra de las
capitales y de otras ciudades, sacada de la misma climatología de la NASA que usa la
calculadora. Se genera una vez y queda como página estática (web/estatico/ng-colombia.html):

    python -m web.ng_colombia

Las coordenadas son las del centro de cada ciudad; el valor es el de la celda de 0,1°
más cercana. Para un proyecto se deben usar las coordenadas exactas del sitio.
"""
import json
import math
import re
from pathlib import Path

from calculate_risk.norma import densidad

# (ciudad, departamento, latitud, longitud): capitales y otras ciudades grandes.
CIUDADES = (
    ("Bogotá", "Bogotá D.C.", 4.711, -74.072),
    ("Medellín", "Antioquia", 6.244, -75.581),
    ("Cali", "Valle del Cauca", 3.452, -76.532),
    ("Barranquilla", "Atlántico", 10.964, -74.796),
    ("Cartagena", "Bolívar", 10.391, -75.479),
    ("Cúcuta", "Norte de Santander", 7.894, -72.508),
    ("Bucaramanga", "Santander", 7.119, -73.123),
    ("Pereira", "Risaralda", 4.813, -75.696),
    ("Santa Marta", "Magdalena", 11.241, -74.205),
    ("Ibagué", "Tolima", 4.438, -75.232),
    ("Manizales", "Caldas", 5.068, -75.517),
    ("Villavicencio", "Meta", 4.142, -73.626),
    ("Pasto", "Nariño", 1.214, -77.281),
    ("Montería", "Córdoba", 8.748, -75.881),
    ("Neiva", "Huila", 2.927, -75.282),
    ("Armenia", "Quindío", 4.534, -75.681),
    ("Valledupar", "Cesar", 10.463, -73.253),
    ("Popayán", "Cauca", 2.444, -76.614),
    ("Sincelejo", "Sucre", 9.305, -75.398),
    ("Tunja", "Boyacá", 5.535, -73.367),
    ("Riohacha", "La Guajira", 11.544, -72.907),
    ("Quibdó", "Chocó", 5.692, -76.658),
    ("Florencia", "Caquetá", 1.614, -75.606),
    ("Yopal", "Casanare", 5.339, -72.395),
    ("Arauca", "Arauca", 7.084, -70.759),
    ("Mocoa", "Putumayo", 1.152, -76.647),
    ("San José del Guaviare", "Guaviare", 2.571, -72.645),
    ("Leticia", "Amazonas", -4.215, -69.940),
    ("Inírida", "Guainía", 3.865, -67.924),
    ("Mitú", "Vaupés", 1.198, -70.173),
    ("Puerto Carreño", "Vichada", 6.189, -67.486),
    ("San Andrés", "San Andrés y Providencia", 12.584, -81.701),
    ("Barrancabermeja", "Santander", 7.065, -73.854),
    ("Rionegro", "Antioquia", 6.155, -75.374),
    ("Apartadó", "Antioquia", 7.883, -76.626),
)

CARPETA = Path(__file__).resolve().parent / "estatico"


def tabla() -> list:
    """[(ciudad, departamento, lat, lon, N_G, ficha)] ordenada de mayor a menor N_G."""
    filas = []
    for ciudad, depto, lat, lon in CIUDADES:
        ficha = densidad.ficha_desde_lat_lon(lat, lon)
        filas.append((ciudad, depto, lat, lon, ficha.N_G, ficha))
    return sorted(filas, key=lambda f: -f[4])


def fraccion_prentice_mackerras(lat: float) -> float:
    """f = 1/(1+Z) con Z = 4,16 + 2,16·cos(3λ) (Prentice y Mackerras, 1977)."""
    z = 4.16 + 2.16 * math.cos(math.radians(3 * lat))
    return 1.0 / (1.0 + z)


def _coma(x: float, d: int) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def html_de_tabla(filas) -> str:
    renglones = "\n".join(
        f'      <tr><td>{ciudad}</td><td>{depto}</td>'
        f'<td class="num">{_coma(lat, 3)}</td><td class="num">{_coma(lon, 3)}</td>'
        f'<td class="num">{_coma(ficha.destellos_totales, 1)}</td>'
        f'<td class="num"><b>{_coma(n_g, 1)}</b></td>'
        f'<td class="num">{_coma(ficha.destellos_totales * fraccion_prentice_mackerras(lat), 1)}</td>'
        f'<td class="num"><a href="/?lat={lat}&amp;lon={lon}">calcular</a></td></tr>'
        for ciudad, depto, lat, lon, n_g, ficha in filas)
    return f'''<div class="tarjeta tabla-envuelta">
  <table>
    <thead><tr><th>Ciudad</th><th>Departamento</th><th class="num">Latitud</th>
      <th class="num">Longitud</th><th class="num">Destellos totales<br>(NASA)</th>
      <th class="num">DDT / N_G<br>f = 0,227</th><th class="num">DDT / N_G<br>Prentice-Mackerras</th><th></th></tr></thead>
    <tbody>
{renglones}
    </tbody>
  </table>
</div>'''


TITULO = "DDT en Colombia: densidad de descargas a tierra (N_G) por ciudad"
DESCRIPCION = ("Densidad de descargas a tierra DDT o N_G (rayos/km² año) de las capitales y "
               "principales ciudades de Colombia, con la fracción nube-tierra discutida, para el "
               "análisis de riesgo por rayos según la NTC 4552-2 y el RETIE. Datos NASA LIS/OTD.")


def preguntas(filas) -> list:
    """(pregunta, respuesta) en texto plano: van en la página y en el JSON-LD FAQPage."""
    alta, baja = filas[0], filas[-1]
    bogota = next(f for f in filas if f[0] == "Bogotá")
    return [
        ("¿Qué es la DDT o N_G?",
         "Es la densidad de descargas a tierra: el número de rayos nube-tierra por kilómetro "
         "cuadrado por año en un sitio. La NTC 4552 la llama N_G y en Colombia se conoce también "
         "como DDT. Es el dato de partida del análisis de riesgo por rayos de la NTC 4552-2:2023 "
         "(IEC 62305-2) que exige el RETIE."),
        ("¿Cuál es la DDT de Bogotá?",
         f"Con la climatología LIS/OTD de la NASA y una fracción nube-tierra de 0,227, unos "
         f"{_coma(bogota[4], 1)} rayos/km² año en el centro de la ciudad; con la fracción de "
         f"Prentice y Mackerras, unos "
         f"{_coma(bogota[5].destellos_totales * fraccion_prentice_mackerras(bogota[2]), 1)}."),
        ("¿Dónde caen más rayos en Colombia?",
         f"De las ciudades de esta tabla, la de mayor DDT es {alta[0]} ({_coma(alta[4], 1)} "
         f"rayos/km² año) y la de menor es {baja[0]} ({_coma(baja[4], 1)}). Las zonas más activas "
         f"del país están en el Magdalena Medio, el Catatumbo, Antioquia y el Pacífico."),
        ("¿Por qué no basta con los datos del satélite?",
         "Porque el satélite cuenta todos los destellos, también los que se quedan dentro de la "
         "nube, y el análisis de riesgo necesita solo los que caen a tierra. Hay que multiplicar "
         "por la fracción nube-tierra, que no es una constante: según el valor que se use, la DDT "
         "puede cambiar en más de un 60 %. Lo mejor es un dato medido por una red de detección local."),
    ]


def _json_ld(filas) -> str:
    datos = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": r}}
                       for q, r in preguntas(filas)],
    }
    return ('<script type="application/ld+json">\n'
            + json.dumps(datos, ensure_ascii=False, indent=1) + "\n</script>\n")


def generar():
    filas = tabla()
    ficha = filas[0][5]
    plantilla = (CARPETA / "citar.html").read_text(encoding="utf-8")
    pagina = re.sub(r"<title>[^<]*</title>", f"<title>{TITULO}</title>", plantilla)
    pagina = re.sub(r'<meta name="description" content="[^"]*">',
                    f'<meta name="description" content="{DESCRIPCION}">', pagina)
    # Los metadatos que trae la plantilla (canónica, Open Graph) son de «Cómo citar».
    pagina = pagina.replace("https://charlightning.org/citar.html", "https://charlightning.org/ng-colombia.html")
    pagina = re.sub(r'<meta property="og:title" content="[^"]*">',
                    f'<meta property="og:title" content="{TITULO}">', pagina)
    pagina = re.sub(r'<meta property="og:description" content="[^"]*">',
                    f'<meta property="og:description" content="{DESCRIPCION}">', pagina)
    pagina = pagina.replace("</head>", _json_ld(filas) + "</head>", 1)
    pagina = pagina.replace(' aria-current="page"', "").replace(
        '<a href="/ng-colombia.html">', '<a href="/ng-colombia.html" aria-current="page">')
    alta, baja = filas[0], filas[-1]
    f = ficha.fraccion_nube_tierra
    f_pm = fraccion_prentice_mackerras(5.0)
    faq = "\n".join(f"<h3>{q}</h3>\n<p>{r}</p>" for q, r in preguntas(filas))
    cuerpo = f"""<h1>{TITULO}</h1>
<p class="subtitulo">Cuántos rayos caen a tierra por km² al año en las capitales y en otras
ciudades de Colombia. Es el dato de partida del análisis de riesgo por rayos de la
NTC 4552-2:2023 (IEC 62305-2) que exige el RETIE.</p>

<p>Colombia está entre los países con más actividad de rayos del mundo, y varía mucho de una
región a otra: en esta tabla la DDT va de unos {_coma(baja[4], 1)} rayos/km² año en {baja[0]} a
unos {_coma(alta[4], 1)} en {alta[0]}. Por eso N_G se debe tomar del sitio exacto del proyecto y
no de un valor general.</p>

{html_de_tabla(filas)}

<h2>Ojo: el satélite ve todos los rayos, no solo los que caen a tierra</h2>
<p>Los sensores LIS y OTD de la NASA cuentan <b>todos los destellos</b>: los que van de la nube
a tierra y los que se quedan dentro de la nube o van de una nube a otra, que son la mayoría. El
análisis de riesgo necesita solo los de nube a tierra, así que:</p>
<p style="text-align:center"><b>DDT = N_G = destellos totales × f</b>, &nbsp; con
&nbsp; f = 1 / (1 + Z)</p>
<p>donde Z es cuántos destellos intranube hay por cada uno a tierra. Z no es una constante:
cambia con la latitud, el tipo de tormenta y la región, y los estudios publicados dan
valores desde menos de 2 hasta más de 6. Con el valor que se escoja, la DDT puede cambiar en más de un 60 %, y eso se nota
en R1:</p>
<ul>
  <li><b>f = {_coma(f, 3)}</b> (Z ≈ {_coma(1 / f - 1, 1)}): es el valor que usa la calculadora
  por omisión y el de la columna principal. Es cercano a la relación media medida en
  continente por Boccippio y otros (2001), y del lado conservador para el riesgo.</li>
  <li><b>f ≈ 0,25</b> (Z ≈ 3): Rakov (2016), en <i>Fundamentals of Lightning</i>, da que cerca de
  la cuarta parte de los destellos en el mundo son nube-tierra. Es casi el mismo valor: la DDT
  sale un {round(100 * 0.25 / f - 100)} % más alta que con {_coma(f, 3)}.</li>
  <li><b>Prentice y Mackerras (1977)</b>: Z = 4,16 + 2,16·cos(3λ), con λ la latitud. Cerca del
  ecuador da Z ≈ 6,3 y f ≈ {_coma(f_pm, 3)}: una DDT cerca de {round(100 * f_pm / f)} % de la
  anterior.</li>
  <li>Una <b>red de detección local</b> mide directamente los rayos a tierra y no necesita
  esta fracción. Si tiene ese dato con su fuente, úselo en la calculadora con «Declarado».</li>
</ul>
<p>En la calculadora la fracción nube-tierra es un campo editable y queda escrita en la memoria
de cálculo, para que quien revise el estudio sepa de dónde salió la DDT.</p>

<h2>De dónde salen estos valores</h2>
<ul>
  <li>Climatología de destellos <b>{ficha.producto or "LIS/OTD"}</b> de la NASA (sensores LIS y
  OTD en satélite), en celdas de 0,1°.</li>
  <li>Coordenadas del centro de cada ciudad; el valor es el de la celda más cercana.</li>
</ul>
<p class="aviso">Son valores de referencia. Para un proyecto use las coordenadas exactas del sitio
en la <a href="/">calculadora</a>, que trae la ficha completa del dato para la memoria de
cálculo, o un valor de una red local de detección con su fuente.</p>

<h2>Preguntas frecuentes</h2>
{faq}

<h2>Referencias</h2>
<ul>
  <li>Cecil, D. J. (2015). LIS/OTD 0.1 Degree Very High Resolution Gridded Lightning Full
  Climatology (VHRFC). NASA GHRC DAAC. doi:10.5067/LIS/LIS-OTD/DATA302</li>
  <li>Rakov, V. A. (2016). <i>Fundamentals of Lightning</i>. Cambridge University Press.</li>
  <li>Prentice, S. A. y Mackerras, D. (1977). The ratio of cloud to cloud-ground lightning
  flashes in thunderstorms. <i>Journal of Applied Meteorology</i>, 16(5), 545–550.</li>
  <li>Boccippio, D. J., Cummins, K. L., Christian, H. J. y Goodman, S. J. (2001). Combined
  satellite- and surface-based estimation of the intracloud–cloud-to-ground lightning ratio
  over the continental United States. <i>Monthly Weather Review</i>, 129(1), 108–122.</li>
  <li>ICONTEC. NTC 4552-2:2023. Protección contra descargas eléctricas atmosféricas (rayos).
  Parte 2: Manejo del riesgo.</li>
</ul>
"""
    pagina = re.sub(r'(<main>\n<div class="publicidad".*?</div>\n).*?</main>',
                    lambda m: m.group(1) + cuerpo + "</main>", pagina, flags=re.S)
    (CARPETA / "ng-colombia.html").write_text(pagina, encoding="utf-8")
    return filas


if __name__ == "__main__":
    for ciudad, depto, lat, lon, n_g, _ in generar():
        print(f"{ciudad:24s} {n_g:6.2f}")
