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

from calculate_risk.norma import probabilidades
from calculate_risk.norma.modelo import Estructura, SistemaInterno, Zona
from ventanas import campos


# Reparto de los campos de Zona. Lo común se pregunta una vez; las pérdidas
# cambian según el riesgo, porque el modelo guarda una zona por tipo (es lo
# que hace _zona(datos, tipo) del adaptador). La pantalla pregunta los cuatro
# juegos y arma cuatro zonas.
COMUNES = (
    "nombre", "P_TA", "P_TU", "P_B", "K_S1", "K_S2",
    "r_t", "r_p", "r_f", "n_z", "t_z",
    "sistemas_internos", "exterior_sin_personas",
)

POR_TIPO = {
    1: ("L_T", "L_F", "L_O", "h_z"),
    2: ("L_F", "L_O"),
    3: ("L_F", "c_z"),
    4: ("L_T", "L_F", "L_O",
        "c_a", "c_b", "c_c", "c_s", "c_e", "L_FE", "razones_l4_unitarias"),
}


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
            _poner_en(campo, getattr(estructura, nombre))


def _poner_en(campo, valor):
    """Pone un valor en el campo que sea, sin que el llamador sepa cuál es."""
    if isinstance(campo, campos.CampoTabla):
        campo.poner_valor(valor)
    else:
        campo.poner(valor)

class FormularioSistemaInterno(ttk.LabelFrame):
    """Los cinco campos de modelo.SistemaInterno.

    Aquí cae H17: P_DPS sale de la Tabla B.3 por su cuenta, no deducido del
    nivel del SPCR como hace la pantalla vieja. Se puede poner un DPS de
    NPR I en una estructura con SPCR de nivel IV, que es lo que la norma
    permite y la pantalla vieja no deja expresar.
    """

    def __init__(self, padre, sistema=None, titulo="Sistema interno"):
        super().__init__(padre, text=titulo, padding=8)
        d = por_defecto(SistemaInterno)

        self.campos = {
            "nombre": campos.CampoTexto(self, "Nombre", 0),
            "linea": campos.CampoTexto(self, "Lo alimenta la línea", 1,
                                       valor=d["linea"], obligatorio=False),
            "K_S3": campos.CampoTabla(self, "KS3", 2, etiqueta="Cableado interno (K_S3)"),
            "U_W": campos.CampoNumero(self, "Tensión soportada (U_W)", 3,
                                      valor=d["U_W"], unidad="kV", positivo=True),
            "P_DPS": campos.CampoTabla(self, "PDPS", 4, etiqueta="DPS coordinado (P_DPS)"),
        }
        if sistema is not None:
            self.poner(sistema)

    def leer(self) -> SistemaInterno:
        return SistemaInterno(**campos.recoger(self.campos))

    def poner(self, sistema: SistemaInterno):
        for nombre, campo in self.campos.items():
            _poner_en(campo, getattr(sistema, nombre))


class FormularioZonaComun(ttk.LabelFrame):
    """Lo que una zona tiene en común para los cuatro riesgos.

    K_S1 y K_S2 no se eligen de una lista: son una fórmula, K_S = 0,12 x w_m
    (ec. B.5 y B.6), así que se pregunta el ancho de la malla del
    apantallamiento. Sin apantallamiento valen 1, que es el valor por defecto
    de la dataclass. La pantalla vieja ofrecía tres valores fijos (1; 0,2;
    10^-4) que no salen de ninguna tabla.

    Los sistemas internos no se editan aquí: los pone y los lee el editor del
    caso, que es el que sabe cuántos hay.
    """

    def __init__(self, padre, titulo="Zona"):
        super().__init__(padre, text=titulo, padding=8)
        d = por_defecto(Zona)
        self.sistemas_internos = []

        self.campos = {
            "nombre": campos.CampoTexto(self, "Nombre de la zona", 0),
            "P_TA": campos.CampoTabla(self, "PTA", 1,
                                      etiqueta="Tensiones de paso y contacto (P_TA)"),
            "P_B": campos.CampoTabla(self, "PB", 2,
                                     etiqueta="Protección contra daño físico (P_B)"),
            "P_TU": campos.CampoTabla(self, "PTU", 3,
                                      etiqueta="Tensiones de contacto por línea (P_TU)"),
            "r_t": campos.CampoTabla(self, "N_SUPERFICIE", 4,
                                     etiqueta="Superficie del piso (r_t)"),
            "r_p": campos.CampoTabla(self, "RP", 5,
                                     etiqueta="Medidas contra incendio (r_p)"),
            "r_f": campos.CampoTabla(self, "RF", 6,
                                     etiqueta="Riesgo de incendio (r_f)"),
            "n_z": campos.CampoNumero(self, "Personas o usuarios en la zona (n_z)", 7,
                                      valor=d["n_z"], minimo=0),
            "t_z": campos.CampoNumero(self, "Horas al año de presencia (t_z)", 8,
                                      valor=d["t_z"], minimo=0, maximo=8760, unidad="h"),
            "exterior_sin_personas": campos.CampoSiNo(
                self, "Zona exterior sin personas (anula R_A y R_U)", 9,
                valor=d["exterior_sin_personas"]),
        }

        # K_S1 y K_S2 por el ancho de la malla, ec. (B.5) y (B.6)
        self.blindaje = campos.CampoSiNo(self, "Hay apantallamiento espacial", 10)
        self.w_m1 = campos.CampoNumero(self, "Ancho de la malla exterior (w_m1)", 11,
                                       unidad="m", positivo=True)
        self.w_m2 = campos.CampoNumero(self, "Ancho de la malla interior (w_m2)", 12,
                                       unidad="m", positivo=True)

    def leer(self) -> dict:
        """Los campos comunes, ya con K_S1 y K_S2 calculados."""
        valores = campos.recoger(self.campos)
        valores["sistemas_internos"] = list(self.sistemas_internos)
        if self.blindaje.valor():
            valores["K_S1"] = probabilidades.k_s1(self.w_m1.valor())
            valores["K_S2"] = probabilidades.k_s2(self.w_m2.valor())
        else:
            d = por_defecto(Zona)
            valores["K_S1"] = d["K_S1"]
            valores["K_S2"] = d["K_S2"]
        return valores

    def poner(self, zona: Zona):
        for nombre, campo in self.campos.items():
            _poner_en(campo, getattr(zona, nombre))
        self.sistemas_internos = list(zona.sistemas_internos)

        d = por_defecto(Zona)
        hay = zona.K_S1 != d["K_S1"] or zona.K_S2 != d["K_S2"]
        self.blindaje.poner(hay)
        if hay:
            self.w_m1.poner(probabilidades.w_m_desde_k_s(zona.K_S1))
            self.w_m2.poner(probabilidades.w_m_desde_k_s(zona.K_S2))