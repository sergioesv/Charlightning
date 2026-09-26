"""
La idea de fondo es que el formulario pregunte EXACTAMENTE los campos de la
dataclass, ni uno más ni uno menos. Por eso leer() termina en

    Estructura(**campos.recoger(self.campos))

y por eso hay una prueba que compara los nombres del formulario con los
campos de la dataclass: si alguien le agrega un campo al modelo, la prueba
falla hasta que la pantalla también lo pregunte. Ese es justamente el hueco
por el que se colaron las limitaciones H16-H19, que existen porque el
adaptador rellena con valores por defecto lo que la pantalla no pregunta.

Los valores iniciales salen de las propias dataclasses, no se copian aquí.
"""
from dataclasses import fields
from tkinter import ttk

from calculate_risk.norma.modelo import Estructura
from ventanas import campos


def por_defecto(clase) -> dict:
    """Los valores por defecto de la dataclass, para no copiarlos a mano."""
    return {campo.name: campo.default for campo in fields(clase)}


class FormularioEstructura(ttk.LabelFrame):
    """Los nueve campos de modelo.Estructura.

    L, W y H no traen valor inicial a propósito: son los únicos que la
    dataclass exige, y dejarlos en blanco obliga a escribirlos en vez de
    calcular con un número que el usuario nunca vio.
    """

    def __init__(self, padre, estructura=None, titulo="Estructura"):
        super().__init__(padre, text=titulo, padding=8)
        d = por_defecto(Estructura)

        self.campos = {
            "L": campos.CampoNumero(self, "Longitud (L)", 0, unidad="m", positivo=True),
            "W": campos.CampoNumero(self, "Ancho (W)", 1, unidad="m", positivo=True),
            "H": campos.CampoNumero(self, "Altura (H)", 2, unidad="m", positivo=True),
            "H_p": campos.CampoNumero(self, "Altura del saliente del techo (H_p)", 3,
                                      valor=d["H_p"], unidad="m", minimo=0),
            "C_D": campos.CampoTabla(self, "CD", 4, etiqueta="Localización (C_D)"),
            "n_t": campos.CampoNumero(self, "Personas en la estructura (n_t)", 5,
                                      valor=d["n_t"], minimo=0),
            "c_t": campos.CampoNumero(self, "Valor total de la estructura (c_t)", 6,
                                      valor=d["c_t"], minimo=0, unidad="para R4"),
            "riesgo_explosion_o_vital": campos.CampoSiNo(
                self, "Riesgo de explosión o sistemas vitales", 7,
                valor=d["riesgo_explosion_o_vital"]),
            "hay_animales": campos.CampoSiNo(self, "Hay animales", 8,
                                             valor=d["hay_animales"]),
        }
        if estructura is not None:
            self.poner(estructura)

    def leer(self) -> Estructura:
        """Devuelve la Estructura, o avisa con TODO lo que falte."""
        return Estructura(**campos.recoger(self.campos))

    def poner(self, estructura: Estructura):
        """Llena el formulario con una estructura ya armada (caso guardado)."""
        for nombre, campo in self.campos.items():
            valor = getattr(estructura, nombre)
            if isinstance(campo, campos.CampoTabla):
                campo.poner_valor(valor)
            else:
                campo.poner(valor)