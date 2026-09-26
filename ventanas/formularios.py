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

from calculate_risk.norma import etiquetas, probabilidades, tablas
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona
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


class _PestanaPerdidas(ttk.Frame):
    """Las pérdidas de una zona para UN tipo de riesgo.

    Cada tipo tiene su propia tabla en el Anexo C, y por eso hay una pestaña
    por riesgo en vez de un solo juego de casillas. Lo que no aplica se deja
    en "no aplica" y vale 0: una zona puede no prestar servicio público, no
    tener patrimonio cultural y no tener sistemas vitales, y eso es una
    respuesta, no un olvido (numeral 4.3).
    """

    def __init__(self, padre, tipo: int):
        super().__init__(padre, padding=8)
        self.tipo = tipo
        d = por_defecto(Zona)
        self.campos = {}
        self.banderas = {}

        if tipo == 1:
            self.campos["L_T"] = campos.CampoNumero(
                self, "Pérdida por lesiones (L_T)", 0,
                valor=tablas.LT_L1, minimo=0, maximo=1, unidad="Tabla C.2")
            self.campos["L_F"] = campos.CampoTabla(
                self, "LF_L1", 1, etiqueta="Pérdida por daño físico (L_F)")
            self.campos["L_O"] = campos.CampoTabla(
                self, "LO_L1", 2, etiqueta="Pérdida por falla de sistemas (L_O)",
                opcional=True)
            self.campos["h_z"] = campos.CampoTabla(
                self, "HZ", 3, etiqueta="Daño especial (h_z)")

        elif tipo == 2:
            self.campos["L_F"] = campos.CampoTabla(
                self, "LF_L2", 0, etiqueta="Pérdida por daño físico (L_F)",
                opcional=True)
            self.campos["L_O"] = campos.CampoTabla(
                self, "LO_L2", 1, etiqueta="Pérdida por falla de sistemas (L_O)",
                opcional=True)

        elif tipo == 3:
            self.banderas["L_F"] = (
                campos.CampoSiNo(self, "Hay patrimonio cultural irremplazable", 0),
                tablas.LF_L3)
            self.campos["c_z"] = campos.CampoNumero(
                self, "Valor del patrimonio en la zona (c_z)", 1,
                valor=d["c_z"], minimo=0)

        elif tipo == 4:
            self.banderas["L_T"] = (
                campos.CampoSiNo(self, "Hay animales en la zona", 0),
                tablas.LT_L4)
            self.campos["L_F"] = campos.CampoTabla(
                self, "LF_L4", 1, etiqueta="Pérdida por daño físico (L_F)")
            self.campos["L_O"] = campos.CampoTabla(
                self, "LO_L4", 2, etiqueta="Pérdida por falla de sistemas (L_O)",
                opcional=True)
            self.campos["c_a"] = campos.CampoNumero(
                self, "Valor de los animales (c_a)", 3, valor=d["c_a"], minimo=0)
            self.campos["c_b"] = campos.CampoNumero(
                self, "Valor del edificio (c_b)", 4, valor=d["c_b"], minimo=0)
            self.campos["c_c"] = campos.CampoNumero(
                self, "Valor del contenido (c_c)", 5, valor=d["c_c"], minimo=0)
            self.campos["c_s"] = campos.CampoNumero(
                self, "Valor de los sistemas internos (c_s)", 6,
                valor=d["c_s"], minimo=0)
            self.campos["c_e"] = campos.CampoNumero(
                self, "Valor de los bienes en sitios peligrosos fuera (c_e)", 7,
                valor=d["c_e"], minimo=0)
            self.campos["L_FE"] = campos.CampoNumero(
                self, "Pérdida típica por daño físico fuera (L_FE)", 8,
                valor=d["L_FE"], minimo=0, maximo=1)
            # Nota "a" de la Tabla C.11: si R4 se compara contra el valor
            # representativo (1e-3) las razones c/c_t se reemplazan por 1.
            # Arranca en SÍ, al revés que la dataclass, porque es lo que hace
            # la pantalla: el Anexo D con valores reales se pide aparte.
            self.campos["razones_l4_unitarias"] = campos.CampoSiNo(
                self, "Comparar R4 contra el valor representativo (nota «a», Tabla C.11)",
                9, valor=True)
        else:
            raise ValueError("El tipo de riesgo debe ser 1, 2, 3 o 4")

    def leer(self) -> dict:
        valores = campos.recoger(self.campos)
        for nombre, (bandera, valor_si) in self.banderas.items():
            valores[nombre] = valor_si if bandera.valor() else 0
        return valores

    def poner(self, zona: Zona):
        for nombre, campo in self.campos.items():
            _poner_en(campo, getattr(zona, nombre))
        for nombre, (bandera, valor_si) in self.banderas.items():
            bandera.poner(getattr(zona, nombre) == valor_si)


