"""
Paso 39: barridos de sensibilidad y exportación a CSV.

Dos cosas distintas, las dos en forma de tabla:

1. La matriz de SOLUCIONES que devuelve medidas.explorar(): una fila por
   combinación de medidas, con su riesgo, su costo y su ahorro del Anexo D.
   Es la tabla de resultados del artículo.

2. Un BARRIDO de un parámetro continuo (N_G, las dimensiones, la longitud de
   la línea...): una fila por valor, con el riesgo que da. Es la curva de
   sensibilidad.

Nada de esto agrega física nueva: solo recorre el cálculo que ya está probado
y lo escribe en un archivo que se puede graficar o meter en el artículo.
"""
import copy
import csv
from dataclasses import dataclass

from calculate_risk.norma import riesgos

# Dónde vive el parámetro que se va a barrer
DESTINOS = ("N_G", "estructura", "linea", "zona")


@dataclass(frozen=True)
class Punto:
    """Un valor del parámetro barrido y el riesgo que produce."""
    valor: float
    riesgo: float
    R_T: float
    cumple: bool


def barrer(estructura, lineas, zonas, N_G, valores, destino="N_G", campo=None,
           tipo=1) -> list:
    """Varía un parámetro y devuelve el riesgo en cada valor.

    destino="N_G"          -> se barre la densidad de descargas (campo se ignora)
    destino="estructura"   -> campo es "L", "W", "H", "H_p", "C_D"...
    destino="linea"        -> campo es "L_L", "C_I", "C_E"...  (a todas las líneas)
    destino="zona"         -> campo es "n_z", "t_z", "r_f"...  (a todas las zonas)

    El caso original no se modifica.
    """
    if destino not in DESTINOS:
        raise ValueError(f"destino debe ser uno de {DESTINOS}")
    if destino != "N_G" and not campo:
        raise ValueError(f"Con destino={destino!r} hay que decir qué campo barrer")

    puntos = []
    for valor in valores:
        e, l, z, ng = copy.deepcopy(estructura), copy.deepcopy(lineas), copy.deepcopy(zonas), N_G

        if destino == "N_G":
            ng = valor
        elif destino == "estructura":
            setattr(e, campo, valor)
        elif destino == "linea":
            for linea in l:
                setattr(linea, campo, valor)
        else:
            for zona in z:
                setattr(zona, campo, valor)

        r = riesgos.evaluar(e, l, z, ng, tipos=(tipo,))[tipo]
        puntos.append(Punto(valor=valor, riesgo=r["total"], R_T=r["R_T"],
                            cumple=r["cumple"]))
    return puntos


COLUMNAS_SOLUCIONES = ("medidas", "n_medidas", "riesgo", "R_T", "cumple",
                       "costo", "C_L", "C_RL", "C_PM", "S_M")


def exportar_soluciones(soluciones, ruta) -> str:
    """Escribe a CSV la matriz de soluciones de medidas.explorar()."""
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(COLUMNAS_SOLUCIONES)
        for s in soluciones:
            escritor.writerow([
                " + ".join(s.nombres),
                len(s.medidas),
                s.riesgo,
                s.R_T,
                int(s.cumple),
                s.costo,
                "" if s.C_L is None else s.C_L,
                "" if s.C_RL is None else s.C_RL,
                "" if s.C_PM is None else s.C_PM,
                "" if s.S_M is None else s.S_M,
            ])
    return str(ruta)


def exportar_barrido(puntos, ruta, nombre_parametro="parametro") -> str:
    """Escribe a CSV la curva de sensibilidad que devuelve barrer()."""
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow((nombre_parametro, "riesgo", "R_T", "cumple"))
        for p in puntos:
            escritor.writerow([p.valor, p.riesgo, p.R_T, int(p.cumple)])
    return str(ruta)