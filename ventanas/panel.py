import tkinter as tk
from variables.globales import papo

class Panel(tk.Frame):
    """Clase genérica para mostrar un Frame con un cierto título y
    tamaño dados, centrado en la pantalla"""

    def __init__(self, master, titulo="Sin título", ancho=360, alto=180):
        super().__init__()
        self.master: tk.Tk = master
        
        self.siguiente = (
            lambda: None
        )  # Valor por defecto no útil. El programa principal debe asignar otro
        self.titulo = titulo
        self.ancho = ancho
        self.alto = alto
        self.x = (self.master.winfo_screenwidth() - self.ancho) // 2
        self.y = (self.master.winfo_screenheight() - self.alto) // 2


    def mostrar(self):
        self.master.title(self.titulo)
        self.master.geometry(
            "{}x{}+{}+{}".format(self.ancho, self.alto, self.x, self.y)
        )
        self.lift()
        

        
