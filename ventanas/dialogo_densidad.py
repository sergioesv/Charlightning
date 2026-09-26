"""
Paso 51e: N_G a partir de latitud y longitud, en la pantalla nueva.

La pantalla vieja tenía el botón «Calcular ddt», que abría la ventana de
calculo_ddt_plot/. Esa ventana arrastraba dos defectos: tomaba lat = 0 o
lon = 0 como casilla vacía (`if float(lat):`), así que el ecuador y el
meridiano de Greenwich no se podían calcular, y exigía punto decimal.

Aquí el cálculo lo hace norma/densidad.py, que ya arregla el cero (Paso 35),
y las casillas son CampoNumero, que acepta coma. El valor que sale es el
mismo: la climatología LIS/OTD de la NASA por el factor 0,227.

netCDF4 se importa DENTRO del método a propósito: quien no tenga la librería
instalada tiene que poder abrir el programa y escribir N_G a mano.
"""
import tkinter as tk
from tkinter import ttk

from ventanas import campos

# Medellín, el ejemplo que ya traía escrito la ventana vieja.
LAT_INICIAL = 6.251
LON_INICIAL = -75.563

SIN_LIBRERIA = ("Para calcular N_G desde la latitud y la longitud hace falta "
                "la librería netCDF4 y el archivo de la NASA. Se puede "
                "escribir N_G a mano.")


class DialogoDensidad(tk.Toplevel):
    """Pide latitud y longitud y entrega N_G por el callback `devolver`."""

    def __init__(self, padre, devolver=None):
        super().__init__(padre)
        self.title("N_G desde latitud y longitud")
        self.devolver = devolver
        self.n_g = None

        marco = ttk.Frame(self, padding=12)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, wraplength=430, justify="left", text=(
            "Climatología LIS/OTD de la NASA (1998-2013). Devuelve la densidad "
            "de descargas a tierra del punto de grilla más cercano.")
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        self.campos = {
            "lat": campos.CampoNumero(marco, "Latitud", 1, valor=LAT_INICIAL,
                                      unidad="°", minimo=-90, maximo=90),
            "lon": campos.CampoNumero(marco, "Longitud", 2, valor=LON_INICIAL,
                                      unidad="°", minimo=-180, maximo=180),
        }

        self.aviso = ttk.Label(marco, wraplength=430, justify="left")
        self.aviso.grid(row=3, column=0, columnspan=3, sticky="w", pady=8)

        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, columnspan=3, sticky="e")
        self.boton_calcular = ttk.Button(botones, text="Calcular",
                                         command=self.calcular)
        self.boton_calcular.grid(row=0, column=0, padx=4)
        self.boton_usar = ttk.Button(botones, text="Usar este valor",
                                     command=self.usar, state="disabled")
        self.boton_usar.grid(row=0, column=1, padx=4)
        ttk.Button(botones, text="Cancelar", command=self.destroy).grid(
            row=0, column=2, padx=4)

    def calcular(self):
        """Busca N_G en la climatología. Devuelve None si algo falta."""
        try:
            lat = self.campos["lat"].valor()
            lon = self.campos["lon"].valor()
        except campos.DatoFaltante as error:
            return self._decir(str(error))

        try:
            from calculate_risk.norma import densidad
        except ImportError:
            return self._decir(SIN_LIBRERIA)
        try:
            self.n_g = densidad.n_g_desde_lat_lon(lat, lon)
        except OSError:
            return self._decir(SIN_LIBRERIA)

        self._decir(f"N_G = {self.n_g:.4g} rayos/km² año".replace(".", ","))
        self.boton_usar.configure(state="normal")
        return self.n_g

    def usar(self):
        """Entrega el valor a quien abrió el diálogo y cierra."""
        if self.n_g is None:
            return None
        if self.devolver is not None:
            self.devolver(self.n_g)
        self.destroy()
        return self.n_g

    def _decir(self, mensaje):
        self.aviso.configure(text=mensaje)
        return None