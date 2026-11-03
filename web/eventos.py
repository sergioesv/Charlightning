"""
Los pasos que da la gente en la calculadora, para saber dónde se quedan.

Se guarda solo el nombre del paso, el instante y un código de visitante que cambia cada
día (un hash de IP + navegador + fecha + sal secreta): no se guarda la IP ni nada del
proyecto, y no sirve para seguir a nadie de un día a otro. El archivo va en el mismo
volumen que el contador (eventos.jsonl).
"""
import hashlib
import json
import os
import threading
import time
from collections import defaultdict
from pathlib import Path

PASOS = ("ejemplo", "ciudad", "ubicacion", "buscar", "calcular", "informe")
MAX_BYTES = 20 * 1024 * 1024   # tope del archivo: más allá se deja de anotar


def ruta_por_omision() -> Path:
    if os.environ.get("EVENTOS_ARCHIVO"):
        return Path(os.environ["EVENTOS_ARCHIVO"])
    volumen = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")
    if volumen:
        return Path(volumen) / "eventos.jsonl"
    return Path(__file__).resolve().parent.parent / "datos" / "eventos.jsonl"


class Eventos:
    def __init__(self, ruta: Path, sal: str = ""):
        self.ruta = Path(ruta)
        self._sal = sal or os.environ.get("EVENTOS_SAL") or os.urandom(16).hex()
        self._candado = threading.Lock()

    def _visitante(self, ip: str, agente: str, dia: str) -> str:
        crudo = f"{self._sal}|{ip}|{agente}|{dia}".encode()
        return hashlib.sha256(crudo).hexdigest()[:10]

    def anotar(self, paso: str, ip: str, agente: str, ahora: float = None) -> bool:
        if paso not in PASOS:
            return False
        ahora = time.time() if ahora is None else ahora
        dia = time.strftime("%Y-%m-%d", time.gmtime(ahora))
        linea = json.dumps({"t": int(ahora), "d": dia, "p": paso,
                            "v": self._visitante(ip, agente, dia)}, separators=(",", ":"))
        with self._candado:
            try:
                if self.ruta.exists() and self.ruta.stat().st_size > MAX_BYTES:
                    return False
                self.ruta.parent.mkdir(parents=True, exist_ok=True)
                with self.ruta.open("a", encoding="utf-8") as f:
                    f.write(linea + "\n")
            except OSError:
                return False
        return True

    def resumen(self) -> dict:
        """Por día: cuántos visitantes distintos hicieron cada paso (y el total de veces)."""
        visitantes = defaultdict(lambda: defaultdict(set))
        veces = defaultdict(lambda: defaultdict(int))
        try:
            with self.ruta.open(encoding="utf-8") as f:
                for linea in f:
                    try:
                        e = json.loads(linea)
                        visitantes[e["d"]][e["p"]].add(e["v"])
                        veces[e["d"]][e["p"]] += 1
                    except (ValueError, KeyError, TypeError):
                        continue
        except OSError:
            pass
        dias = {d: {p: {"visitantes": len(v), "veces": veces[d][p]} for p, v in pasos.items()}
                for d, pasos in sorted(visitantes.items())}
        total = {p: len({v for d in visitantes for v in visitantes[d].get(p, ())}) for p in PASOS}
        return {"pasos": list(PASOS), "dias": dias, "visitantes_por_paso": total}
