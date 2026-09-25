"""
Paso 39a: barridos de sensibilidad y exportacion a CSV.

Ademas de comprobar que el CSV sale bien, aqui hay una prueba de PROPIEDAD:
R tiene que ser exactamente proporcional a N_G, porque N_G multiplica a todas
las frecuencias (N_D, N_M, N_L, N_I) y no aparece en ninguna probabilidad ni
en ninguna perdida. Si algun dia eso deja de cumplirse, algo se rompio en la
cadena de calculo.
"""
import csv

import pytest
from pytest import approx

from calculate_risk.norma import barridos, medidas
from calculate_risk.norma.adaptador import caso_desde_pantalla
from tests.datos_pantalla import CASA_RURAL


def _casa_rural():
    c = caso_desde_pantalla(CASA_RURAL, tipo=1)
    return c["estructura"], c["lineas"], c["zonas"], c["N_G"]


def _leer(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


# ---------------------------------------------------------------------------
# Barridos
# ---------------------------------------------------------------------------

def test_el_riesgo_es_proporcional_a_N_G():
    puntos = barridos.barrer(*_casa_rural(), valores=[1, 2, 4, 8], destino="N_G")

    base = puntos[0].riesgo                      # N_G = 1
    for p in puntos:
        assert p.riesgo == approx(base * p.valor, rel=1e-12)

    # Y con N_G = 4 se recupera el valor publicado del Anexo E.2
    assert puntos[2].riesgo == approx(2.51e-5, rel=0.01)


def test_subir_la_altura_sube_el_riesgo():
    # A_D crece con H (ec. A.2), asi que N_D y el riesgo tambien.
    puntos = barridos.barrer(*_casa_rural(), valores=[3, 6, 12, 25, 50],
                             destino="estructura", campo="H")

    riesgos_ = [p.riesgo for p in puntos]
    assert riesgos_ == sorted(riesgos_)
    assert riesgos_[0] < riesgos_[-1]


def test_alargar_la_linea_sube_el_riesgo():
    # A_L = 40*L_L y A_I = 4000*L_L (ecs. A.9 y A.11)
    puntos = barridos.barrer(*_casa_rural(), valores=[100, 500, 1000, 2000],
                             destino="linea", campo="L_L")

    riesgos_ = [p.riesgo for p in puntos]
    assert riesgos_ == sorted(riesgos_)
    # Con 100 m la casa rural si cumple; con 1000 m no.
    assert puntos[0].cumple and not puntos[2].cumple


def test_el_barrido_no_modifica_el_caso_original():
    estructura, lineas, zonas, N_G = _casa_rural()

    barridos.barrer(estructura, lineas, zonas, N_G, valores=[50],
                    destino="estructura", campo="H")
    barridos.barrer(estructura, lineas, zonas, N_G, valores=[9999],
                    destino="linea", campo="L_L")

    assert estructura.H == 6.0
    assert lineas[0].L_L == 1000.0


def test_destino_o_campo_invalidos_avisan():
    estructura, lineas, zonas, N_G = _casa_rural()

    with pytest.raises(ValueError, match="destino"):
        barridos.barrer(estructura, lineas, zonas, N_G, valores=[1], destino="otro")

    with pytest.raises(ValueError, match="campo"):
        barridos.barrer(estructura, lineas, zonas, N_G, valores=[1], destino="estructura")


# ---------------------------------------------------------------------------
# Exportacion a CSV
# ---------------------------------------------------------------------------

def test_exportar_barrido(tmp_path):
    puntos = barridos.barrer(*_casa_rural(), valores=[1, 2, 4], destino="N_G")
    ruta = barridos.exportar_barrido(puntos, tmp_path / "ng.csv", "N_G")

    filas = _leer(ruta)
    assert filas[0] == ["N_G", "riesgo", "R_T", "cumple"]
    assert len(filas) == 4                       # cabecera + 3 puntos
    assert filas[1][0] == "1" and filas[1][3] == "1"     # N_G=1 si cumple
    assert filas[3][3] == "0"                            # N_G=4 no cumple


def test_exportar_soluciones(tmp_path):
    estructura, lineas, zonas, N_G = _casa_rural()
    soluciones = medidas.explorar(estructura, lineas, zonas, N_G, tipo=1,
                                  solo_familias={"spcr", "dps"})

    ruta = barridos.exportar_soluciones(soluciones, tmp_path / "medidas.csv")

    filas = _leer(ruta)
    assert filas[0] == list(barridos.COLUMNAS_SOLUCIONES)
    assert len(filas) == len(soluciones) + 1
    # Sin datos economicos, las columnas del Anexo D quedan vacias
    assert filas[1][6:] == ["", "", "", ""]
    # La combinacion se escribe legible, para poder pegarla en el articulo
    assert " + " in filas[-1][0] or filas[-1][1] == "1"