"""
Dónde se guardan los registros de las memorias de cálculo, para que el QR del PDF
(charlightning.org/verify/<id>) pueda comprobar que una memoria existe y qué dijo.

Dos implementaciones con la misma forma (`guardar(registro)` y `buscar(id)`):

  * SupabaseVerificaciones: la tabla `verifications` de Supabase, por su API REST. Se usa
    cuando el servidor tiene SUPABASE_URL y SUPABASE_SERVICE_KEY. La clave de servicio
    vive solo en las variables del servidor; la tabla no tiene políticas públicas, así que
    nadie puede leerla ni escribirla desde el navegador.
  * ArchivoVerificaciones: un archivo JSONL en el volumen de Railway, junto al contador.
    Es lo que se usa mientras Supabase no esté configurado.

Lo que se guarda es lo que define calculate_risk.informe.verificacion.Registro: ningún
nombre de proyecto, de cliente ni de proyectista.
"""
import json
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict
from pathlib import Path

from calculate_risk.informe.verificacion import Registro

ID_VALIDO = re.compile(r"^CHL-\d{4}-[0-9A-F]{6}$")
CAMPOS = ("id", "created_at", "coordinates", "risk_r1", "verdict", "data_hash", "engine_version")


def _registro(fila: dict) -> Registro:
    return Registro(**{campo: fila.get(campo) for campo in CAMPOS})


class ArchivoVerificaciones:
    """Un registro por línea en un archivo JSONL."""

    def __init__(self, archivo):
        self.archivo = Path(archivo)
        self._candado = threading.Lock()

    def guardar(self, registro: Registro) -> None:
        with self._candado:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            with self.archivo.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(registro), ensure_ascii=False) + "\n")

    def buscar(self, id_: str):
        if not ID_VALIDO.match(id_) or not self.archivo.exists():
            return None
        with self._candado, self.archivo.open(encoding="utf-8") as f:
            for linea in f:
                fila = json.loads(linea)
                if fila.get("id") == id_:
                    return _registro(fila)
        return None


class SupabaseVerificaciones:
    """La tabla `verifications` por la API REST de Supabase (PostgREST)."""

    def __init__(self, url: str, clave: str, tabla: str = "verifications", espera: float = 8.0):
        self.base = f"{url.rstrip('/')}/rest/v1/{tabla}"
        self.espera = espera
        self._cabeceras = {"apikey": clave, "Authorization": f"Bearer {clave}",
                           "Content-Type": "application/json"}

    def _pedir(self, peticion):
        with urllib.request.urlopen(peticion, timeout=self.espera) as respuesta:
            return respuesta.read()

    def guardar(self, registro: Registro) -> None:
        peticion = urllib.request.Request(
            self.base, data=json.dumps(asdict(registro)).encode("utf-8"), method="POST",
            headers={**self._cabeceras, "Prefer": "return=minimal"})
        self._pedir(peticion)

    def buscar(self, id_: str):
        if not ID_VALIDO.match(id_):
            return None
        consulta = urllib.parse.urlencode({"id": f"eq.{id_}", "select": ",".join(CAMPOS)})
        filas = json.loads(self._pedir(urllib.request.Request(
            f"{self.base}?{consulta}", headers=self._cabeceras)))
        return _registro(filas[0]) if filas else None


def desde_entorno(carpeta: Path):
    """Supabase si el servidor tiene sus dos variables; si no, un archivo en `carpeta`."""
    url = os.environ.get("SUPABASE_URL", "")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if url and clave:
        return SupabaseVerificaciones(url, clave)
    return ArchivoVerificaciones(Path(carpeta) / "verificaciones.jsonl")
