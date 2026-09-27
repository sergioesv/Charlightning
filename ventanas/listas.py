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
from tkinter import messagebox, ttk

from ventanas import campos
GRIS = "#8a8a8a"

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

        # El formulario va dentro de un lienzo con barra: el de una zona mide
        # unos 490 px y en una pantalla de 768 no cabe. Sin esto las pestañas
        # de pérdidas (L_T, L_F, L_O, h_z) no llegan a verse y el cálculo
        # pide datos que el usuario no tiene dónde escribir.
        self.lienzo = tk.Canvas(self, highlightthickness=0)
        self.lienzo.grid(row=0, column=1, sticky="nsew")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        barra.grid(row=0, column=2, sticky="ns")
        self.lienzo.configure(yscrollcommand=barra.set)

        self.zona_formulario = ttk.Frame(self.lienzo)
        self.lienzo.create_window((0, 0), window=self.zona_formulario, anchor="nw")
        self.zona_formulario.bind(
            "<Configure>",
            lambda _e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        # La rueda solo mueve el lienzo que tenga el puntero encima.
        self.lienzo.bind("<Enter>", lambda _e: self._rueda(True))
        self.lienzo.bind("<Leave>", lambda _e: self._rueda(False))

        botones = ttk.Frame(self)
        botones.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.boton_anadir = ttk.Button(botones, text=f"+ {singular.capitalize()}",
                                       command=self.anadir)
        self.boton_anadir.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        self.boton_quitar = ttk.Button(botones, text=f"− {singular.capitalize()}",
                                       command=self.pedir_quitar)
        self.boton_quitar.grid(row=0, column=1, sticky="ew")
        # Un botón apagado sin explicación es otra forma de no decir nada:
        # debajo va SIEMPRE el motivo por el que no se puede quitar.
        self.razon_quitar = ttk.Label(botones, text="", wraplength=200,
                                      justify="left", foreground=GRIS)
        self.razon_quitar.grid(row=1, column=0, columnspan=2, sticky="w",
                               pady=(4, 0))
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        # El formulario de la derecha es el que tiene que crecer: sin esto
        # se queda en su alto mínimo y las pestañas de abajo no se ven.
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._actualizar_botones()

    def _rueda(self, encendida):
        """Engancha o suelta la rueda del ratón sobre este lienzo."""
        if encendida:
            self.lienzo.bind_all("<MouseWheel>", self._girar)
            self.lienzo.bind_all("<Button-4>", self._girar)
            self.lienzo.bind_all("<Button-5>", self._girar)
        else:
            for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.lienzo.unbind_all(evento)

    def _girar(self, evento):
        """Windows y Mac mandan delta; X11 manda los botones 4 y 5."""
        if evento.num == 4:
            pasos = -1
        elif evento.num == 5:
            pasos = 1
        else:
            pasos = -1 if evento.delta > 0 else 1
        self.lienzo.yview_scroll(pasos, "units")

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
        """Quita el elemento seleccionado. Si no se puede, DICE por qué.

        Antes se iba en silencio cuando no había nada elegido, y lanzaba la
        excepción sin recoger cuando se llegaba al mínimo: dentro de un
        callback de tkinter eso muere en report_callback_exception, o sea
        que se imprime en la consola y el usuario no ve absolutamente nada.
        Ahora siempre avisa, y quien llama decide cómo enseñarlo.
        """
        if not self.puede_quitar():
            raise campos.DatoFaltante(self.razon_para_no_quitar())
        indice = self.seleccionado()
        self.formularios.pop(indice).destroy()
        self._refrescar_nombres()
        if self.formularios:
            self.lista.selection_set(min(indice, len(self.formularios) - 1))
        self.mostrar_seleccionado()

    def pedir_quitar(self):
        """Lo que hace el botón: quita, y si no se puede lo dice en pantalla."""
        try:
            self.quitar()
        except campos.DatoFaltante as error:
            messagebox.showinfo(title="No se puede quitar", message=str(error))

    def razon_para_no_quitar(self) -> str:
        """Por qué no se puede quitar ahora mismo; vacío si sí se puede."""
        if not self.formularios:
            return "No hay nada que quitar."
        if len(self.formularios) <= self.minimo:
            return (f"Tiene que quedar al menos {self.minimo} "
                    f"{self.singular}.")
        if self.seleccionado() is None:
            return f"Elige en la lista qué {self.singular} quitar."
        return ""

    def puede_quitar(self) -> bool:
        return not self.razon_para_no_quitar()

    def _actualizar_botones(self):
        razon = self.razon_para_no_quitar()
        self.boton_quitar.configure(state="disabled" if razon else "normal")
        self.razon_quitar.configure(text=razon)

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
        self._actualizar_botones()

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
        self._actualizar_botones()
        
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