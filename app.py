from ventanas.modo import Modo
from ventanas.principal_guiado import Principal_guiado


import tkinter as tk
from tkinter import ttk

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

        principal_guiado = Principal_guiado(master,
                                            titulo="principal guiadooooo",
                                            ancho=1366,
                                            alto=768)

        # Conexión entre sí de la secuencia
        
        principal_guiado.anterior_modo = modo.mostrar
        modo.siguienteguiado = principal_guiado.mostrar
        
        # Configuración de los  frames
        for frame in (modo, principal_guiado):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Empezamos por el de modo

        modo.mostrar()
        