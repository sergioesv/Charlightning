"""
Paso 34: CLI de calculate_risk.norma.

Uso:
    python -m calculate_risk.norma casos/casa_rural.json
"""
import sys

from calculate_risk.norma import riesgos
from calculate_risk.norma.casos import cargar_caso


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Uso: python -m calculate_risk.norma <archivo.json>")
        return 1

    caso = cargar_caso(argv[0])
    resultados = riesgos.evaluar(
        caso["estructura"], caso["lineas"], caso["zonas"], caso["N_G"], tipos=caso["tipos"]
    )

    for tipo, r in resultados.items():
        estado = "CUMPLE" if r["cumple"] else "NO CUMPLE"
        print(f"R{tipo} = {r['total']:.4g}  (R_T = {r['R_T']:.4g})  -> {estado}")
        for componente in riesgos.COMPONENTES:
            if r[componente]:
                print(f"    {componente} = {r[componente]:.4g}")

    return 0


if __name__ == "__main__":
    sys.exit(main())