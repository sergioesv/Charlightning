"""
El formulario de contacto: el mensaje llega al correo del autor sin que la
dirección aparezca nunca en la página ni en el repositorio.

La dirección vive solo en la variable CONTACTO_CORREO del servidor, y el envío
sale por la API de Resend (RESEND_API_KEY). Cada mensaje se guarda además en
mensajes.jsonl, en el mismo volumen que el contador, por si el envío falla.
"""
import json
import os
import re
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL_RESEND = "https://api.resend.com/emails"
REMITENTE = "Charlightning <onboarding@resend.dev>"
CORREO_VALIDO = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$")

MAX_NOMBRE = 120
MAX_CORREO = 200
MAX_MENSAJE = 4000

# Por qué escriben: va en el asunto del correo, para ver de un vistazo cuáles son trabajo.
MOTIVOS = {
    "estudio": "Estudio de riesgo (RETIE / NTC 4552-2)",
    "revision": "Revisión de un diseño",
    "otro": "Otro",
}


class MensajeInvalido(ValueError):
    """Falta algo o sobra: el texto dice qué."""


def revisar(datos: dict) -> dict:
    """{nombre, correo, motivo, mensaje} limpios, o MensajeInvalido con la razón."""
    if not isinstance(datos, dict):
        raise MensajeInvalido("El mensaje no llegó bien.")
    nombre = str(datos.get("nombre", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    mensaje = str(datos.get("mensaje", "")).strip()
    motivo = str(datos.get("motivo", "") or "otro").strip()
    if motivo not in MOTIVOS:
        motivo = "otro"
    if not nombre:
        raise MensajeInvalido("Falta su nombre.")
    if not mensaje:
        raise MensajeInvalido("Falta el mensaje.")
    if correo and not CORREO_VALIDO.match(correo):
        raise MensajeInvalido("El correo no parece válido.")
    if len(nombre) > MAX_NOMBRE or len(correo) > MAX_CORREO or len(mensaje) > MAX_MENSAJE:
        raise MensajeInvalido(f"El mensaje es muy largo (máximo {MAX_MENSAJE} caracteres).")
    return {"nombre": nombre, "correo": correo, "motivo": motivo, "mensaje": mensaje}


class Buzon:
    """Guarda cada mensaje y, si el servidor sabe a dónde, lo manda por correo."""

    def __init__(self, archivo: Path, destino: str = "", clave: str = "", enviar=None):
        self.archivo = Path(archivo)
        self.destino = destino
        self.clave = clave
        self._enviar = enviar or _enviar_por_resend
        self._candado = threading.Lock()

    @classmethod
    def desde_entorno(cls, carpeta: Path):
        return cls(carpeta / "mensajes.jsonl",
                   destino=os.environ.get("CONTACTO_CORREO", ""),
                   clave=os.environ.get("RESEND_API_KEY", ""))

    def recibir(self, datos: dict) -> bool:
        """Guarda el mensaje y lo envía. True si salió por correo."""
        limpio = revisar(datos)
        registro = {**limpio, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        with self._candado:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            with self.archivo.open("a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        if not (self.destino and self.clave):
            return False
        return self._enviar(self.clave, self.destino, limpio)


def _enviar_por_resend(clave: str, destino: str, m: dict) -> bool:
    cuerpo = {
        "from": REMITENTE,
        "to": [destino],
        "subject": f"[Charlightning] {MOTIVOS[m['motivo']]} — {m['nombre']}",
        "text": (f"Motivo: {MOTIVOS[m['motivo']]}\nNombre: {m['nombre']}\n"
                 f"Correo: {m['correo'] or '(no lo dejó)'}\n\n"
                 f"{m['mensaje']}\n\n— Enviado desde el formulario de contacto de Charlightning"),
    }
    if m["correo"]:
        cuerpo["reply_to"] = m["correo"]
    peticion = urllib.request.Request(
        URL_RESEND, data=json.dumps(cuerpo).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json",
                 "User-Agent": "Charlightning"})
    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            return 200 <= respuesta.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
