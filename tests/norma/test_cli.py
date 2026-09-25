"""
Paso 34: prueba el CLI (python -m calculate_risk.norma <archivo.json>) sin
lanzar un proceso aparte -- llama main() directo y captura lo que imprime.
"""
import os

from calculate_risk.norma.__main__ import main

RUTA_CASA_RURAL = os.path.join(
    os.path.dirname(__file__), "..", "..", "casos", "casa_rural.json"
)


def test_cli_imprime_el_riesgo_total_y_cumple(capsys):
    codigo = main([RUTA_CASA_RURAL])
    salida = capsys.readouterr().out

    assert codigo == 0
    assert "R1 = 2.506e-05" in salida
    assert "NO CUMPLE" in salida
    assert "R_V = 2.4e-05" in salida


def test_cli_sin_argumentos_muestra_uso_y_falla(capsys):
    codigo = main([])
    salida = capsys.readouterr().out

    assert codigo == 1
    assert "Uso:" in salida