class FormularioZona(ttk.Frame):
    """La zona completa: lo común arriba y una pestaña por riesgo abajo.

    zonas_por_tipo() devuelve CUATRO objetos Zona, uno por riesgo, porque el
    modelo guarda las pérdidas de un solo tipo por zona. Es la misma división
    que hace _zona(datos, tipo) en el adaptador, pero ahora con los datos que
    el usuario eligió en vez de con valores por defecto.
    """

    TITULOS = {1: "R1 Vidas humanas", 2: "R2 Servicio público",
               3: "R3 Patrimonio", 4: "R4 Económica"}

    def __init__(self, padre, zonas=None, titulo="Zona"):
        super().__init__(padre, padding=4)
        self.comun = FormularioZonaComun(self, titulo=titulo)
        self.comun.grid(row=0, column=0, sticky="ew", padx=4, pady=4)

        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        self.pestanas = {}
        for tipo in sorted(POR_TIPO):
            pestana = _PestanaPerdidas(self.cuaderno, tipo)
            self.cuaderno.add(pestana, text=self.TITULOS[tipo])
            self.pestanas[tipo] = pestana

        if zonas is not None:
            self.poner(zonas)

    @property
    def sistemas_internos(self):
        return self.comun.sistemas_internos

    @sistemas_internos.setter
    def sistemas_internos(self, valor):
        self.comun.sistemas_internos = list(valor)

    def zonas_por_tipo(self) -> dict:
        """{1: Zona, 2: Zona, 3: Zona, 4: Zona} con lo común repetido.

        Si falta algo, junta lo que falta de la parte común y de las cuatro
        pestañas en un solo aviso, diciendo de qué riesgo es cada cosa.
        """
        problemas = []
        try:
            comun = self.comun.leer()
        except campos.DatoFaltante as error:
            comun = None
            problemas.append(str(error))

        perdidas = {}
        for tipo, pestana in self.pestanas.items():
            try:
                perdidas[tipo] = pestana.leer()
            except campos.DatoFaltante as error:
                problemas.append(f"{self.TITULOS[tipo]}:\n{error}")

        if problemas:
            raise campos.DatoFaltante("\n".join(problemas))
        return {tipo: Zona(**comun, **perdidas[tipo]) for tipo in perdidas}

    def poner(self, zonas: dict):
        """Llena el formulario desde {tipo: Zona}; lo común sale de la primera."""
        primera = zonas[sorted(zonas)[0]]
        self.comun.poner(primera)
        for tipo, pestana in self.pestanas.items():
            if tipo in zonas:
                pestana.poner(zonas[tipo])


def _opciones_tension() -> list:
    """Las cinco tensiones que tabulan las Tablas B.8 y B.9."""
    return [(f"{u} kV", u) for u in probabilidades.tensiones_soportadas()]


def _opciones_de(tabla: str, llaves) -> list:
    """[(texto, llave)] para una lista que elige una fila, no un valor."""
    return [(etiquetas.texto(tabla, llave), llave) for llave in llaves]


