from ventanas.modo import Modo
from ventanas.principal_norma import PrincipalNorma

import tkinter as tk

class App(tk.Frame):
    """Clase principal que crea los diferentes paneles y los "conecta" entre
    sí de modo que la función .siguiente() de uno llame al .mostrar() del
    siguiente"""
    def __init__(self, master):
        super().__init__()

        # Creacion de los paneles


        modo = Modo(master,
                    titulo="Modo",
                    ancho=740,
                    alto=452)

        principal_norma = PrincipalNorma(master)

        # Conexión entre sí de la secuencia

        principal_norma.anterior_modo = modo.mostrar
        modo.siguientenorma = principal_norma.mostrar

        # Configuración de los  frames
        for frame in (modo, principal_norma):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Empezamos por el de modo

        modo.mostrar()
        