"""
Las páginas y sus archivos, con la versión pegada a cada enlace.

Cada .html y cada .js se sirve con sus referencias a /estilos.css, /calculadora.js,
./campos.js… cambiadas por /estilos.css?v=<versión>. La versión es una huella del
contenido de la carpeta, así que cambia con cada despliegue que toque un archivo.
Con eso el navegador puede guardar los CSS y JS mucho tiempo (son inmutables para
esa versión) y nunca mezcla una página nueva con una hoja de estilos vieja.
"""
import hashlib
import re
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response

# href="/estilos.css" o src="/contador.js" en las páginas
EN_HTML = re.compile(r'((?:href|src)="/[\w\-/]+\.(?:css|js))(")')
# import ... from "./campos.js" en los módulos
EN_JS = re.compile(r'(from\s+"\./[\w\-]+\.js)(")')


def huella_de(carpeta: Path) -> str:
    """Una huella corta de todo lo que hay en la carpeta."""
    h = hashlib.sha256()
    for archivo in sorted(Path(carpeta).rglob("*")):
        if archivo.is_file():
            h.update(archivo.name.encode())
            h.update(archivo.read_bytes())
    return h.hexdigest()[:10]


def con_version(texto: str, version: str, es_html: bool) -> str:
    patron = EN_HTML if es_html else EN_JS
    return patron.sub(lambda m: f"{m.group(1)}?v={version}{m.group(2)}", texto)


class EstaticosVersionados(StaticFiles):
    """StaticFiles que pega la versión a las referencias de las páginas y los módulos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = huella_de(self.directory)
        self._textos = {}

    async def get_response(self, path, scope):
        respuesta = await super().get_response(path, scope)
        if not isinstance(respuesta, FileResponse):
            return respuesta
        ruta = Path(respuesta.path)
        if ruta.suffix not in (".html", ".js"):
            return respuesta
        if ruta not in self._textos:
            texto = ruta.read_text(encoding="utf-8")
            self._textos[ruta] = con_version(texto, self.version, ruta.suffix == ".html")
        tipo = "text/html; charset=utf-8" if ruta.suffix == ".html" else "text/javascript; charset=utf-8"
        return Response(self._textos[ruta], media_type=tipo)