def _blindaje_de(p_ld: float, u_w: float) -> str:
    """Qué fila de la Tabla B.8 da ese P_LD con esa U_W (para abrir un caso)."""
    for blindaje in probabilidades.BLINDAJES:
        if probabilidades.p_ld(blindaje, u_w) == p_ld:
            return blindaje
    raise campos.DatoFaltante(
        f"P_LD = {p_ld} no está en la Tabla B.8 para U_W = {u_w} kV")


def _tipo_linea_de(p_li: float, u_w: float) -> str:
    """Qué fila de la Tabla B.9 da ese P_LI con esa U_W."""
    for tipo in probabilidades.TIPOS_DE_LINEA:
        if probabilidades.p_li(tipo, u_w) == p_li:
            return tipo
    raise campos.DatoFaltante(
        f"P_LI = {p_li} no está en la Tabla B.9 para U_W = {u_w} kV")


class _FormularioAdyacente(ttk.LabelFrame):
    """La estructura del extremo lejano de la línea (ec. A.5).

    Solo se le piden las dimensiones: de esa estructura, el cálculo de N_DJ
    únicamente usa L, W, H y H_p (más C_DJ, que va en la línea). Todo lo
    demás de la Estructura —personas, valor, banderas— es de la estructura
    que se está evaluando, no de la vecina.
    """

    def __init__(self, padre):
        super().__init__(padre, text="Estructura del extremo lejano", padding=8)
        d = por_defecto(Estructura)
        self.campos = {
            "L": campos.CampoNumero(self, "Longitud (L)", 0, unidad="m", positivo=True),
            "W": campos.CampoNumero(self, "Ancho (W)", 1, unidad="m", positivo=True),
            "H": campos.CampoNumero(self, "Altura (H)", 2, unidad="m", positivo=True),
            "H_p": campos.CampoNumero(self, "Altura del saliente (H_p)", 3,
                                      valor=d["H_p"], unidad="m", minimo=0),
        }

    def leer(self) -> Estructura:
        return Estructura(**campos.recoger(self.campos))

    def poner(self, estructura: Estructura):
        for nombre, campo in self.campos.items():
            campo.poner(getattr(estructura, nombre))


