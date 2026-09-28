"""
Paso 58c: de dónde sale N_G, en la pantalla.

Reemplaza el botón «Calcular con lat/lon» y su diálogo (Paso 51e). Dos modos:

  coordenadas  se escriben latitud y longitud; N_G sale de la climatología de la
               NASA y la casilla de N_G no se escribe a mano. El resultado se
               recalcula cada vez que se pide el caso, así que N_G nunca puede
               quedar desfasado de las coordenadas.
  declarado    N_G lo da el diseñador (red local, mapa oficial, la propia norma)
               y LA FUENTE ES OBLIGATORIA.

Dos avisos que la pantalla vieja no tenía: fuera de ±38° de latitud el sensor no
observa, y el programa lo dice y pasa solo al modo declarado; y una celda en cero
no se calcula en silencio, porque daría un riesgo cero sin decir nada.

netCDF4 se importa DENTRO de los métodos a propósito: quien no tenga la librería
tiene que poder abrir el programa y declarar N_G con su fuente.
"""
import tkinter as tk
from tkinter import ttk

from calculate_risk.norma.modelo import Emplazamiento
from ventanas import campos

COORDENADAS = "coordenadas"
DECLARADO = "declarado"

SIN_LIBRERIA = ("Para calcular N_G desde la latitud y la longitud hace falta "
                "la librería netCDF4 y el archivo de la NASA. Se puede "
                "declarar N_G con su fuente.")
CELDA_EN_CERO = ("La celda de la NASA más cercana no registra descargas. Un cero puede ser "
                 "real o falta de dato (mar, desierto), y el programa no calcula un riesgo "
                 "cero en silencio: declara N_G con su fuente.")


def _coma(numero: float, decimales: int) -> str:
    return f"{numero:.{decimales}f}".replace(".", ",")


def _para_la_casilla(n_g: float) -> str:
    """N_G con cuatro cifras significativas, para no enseñar 2,6429927434921265."""
    return f"{n_g:.4g}".replace(".", ",")


def texto_de_ficha(ficha) -> str:
    """La ficha del dato en una frase, con coma decimal."""
    return (f"Celda de la NASA en ({_coma(ficha.celda_lat, 2)}°; {_coma(ficha.celda_lon, 2)}°), "
            f"a {_coma(ficha.distancia_km, 1)} km del sitio. "
            f"{_coma(ficha.destellos_totales, 2)} destellos totales/km² año × "
            f"{_coma(ficha.fraccion_nube_tierra, 3)} nube-tierra "
            f"(relación intranube:tierra ≈ {_coma(ficha.relacion_ic_cg, 1)}). "
            f"Observada {_coma(ficha.horas_observadas, 0)} h.")


