"""
El contador de visitas de la página, en un archivo JSON.

En Railway el archivo va en el volumen permanente (RAILWAY_VOLUME_MOUNT_PATH), que
sobrevive a cada despliegue; en el computador queda en datos/visitas.json. Se
escribe en un archivo temporal y se renombra, para que un corte a mitad de
escritura no deje el contador en cero.
"""
import json
import os
import threading
from pathlib import Path


def ruta_por_omision() -> Path:
    if os.environ.get("CONTADOR_ARCHIVO"):
        return Path(os.environ["CONTADOR_ARCHIVO"])
    volumen = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")
    if volumen:
        return Path(volumen) / "visitas.json"
    return Path(__file__).resolve().parent.parent / "datos" / "visitas.json"


class Contador:
    """Lleva la cuenta de visitas; seguro con varios hilos en un mismo proceso."""

    def __init__(self, ruta: Path):
        self.ruta = Path(ruta)
        self._candado = threading.Lock()

    def leer(self) -> int:
        try:
            guardadas = int(json.loads(self.ruta.read_text(encoding="utf-8"))["visitas"])
        except (OSError, ValueError, KeyError, TypeError):
            guardadas = 0
        # Un piso por si el archivo se pierde (una mudanza del volumen, por ejemplo):
        # el contador nunca baja de CONTADOR_MINIMO.
        return max(guardadas, int(os.environ.get("CONTADOR_MINIMO", 0) or 0))

    def sumar(self) -> int:
        with self._candado:
            visitas = self.leer() + 1
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.ruta.with_suffix(".tmp")
            temporal.write_text(json.dumps({"visitas": visitas}), encoding="utf-8")
            os.replace(temporal, self.ruta)
            return visitas