class FormularioLinea(ttk.Frame):
    """Los trece campos de modelo.Linea.

    Aquí caen dos limitaciones de la pantalla vieja:

    H16 - la longitud L_L es una casilla libre en metros. El adaptador la
          tenía clavada en 1000 m, y como A_L y A_I son proporcionales a
          L_L, eso decidía el 96 % del riesgo de la casa rural.
    H18 - la línea puede llegar a otra estructura, que es lo que mete N_DJ
          en R_U, R_V y R_W por la ec. (A.5). La pantalla vieja no lo
          preguntaba, así que N_DJ era siempre 0.

    P_LD y P_LI no se escriben: se buscan en las Tablas B.8 y B.9 con el
    blindaje o el tipo de línea y la tensión soportada U_W.
    """

    def __init__(self, padre, linea=None, titulo="Línea"):
        super().__init__(padre, padding=4)
        d = por_defecto(Linea)

        self.marco = ttk.LabelFrame(self, text=titulo, padding=8)
        self.marco.grid(row=0, column=0, sticky="ew")
        m = self.marco

        self.campos = {
            "nombre": campos.CampoTexto(m, "Nombre de la línea", 0),
            "L_L": campos.CampoNumero(m, "Longitud de la sección (L_L)", 1,
                                      valor=d["L_L"], unidad="m", positivo=True),
            "C_I": campos.CampoTabla(m, "CI", 2, etiqueta="Instalación (C_I)"),
            "C_T": campos.CampoTabla(m, "CT", 3, etiqueta="Tipo de línea (C_T)"),
            "C_E": campos.CampoTabla(m, "CE", 4, etiqueta="Entorno (C_E)"),
            "U_W": campos.CampoLista(m, "Tensión soportada del equipo (U_W)", 5,
                                     _opciones_tension()),
            "P_EB": campos.CampoTabla(m, "PEB", 6,
                                      etiqueta="Equipotencialización con DPS (P_EB)"),
        }

        # Los que dan más de un valor o salen de una tabla de doble entrada
        self.derivados = {
            "cld_cli": campos.CampoTabla(m, "CLD_CLI", 7,
                                         etiqueta="Blindaje y puesta a tierra (C_LD y C_LI)"),
            "blindaje": campos.CampoLista(
                m, "Conexión del blindaje (P_LD)", 8,
                _opciones_de("PLD", probabilidades.BLINDAJES)),
            "tipo_linea": campos.CampoLista(
                m, "Servicio que transporta (P_LI)", 9,
                _opciones_de("PLI", probabilidades.TIPOS_DE_LINEA)),
        }

        # H18: la estructura del extremo lejano
        self.hay_adyacente = campos.CampoSiNo(
            m, "La línea llega a otra estructura (N_DJ)", 10)
        self.C_DJ = campos.CampoTabla(m, "CD", 11,
                                      etiqueta="Localización de esa estructura (C_DJ)")
        self.adyacente = _FormularioAdyacente(self)
        self.adyacente.grid(row=1, column=0, sticky="ew", pady=4)

        if linea is not None:
            self.poner(linea)

    def leer(self) -> Linea:
        """Devuelve la Línea, o avisa con TODO lo que falte."""
        todos = dict(self.campos)
        todos.update(self.derivados)
        problemas = []
        try:
            valores = campos.recoger(todos)
        except campos.DatoFaltante as error:
            valores = None
            problemas.append(str(error))

        adyacente = None
        c_dj = None
        if self.hay_adyacente.valor():
            # Las medidas de la estructura vecina y su C_DJ se piden juntos,
            # para que falten juntos y no de a uno.
            grupo = dict(self.adyacente.campos)
            grupo["C_DJ"] = self.C_DJ
            try:
                medidas = campos.recoger(grupo)
                c_dj = medidas.pop("C_DJ")
                adyacente = Estructura(**medidas)
            except campos.DatoFaltante as error:
                problemas.append(str(error))

        if problemas:
            raise campos.DatoFaltante("\n".join(problemas))

        par = valores.pop("cld_cli")
        valores["C_LD"], valores["C_LI"] = par["CLD"], par["CLI"]
        u_w = valores["U_W"]
        valores["P_LD"] = probabilidades.p_ld(valores.pop("blindaje"), u_w)
        valores["P_LI"] = probabilidades.p_li(valores.pop("tipo_linea"), u_w)
        valores["adyacente"] = adyacente
        if adyacente is not None:
            valores["C_DJ"] = c_dj
        return Linea(**valores)

    def poner(self, linea: Linea):
        """Llena el formulario desde una línea guardada.

        P_LD y P_LI vienen como número, así que hay que averiguar de qué fila
        de la tabla salieron. Con la U_W de la línea la búsqueda es directa;
        si varias filas dan el mismo número (P_LD = 1 sale en dos) queda la
        primera, y el cálculo es idéntico.
        """
        for nombre, campo in self.campos.items():
            _poner_en(campo, getattr(linea, nombre))
        self.derivados["cld_cli"].poner_valor({"CLD": linea.C_LD, "CLI": linea.C_LI})
        self.derivados["blindaje"].poner(_blindaje_de(linea.P_LD, linea.U_W))
        self.derivados["tipo_linea"].poner(_tipo_linea_de(linea.P_LI, linea.U_W))

        self.hay_adyacente.poner(linea.adyacente is not None)
        if linea.adyacente is not None:
            self.adyacente.poner(linea.adyacente)
            self.C_DJ.poner_valor(linea.C_DJ)