"""
Trazabilidad de las memorias de cálculo: qué se imprime en el PDF (un registro y una
huella) y qué se guarda en el servidor para que quien escanee el QR pueda comprobar que la
memoria existe y qué dijo.

Se guarda lo MÍNIMO y nada personal: ni el nombre del proyecto, ni del cliente, ni del
proyectista. Las coordenadas se redondean (0,01° ≈ 1 km) para que el registro no señale
una instalación.

Este módulo no sabe de HTTP ni de bases de datos: solo arma el `Registro`. Dónde se guarda
lo decide quien lo use (web/verificaciones.py).
"""
import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone

from calculate_risk.informe.documento import Verificacion
from calculate_risk.version import VERSION as VERSION_MOTOR
URL_BASE = "https://charlightning.org/verify"
LARGO_HUELLA_IMPRESA = 10


@dataclass(frozen=True)
class Registro:
    id: str                 # CHL-2026-7F3A9C
    created_at: str         # ISO 8601, UTC
    coordinates: str        # «5.69,-76.66», o vacío si N_G se declaró sin coordenadas
    risk_r1: float          # R1 calculado; None si no se evaluó R1
    verdict: str            # «CUMPLE» / «NO CUMPLE»
    data_hash: str          # sha256 (hex) de los datos de entrada y los riesgos
    engine_version: str = VERSION_MOTOR      # «2.0.0» o «2.0.0+290a637» (con la revisión del código)

    def impreso(self) -> Verificacion:
        return Verificacion(id=self.id, url=f"{URL_BASE}/{self.id}",
                            huella=self.data_hash[:LARGO_HUELLA_IMPRESA].upper())


def _plano(valor):
    """Dataclasses y diccionarios a algo que json sepa escribir, siempre igual."""
    if is_dataclass(valor) and not isinstance(valor, type):
        return _plano(asdict(valor))
    if isinstance(valor, dict):
        return {str(k): _plano(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_plano(v) for v in valor]
    return valor


def huella_de(casos: dict, por_tipo: dict) -> str:
    """sha256 de los datos de entrada y del riesgo total de cada tipo. Los mismos datos
    dan siempre la misma huella; cambiar cualquiera la cambia."""
    contenido = {"casos": _plano(casos),
                 "riesgos": {str(t): por_tipo[t]["total"] for t in sorted(por_tipo)}}
    texto = json.dumps(contenido, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(texto.encode("ascii")).hexdigest()


def nuevo_id(ahora: datetime) -> str:
    return f"CHL-{ahora.year}-{secrets.token_hex(3).upper()}"


def _coordenadas(casos: dict) -> str:
    for caso in casos.values():
        emplazamiento = caso.get("emplazamiento")
        if emplazamiento is not None and emplazamiento.modo == "coordenadas" \
                and emplazamiento.lat is not None and emplazamiento.lon is not None:
            return f"{emplazamiento.lat:.2f},{emplazamiento.lon:.2f}"
    return ""


def registro_de(casos: dict, por_tipo: dict, ahora: datetime = None, revision: str = "") -> Registro:
    """El registro de una memoria: todo lo que se guarda en el servidor. `revision` es el
    commit del código que hizo el cálculo, para poder bajar exactamente esa versión."""
    ahora = ahora or datetime.now(timezone.utc)
    return Registro(
        id=nuevo_id(ahora),
        created_at=ahora.isoformat(timespec="seconds"),
        coordinates=_coordenadas(casos),
        risk_r1=por_tipo[1]["total"] if 1 in por_tipo else None,
        verdict="CUMPLE" if all(por_tipo[t]["cumple"] for t in por_tipo) else "NO CUMPLE",
        data_hash=huella_de(casos, por_tipo),
        engine_version=f"{VERSION_MOTOR}+{revision}" if revision else VERSION_MOTOR)
