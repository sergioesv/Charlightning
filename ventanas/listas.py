"""
Es la pieza que le faltaba a la pantalla para poder tener VARIOS de algo:
varios sistemas internos en una zona, varias zonas en la estructura, varias
líneas. Sin esto, la pantalla vieja solo podía con uno de cada, y de ahí
viene la limitación H19.

A la izquierda los nombres, a la derecha el formulario del seleccionado, y
dos botones. Cada elemento tiene su propio formulario, creado por la fábrica
que se le pasa; se muestran y se ocultan según lo que esté seleccionado.
"""
import tkinter as tk
from tkinter import ttk

from ventanas import campos


class ListaDeFormularios(ttk.LabelFrame):
    """Lista de elementos con su formulario.

    fabrica(padre) tiene que devolver un formulario con tres cosas:
    leer(), poner(objeto) y nombre(). Nada más.
    """

    def __init__(self, padre, fabrica, titulo="Elementos", singular="elemento",
                 minimo=0, alto=8):
        super().__init__(padre, text=titulo, padding=8)
        self.fabrica = fabrica
        self.singular = singular
        self.minimo = minimo
        self.formularios = []

        self.lista = tk.Listbox(self, height=alto, exportselection=False, width=26)
        self.lista.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 8))
        self.lista.bind("<<ListboxSelect>>", lambda _evento: self.mostrar_seleccionado())

        self.zona_formulario = ttk.Frame(self)
        self.zona_formulario.grid(row=0, column=1, sticky="nsew")

        botones = ttk.Frame(self)
        botones.grid(row=1, column=1, sticky="w", pady=(6, 0))
        self.boton_anadir = ttk.Button(botones, text=f"Añadir {singular}",
                                       command=self.anadir)
        self.boton_anadir.grid(row=0, column=0, padx=(0, 6))
        self.boton_quitar = ttk.Button(botones, text=f"Quitar {singular}",
                                       command=self.quitar)
        self.boton_quitar.grid(row=0, column=1)

    # -- contenido ---------------------------------------------------------

    def anadir(self, objeto=None):
        """Crea un elemento nuevo y lo deja seleccionado."""
        formulario = self.fabrica(self.zona_formulario)
        if objeto is not None:
            formulario.poner(objeto)
        self.formularios.append(formulario)
        self._refrescar_nombres()
        self.lista.selection_clear(0, "end")
        self.lista.selection_set(len(self.formularios) - 1)
        self.mostrar_seleccionado()
        return formulario

    def quitar(self):
        """Quita el elemento seleccionado, si queda por encima del mínimo."""
        indice = self.seleccionado()
        if indice is None:
            return
        if len(self.formularios) <= self.minimo:
            raise campos.DatoFaltante(
                f"Tiene que quedar al menos {self.minimo} {self.singular}")
        self.formularios.pop(indice).destroy()
        self._refrescar_nombres()
        if self.formularios:
            self.lista.selection_set(min(indice, len(self.formularios) - 1))
        self.mostrar_seleccionado()

    def leer(self, *argumentos, **nombrados) -> list:
        """Lee todos los elementos; si falta algo, junta todo en un aviso.

        Lo que se le pase se reenvía tal cual al leer() de cada formulario:
        así el editor puede pedir "solo R1" y la lista no necesita saber qué
        significa eso.
        """
        objetos = []
        problemas = []
        for numero, formulario in enumerate(self.formularios, start=1):
            try:
                objetos.append(formulario.leer(*argumentos, **nombrados))
            except campos.DatoFaltante as error:
                problemas.append(f"{self.singular.capitalize()} {numero}:\n{error}")
        if problemas:
            raise campos.DatoFaltante("\n".join(problemas))
        if len(objetos) < self.minimo:
            raise campos.DatoFaltante(
                f"Hace falta al menos {self.minimo} {self.singular}")
        return objetos

    def poner(self, objetos):
        """Deja la lista con exactamente estos elementos."""
        for formulario in self.formularios:
            formulario.destroy()
        self.formularios = []
        for objeto in objetos:
            self.anadir(objeto)
        self._refrescar_nombres()

    # -- selección ---------------------------------------------------------

    def seleccionado(self):
        elegidos = self.lista.curselection()
        return elegidos[0] if elegidos else None

    def mostrar_seleccionado(self):
        for formulario in self.formularios:
            formulario.grid_remove()
        indice = self.seleccionado()
        if indice is not None:
            self.formularios[indice].grid(row=0, column=0, sticky="nsew")

    def nombres(self) -> list:
        return [f.nombre() or f"({self.singular} sin nombre)"
                for f in self.formularios]

    def _refrescar_nombres(self):
        seleccion = self.seleccionado()
        self.lista.delete(0, "end")
        for nombre in self.nombres():
            self.lista.insert("end", nombre)
        if seleccion is not None and seleccion < len(self.formularios):
            self.lista.selection_set(seleccion)

    def refrescar(self):
        """Vuelve a leer los nombres de los formularios (se llama al editar)."""
        self._refrescar_nombres()