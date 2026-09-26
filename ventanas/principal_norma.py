"""
Paso 51a: la ventana de la pantalla nueva.

Junta el editor del caso (Paso 47b) con el panel de resultados (Paso 49) y
pone los botones: abrir, guardar, calcular, informe y buscar medidas.

Los métodos que tocan archivos aceptan la ruta como argumento. Si no se les
da, la preguntan con el diálogo del sistema. Así las pruebas pueden llamarlos
sin abrir ningún cuadro de diálogo, que es lo que las volvería inmanejables.

Arriba se elige qué riesgos se evalúan. Arranca solo con R1 porque es lo que
pide casi todo proyecto, y porque obligar a llenar las pérdidas económicas
para ver el riesgo de vidas humanas no tiene sentido.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from calculate_risk.norma import medidas, memoria
from ventanas import campos, editor_caso, resultados
from ventanas.panel import Panel
from variables.globales import papo

NOMBRES_RIESGOS = {1: "R1 vidas", 2: "R2 servicio", 3: "R3 patrimonio",
                   4: "R4 económica"}

CUANTAS_SOLUCIONES = 15


class PrincipalNorma(Panel):
    """La pantalla completa: caso arriba, resultados abajo."""

    def __init__(self, master, titulo="Charlightning — NTC 4552-2:2023",
                 ancho=1366, alto=768):
        super().__init__(master, titulo=titulo, ancho=ancho, alto=alto)
        self.anterior_modo = lambda: None
        self.ultimo_calculo = None

        barra = ttk.Frame(self)
        barra.pack(side="top", fill="x", padx=10, pady=6)
        self._botones(barra)
        self._casillas_de_riesgo(barra)

        # El panel de resultados se empaqueta ANTES y abajo: así tiene su
        # sitio reservado y el editor no se lo come al crecer.
        self.resultados = resultados.PanelResultados(self)
        self.resultados.pack(side="bottom", fill="x", padx=10, pady=6)
        self.resultados.boton_medidas.configure(command=self.buscar_medidas)

        self.editor = editor_caso.EditorCaso(self)
        self.editor.pack(side="top", fill="both", expand=True, padx=10)

    def _botones(self, barra):
        acciones = (("Abrir caso", self.abrir), ("Guardar caso", self.guardar),
                    ("Calcular", self.calcular), ("Informe", self.informe),
                    ("Volver", self.volver))
        self.botones = {}
        for columna, (texto, accion) in enumerate(acciones):
            boton = ttk.Button(barra, text=texto, command=accion)
            boton.grid(row=0, column=columna, padx=(0, 6))
            self.botones[texto] = boton

    def _casillas_de_riesgo(self, barra):
        ttk.Label(barra, text="    Evaluar:").grid(row=0, column=9)
        self.marcas = {}
        for posicion, (tipo, nombre) in enumerate(NOMBRES_RIESGOS.items()):
            marca = tk.BooleanVar(value=(tipo == 1))
            ttk.Checkbutton(barra, text=nombre, variable=marca).grid(
                row=0, column=10 + posicion, padx=2)
            self.marcas[tipo] = marca

    def tipos(self) -> tuple:
        """Los riesgos marcados arriba. Si no hay ninguno, R1."""
        elegidos = tuple(tipo for tipo, marca in self.marcas.items() if marca.get())
        return elegidos or (1,)

    # -- acciones ----------------------------------------------------------

    def calcular(self):
        """Evalúa el caso y llena el panel. Si falta algo, lo dice todo junto."""
        try:
            self.ultimo_calculo = self.editor.evaluar(self.tipos())
        except campos.DatoFaltante as error:
            self.resultados.limpiar()
            self.ultimo_calculo = None
            messagebox.showinfo(title="Faltan datos", message=str(error))
            return None
        self.resultados.mostrar(self.ultimo_calculo)
        return self.ultimo_calculo

    def abrir(self, ruta=None):
        ruta = ruta or filedialog.askopenfilename(
            title="Abrir caso", filetypes=[("Casos", "*.json")])
        if not ruta:
            return None
        try:
            self.editor.abrir(ruta)
        except (OSError, ValueError, KeyError, campos.DatoFaltante) as error:
            messagebox.showinfo(title="No se pudo abrir", message=str(error))
            return None
        self.resultados.limpiar()
        return ruta

    def guardar(self, ruta=None):
        ruta = ruta or filedialog.asksaveasfilename(
            title="Guardar caso", defaultextension=".json",
            filetypes=[("Casos", "*.json")])
        if not ruta:
            return None
        try:
            return self.editor.guardar(ruta, self.tipos())
        except campos.DatoFaltante as error:
            messagebox.showinfo(title="Faltan datos", message=str(error))
            return None

    def informe(self, ruta=None):
        """Escribe la memoria de cálculo. Compila el PDF si hay LaTeX."""
        if self.ultimo_calculo is None and self.calcular() is None:
            return None
        ruta = ruta or filedialog.asksaveasfilename(
            title="Guardar la memoria", defaultextension=".tex",
            initialfile="Memoria de calculo.tex",
            filetypes=[("LaTeX", "*.tex")])
        if not ruta:
            return None

        tipos = self.tipos()
        ruta_tex = memoria.escribir_memoria_caso(
            ruta, self.editor.casos_por_tipo(tipos), self.ultimo_calculo,
            proyecto=self._datos_proyecto(), tipo_desarrollado=tipos[0])
        try:
            ruta_pdf = memoria.compilar(ruta_tex)
            messagebox.showinfo(title="Memoria de cálculo",
                                message=f"Memoria generada:\n{ruta_pdf}")
            return ruta_pdf
        except RuntimeError as error:
            messagebox.showinfo(
                title="Memoria de cálculo",
                message=f"Se escribió el LaTeX:\n{ruta_tex}\n\n{error}")
            return ruta_tex

    def buscar_medidas(self):
        """Busca combinaciones de medidas para el primer riesgo que no cumple."""
        if self.ultimo_calculo is None:
            return None
        incumplen = [t for t, r in self.ultimo_calculo.items() if not r["cumple"]]
        if not incumplen:
            return None
        tipo = min(incumplen)
        caso = self.editor.casos_por_tipo((tipo,))[tipo]

        soluciones = medidas.explorar(caso["estructura"], caso["lineas"],
                                      caso["zonas"], caso["N_G"], tipo=tipo)
        self._mostrar_soluciones(tipo, soluciones)
        return soluciones

    def volver(self):
        self.anterior_modo()

    # -- auxiliares --------------------------------------------------------

    def _datos_proyecto(self) -> dict:
        return {"Proyecto": papo.get("proyecto", ""),
                "Diseñador": papo.get("disenador", ""),
                "Dirección": papo.get("direccion", ""),
                "Teléfono": papo.get("telefono", ""),
                "Descripción": papo.get("descripcion", "")}

    def _mostrar_soluciones(self, tipo, soluciones):
        ventana = tk.Toplevel(self)
        ventana.title(f"Medidas de protección para R{tipo}")
        self.ventana_medidas = ventana

        if not soluciones:
            ttk.Label(ventana, padding=12, wraplength=520, text=(
                "Ninguna combinación de las medidas contempladas lleva el riesgo "
                "por debajo del tolerable. Hay que revisar el caso: puede que "
                "haga falta reducir la pérdida (n_z, t_z) o separar la zona.")
            ).pack()
            return

        tabla = ttk.Treeview(ventana, columns=("riesgo", "costo"), height=15)
        tabla.heading("#0", text="Medidas", anchor="w")
        tabla.column("#0", width=520, anchor="w")
        tabla.heading("riesgo", text=f"R{tipo} resultante", anchor="e")
        tabla.heading("costo", text="Costo", anchor="e")
        tabla.column("riesgo", width=140, anchor="e")
        tabla.column("costo", width=110, anchor="e")
        for solucion in soluciones[:CUANTAS_SOLUCIONES]:
            tabla.insert("", "end",
                         text=", ".join(m.nombre for m in solucion.medidas),
                         values=(resultados.numero(solucion.riesgo),
                                 f"{solucion.costo:,.0f}".replace(",", " ")))
        tabla.pack(padx=10, pady=10)
        self.tabla_medidas = tabla