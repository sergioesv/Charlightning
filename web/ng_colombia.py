"""
La página «N_G en Colombia por ciudad»: la densidad de descargas a tierra de las
capitales y de otras ciudades, sacada de la misma climatología de la NASA que usa la
calculadora. Se genera una vez y queda como página estática (web/estatico/ng-colombia.html):

    python -m web.ng_colombia

Las coordenadas son las del centro de cada ciudad; el valor es el de la celda de 0,1°
más cercana. Para un proyecto se deben usar las coordenadas exactas del sitio.
"""
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


def _coma(x: float, d: int) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def html_de_tabla(filas) -> str:
    renglones = "\n".join(
        f'      <tr><td>{ciudad}</td><td>{depto}</td>'
        f'<td class="num">{_coma(lat, 3)}</td><td class="num">{_coma(lon, 3)}</td>'
        f'<td class="num"><b>{_coma(n_g, 1)}</b></td>'
        f'<td class="num"><a href="/?lat={lat}&amp;lon={lon}">calcular</a></td></tr>'
        for ciudad, depto, lat, lon, n_g, _ in filas)
    return f'''<div class="tarjeta tabla-envuelta">
  <table>
    <thead><tr><th>Ciudad</th><th>Departamento</th><th class="num">Latitud</th>
      <th class="num">Longitud</th><th class="num">N_G [rayos/km² año]</th><th></th></tr></thead>
    <tbody>
{renglones}
    </tbody>
  </table>
</div>'''


def generar():
    filas = tabla()
    ficha = filas[0][5]
    plantilla = (CARPETA / "citar.html").read_text(encoding="utf-8")
    pagina = re.sub(r"<title>[^<]*</title>",
                    "<title>N_G en Colombia: densidad de descargas a tierra por ciudad</title>", plantilla)
    pagina = re.sub(r'<meta name="description" content="[^"]*">',
                    '<meta name="description" content="Densidad de descargas a tierra N_G '
                    '(rayos/km² año) de las capitales y principales ciudades de Colombia, para el '
                    'análisis de riesgo por rayos según la NTC 4552-2 y el RETIE. Datos NASA LIS/OTD.">',
                    pagina)
    # Los metadatos que trae la plantilla (canónica, Open Graph) son de «Cómo citar».
    titulo = re.search(r"<title>([^<]*)</title>", pagina).group(1)
    descripcion = re.search(r'<meta name="description" content="([^"]*)">', pagina).group(1)
    pagina = pagina.replace("https://charlightning.org/citar.html", "https://charlightning.org/ng-colombia.html")
    pagina = re.sub(r'<meta property="og:title" content="[^"]*">',
                    f'<meta property="og:title" content="{titulo}">', pagina)
    pagina = re.sub(r'<meta property="og:description" content="[^"]*">',
                    f'<meta property="og:description" content="{descripcion}">', pagina)
    pagina = pagina.replace(' aria-current="page"', "").replace(
        '<a href="/ng-colombia.html">', '<a href="/ng-colombia.html" aria-current="page">')
    alta, baja = filas[0], filas[-1]
    cuerpo = f'''<h1>N_G en Colombia: densidad de descargas a tierra por ciudad</h1>
<p class="subtitulo">Cuántos rayos caen a tierra por km² al año en las capitales y en otras
ciudades de Colombia. Es el dato de partida del análisis de riesgo por rayos de la
NTC 4552-2:2023 (IEC 62305-2) que exige el RETIE.</p>

<p>Colombia está entre los países con más actividad de rayos del mundo, y varía mucho de una
región a otra: en esta tabla va de unos {_coma(baja[4], 1)} rayos/km² año en {baja[0]} a unos
{_coma(alta[4], 1)} en {alta[0]}. Por eso N_G se debe tomar del sitio exacto del proyecto y no
de un valor general.</p>

{html_de_tabla(filas)}

<h2>De dónde salen estos valores</h2>
<ul>
  <li>Climatología de destellos <b>{ficha.producto or "LIS/OTD"}</b> de la NASA (sensores LIS y
  OTD en satélite), en celdas de 0,1°.</li>
  <li>N_G = destellos totales × {_coma(ficha.fraccion_nube_tierra, 3)}, la fracción usual de
  destellos que llegan a tierra.</li>
  <li>Coordenadas del centro de cada ciudad; el valor es el de la celda más cercana.</li>
</ul>
<p class="aviso">Son valores de referencia. Para un proyecto use las coordenadas exactas del sitio
en la <a href="/">calculadora</a>, que trae la ficha completa del dato para la memoria de
cálculo, o un valor de una red local de detección con su fuente.</p>
'''
    pagina = re.sub(r'(<main>\n<div class="publicidad".*?</div>\n).*?</main>',
                    lambda m: m.group(1) + cuerpo + "</main>", pagina, flags=re.S)
    (CARPETA / "ng-colombia.html").write_text(pagina, encoding="utf-8")
    return filas


if __name__ == "__main__":
    for ciudad, depto, lat, lon, n_g, _ in generar():
        print(f"{ciudad:24s} {n_g:6.2f}")