class PanelEmplazamiento(ttk.LabelFrame):
    """Modo, coordenadas o fuente, y el N_G resultante."""

    def __init__(self, padre, al_cambiar=None):
        super().__init__(padre, text="Densidad de descargas a tierra (N_G)", padding=6)
        self.al_cambiar = al_cambiar or (lambda: None)
        self.modo = tk.StringVar(value=COORDENADAS)

        opciones = ttk.Frame(self)
        opciones.grid(row=0, column=0, sticky="w")
        self.radio_coordenadas = ttk.Radiobutton(
            opciones, text="Por coordenadas (NASA LIS)", value=COORDENADAS,
            variable=self.modo, command=self._cambio_de_modo)
        self.radio_coordenadas.grid(row=0, column=0, padx=(0, 12))
        self.radio_declarado = ttk.Radiobutton(
            opciones, text="Declarado, con su fuente", value=DECLARADO,
            variable=self.modo, command=self._cambio_de_modo)
        self.radio_declarado.grid(row=0, column=1)

        por_defecto = Emplazamiento()
        self.marco_coordenadas = ttk.Frame(self)
        self.lat = campos.CampoNumero(self.marco_coordenadas, "Latitud", 0,
                                      unidad="°", minimo=-90, maximo=90)
        self.lon = campos.CampoNumero(self.marco_coordenadas, "Longitud", 1,
                                      unidad="°", minimo=-180, maximo=180)
        self.fraccion = campos.CampoNumero(
            self.marco_coordenadas, "Fracción nube-tierra", 2,
            valor=por_defecto.fraccion_nube_tierra, positivo=True, maximo=1)
        self.boton_buscar = ttk.Button(self.marco_coordenadas, text="Buscar",
                                       command=self.buscar)
        self.boton_buscar.grid(row=0, column=3, padx=8)

        self.marco_declarado = ttk.Frame(self)
        self.fuente = campos.CampoTexto(self.marco_declarado, "Fuente de N_G", 0, ancho=50)

        marco_ng = ttk.Frame(self)
        marco_ng.grid(row=2, column=0, sticky="w")
        self.N_G = campos.CampoNumero(marco_ng, "N_G", 0, unidad="rayos/km² año",
                                      positivo=True)

        self.aviso = ttk.Label(self, wraplength=560, justify="left")
        self.aviso.grid(row=3, column=0, sticky="w", pady=(4, 0))
        self._mostrar_modo()

    # -- modo --------------------------------------------------------------

    def _mostrar_modo(self):
        if self.modo.get() == COORDENADAS:
            self.marco_declarado.grid_remove()
            self.marco_coordenadas.grid(row=1, column=0, sticky="w")
            self.N_G.entrada.configure(state="readonly")
        else:
            self.marco_coordenadas.grid_remove()
            self.marco_declarado.grid(row=1, column=0, sticky="w")
            self.N_G.entrada.configure(state="normal")

    def _cambio_de_modo(self):
        self._mostrar_modo()
        self.decir("")
        self.al_cambiar()

    def poner_modo(self, modo: str):
        self.modo.set(modo)
        self._mostrar_modo()

    def decir(self, mensaje: str):
        self.aviso.configure(text=mensaje)

    # -- coordenadas -------------------------------------------------------

    def _ficha(self):
        """(ficha, None) o (None, mensaje). Nunca lanza: lo llama un botón."""
        problemas = []
        valores = {}
        for nombre, campo in (("lat", self.lat), ("lon", self.lon),
                              ("fraccion", self.fraccion)):
            try:
                valores[nombre] = campo.valor()
            except campos.DatoFaltante as error:
                problemas.append(str(error))
        if problemas:
            return None, "\n".join(problemas)

        try:
            from calculate_risk.norma import densidad
        except ImportError:
            return None, SIN_LIBRERIA
        try:
            return densidad.ficha_desde_lat_lon(
                valores["lat"], valores["lon"], valores["fraccion"]), None
        except densidad.FueraDeCobertura as error:
            self.N_G.poner("")
            self.poner_modo(DECLARADO)
            self.al_cambiar()
            return None, f"{error} Se pasó al modo declarado."
        except OSError:
            return None, SIN_LIBRERIA
        except ValueError as error:
            return None, str(error)

    def buscar(self):
        """Busca N_G en la climatología y lo deja en la casilla. None si algo falla."""
        ficha, problema = self._ficha()
        if ficha is None:
            self.decir(problema)
            return None
        self.N_G.poner("" if ficha.celda_en_cero else _para_la_casilla(ficha.N_G))
        self.decir(CELDA_EN_CERO if ficha.celda_en_cero else texto_de_ficha(ficha))
        self.al_cambiar()
        return None if ficha.celda_en_cero else ficha

    # -- lectura -----------------------------------------------------------

    def resolver(self):
        """(N_G, Emplazamiento) listos para el motor, o DatoFaltante con el motivo."""
        if self.modo.get() == DECLARADO:
            problemas = []
            valores = {}
            for nombre, campo in (("N_G", self.N_G), ("fuente", self.fuente)):
                try:
                    valores[nombre] = campo.valor()
                except campos.DatoFaltante as error:
                    problemas.append(str(error))
            if problemas:
                raise campos.DatoFaltante("\n".join(problemas))
            return valores["N_G"], Emplazamiento(modo=DECLARADO, fuente=valores["fuente"])

        ficha, problema = self._ficha()
        if ficha is None:
            self.decir(problema)
            raise campos.DatoFaltante(problema)
        if ficha.celda_en_cero:
            self.N_G.poner("")
            self.decir(CELDA_EN_CERO)
            raise campos.DatoFaltante(CELDA_EN_CERO)
        self.N_G.poner(_para_la_casilla(ficha.N_G))
        self.decir(texto_de_ficha(ficha))
        return ficha.N_G, Emplazamiento(
            modo=COORDENADAS, lat=ficha.lat, lon=ficha.lon,
            fraccion_nube_tierra=ficha.fraccion_nube_tierra)

    # -- escritura ---------------------------------------------------------

    def poner(self, N_G, emplazamiento=None):
        """Abre un caso. Sin emplazamiento (archivo viejo) queda declarado y SIN fuente:
        el programa la pide antes de calcular, en vez de inventarla."""
        self.limpiar()
        if emplazamiento is None or emplazamiento.modo == DECLARADO:
            self.poner_modo(DECLARADO)
            self.N_G.poner(N_G)
            if emplazamiento is not None:
                self.fuente.poner(emplazamiento.fuente)
            else:
                self.decir("Este caso no dice de dónde sale N_G: escribe su fuente.")
            return
        self.lat.poner(emplazamiento.lat)
        self.lon.poner(emplazamiento.lon)
        self.fraccion.poner(emplazamiento.fraccion_nube_tierra)
        self.N_G.poner(N_G)
        self.poner_modo(COORDENADAS)
        try:
            from calculate_risk.norma import densidad
            if not densidad.concuerda(emplazamiento, N_G):
                self.decir("El N_G guardado no coincide con las coordenadas: al calcular "
                           "se usa el que dan las coordenadas.")
        except (ImportError, OSError):
            self.decir(SIN_LIBRERIA)

    def limpiar(self):
        """Como recién abierto el programa: por coordenadas y todo en blanco."""
        self.poner_modo(COORDENADAS)
        self.lat.poner("")
        self.lon.poner("")
        self.fraccion.poner(Emplazamiento().fraccion_nube_tierra)
        self.fuente.poner("")
        self.N_G.poner("")
        self.decir("")
