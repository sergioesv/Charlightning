"""
Paso 59: el modelo del documento. Los bloques y nada más.

Un informe es una lista de bloques. Este módulo NO sabe dibujar (eso es pdf.py) y NO
contiene ni una cuenta ni un valor de la norma: recibe texto ya hecho. Por eso el día
que haga falta otra salida (HTML, Word) se escribe otro dibujante y el contenido no
se toca.

El texto de los bloques admite un marcado mínimo: <b>, <i>, <sub>, <super> y <br/>.
Todo lo que venga de un usuario (nombre del proyecto, dirección, fuente de N_G) hay
que pasarlo por `escapar()`: un «&» o un «<» sueltos romperían la composición.

Nada de Unicode para sub y superíndices (₁, ²): las fuentes base del PDF no los traen
y salen cuadros negros. Se usa <sub> y <super>.
"""
from dataclasses import dataclass, field

ESTILOS_DE_PARRAFO = ("cuerpo", "nota")


def escapar(texto) -> str:
    """Texto de usuario -> texto seguro para el marcado."""
    return str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@dataclass
class Titulo:
    """Un encabezado. Nivel 1 = sección (entra al contenido), nivel 2 = subsección."""
    texto: str
    nivel: int = 1

    def __post_init__(self):
        if self.nivel not in (1, 2):
            raise ValueError("El nivel de un título es 1 o 2.")


@dataclass
class Parrafo:
    texto: str
    estilo: str = "cuerpo"

    def __post_init__(self):
        if self.estilo not in ESTILOS_DE_PARRAFO:
            raise ValueError(f"Estilo de párrafo desconocido: {self.estilo!r}.")


@dataclass
class Formula:
    """Una ecuación en sintaxis mathtext (la de matplotlib), centrada."""
    tex: str
    tam: float = 11


@dataclass
class Tabla:
    """Filas de texto con marcado. La primera fila es la cabecera si `cabecera`.

    `anchos` son pesos relativos (se reparten el ancho de la página); `derecha` son
    los índices de las columnas alineadas a la derecha (las numéricas). Se dibuja al estilo
    «booktabs»: solo líneas horizontales.
    """
    filas: list
    anchos: tuple = None
    derecha: tuple = ()
    cabecera: bool = True

    def __post_init__(self):
        if not self.filas:
            raise ValueError("Una tabla necesita al menos una fila.")
        columnas = len(self.filas[0])
        if any(len(fila) != columnas for fila in self.filas):
            raise ValueError("Todas las filas de una tabla tienen que tener las mismas columnas.")
        if self.anchos is not None and len(self.anchos) != columnas:
            raise ValueError("Hay que dar un ancho por columna.")
        if any(not 0 <= c < columnas for c in self.derecha):
            raise ValueError("Una columna alineada a la derecha no existe.")


@dataclass
class Figura:
    """Una imagen PNG con su pie. Si el archivo no está, el PDF lo dice y sigue."""
    ruta: str
    ancho_mm: float = 150
    pie: str = ""


@dataclass
class Recuadro:
    """El veredicto: borde y fondo rojos si no cumple, verdes si cumple. El color nunca
    va solo: la `etiqueta` (por omisión «CUMPLE» / «NO CUMPLE») dice lo mismo en palabras."""
    texto: str
    cumple: bool
    etiqueta: str = ""


@dataclass
class Firma:
    """El cajetín de cierre, en dos columnas: a la izquierda quien firma el proyecto
    (nombre y matrícula si se dieron; si no, quedan en blanco para llenar a mano) y a la
    derecha la autoría del motor, con el texto fijo que da `autoria`."""
    proyectista: str = ""
    matricula: str = ""
    declaracion: str = ""
    autoria: str = ""
    sello: str = ""            # líneas de texto plano bajo la autoría (registro, huella...)


@dataclass
class Espacio:
    mm: float = 4


@dataclass
class Salto:
    """Salto de página."""


@dataclass
class Contenido:
    """El índice de las secciones (títulos de nivel 1) con su página real."""
    titulo: str = "Contenido"


@dataclass
class Verificacion:
    """Lo que el PDF imprime para poder comprobar la memoria en línea."""
    id: str            # CHL-2026-7F3A9C
    url: str           # https://charlightning.org/verify/CHL-2026-7F3A9C
    huella: str        # los primeros caracteres de la huella de los datos


@dataclass
class Documento:
    """Título, subtítulo y sobretítulo llevan marcado; el encabezado, el pie y el autor
    son texto plano (se dibujan sin composición): NO se escapan."""
    titulo: str
    subtitulo: str = ""
    sobretitulo: str = ""
    autor: str = ""
    encabezado_izq: str = ""
    encabezado_der: str = ""
    pie: str = ""
    pie_portada: str = ""
    credito: str = ""                               # autoría del motor, bajo el título (marcado)
    verificacion: Verificacion = None               # None = sin QR (programa de escritorio)
    portada: list = field(default_factory=list)     # bloques bajo el título de la portada
    bloques: list = field(default_factory=list)     # el cuerpo, desde la página 2

    def secciones(self) -> list:
        """Los títulos de nivel 1 del cuerpo, en orden."""
        return [b.texto for b in self.bloques if isinstance(b, Titulo) and b.nivel == 1]