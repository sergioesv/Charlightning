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
import os
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from calculate_risk.norma import medidas, memoria
from ventanas import campos, desglose, editor_caso, resultados
from ventanas.panel import Panel
from variables.globales import papo

NOMBRES_RIESGOS = {1: "R1 vidas", 2: "R2 servicio", 3: "R3 patrimonio",
                   4: "R4 económica"}

CUANTAS_SOLUCIONES = 15

# Los ejemplos resueltos del Anexo E, los que vienen con el programa. La
# carpeta se busca al lado del código y no en el directorio desde el que se
# arrancó: si no, abrir un ejemplo obliga a saber dónde quedó instalado.
CARPETA_DE_CASOS = pathlib.Path(__file__).resolve().parent.parent / "casos"

EJEMPLOS_DE_LA_NORMA = (
    ("E.2  Casa rural (1 zona)", "casa_rural.json"),
    ("E.3  Edificio de oficinas (5 zonas)", "E3_oficinas.json"),
    ("E.4  Hospital (4 zonas)", "E4_hospital.json"),
    ("E.5  Edificio de apartamentos (1 zona)", "E5_apartamentos.json"),
)

class PrincipalNorma(Panel):
    """La pantalla completa: caso arriba, resultados abajo."""

    def __init__(self, master, titulo="Charlightning — NTC 4552-2:2023",
                 ancho=1366, alto=768):
        super().__init__(master, titulo=titulo, ancho=ancho, alto=alto)
        self.anterior_modo = lambda: None
        self.ultimo_calculo = None
        self.huella_calculo = None

        barra = ttk.Frame(self)
        barra.pack(side="top", fill="x", padx=10, pady=6)
        self._botones(barra)
        self._casillas_de_riesgo(barra)

        # El panel de resultados se empaqueta ANTES y abajo: así tiene su
        # sitio reservado y el editor no se lo come al crecer.
        self.resultados = resultados.PanelResultados(self)
        self.resultados.pack(side="bottom", fill="x", padx=10, pady=6)
        self.resultados.boton_medidas.configure(command=self.buscar_medidas)
        self.resultados.boton_desglose.configure(command=self.de_donde_viene)
        self.editor = editor_caso.EditorCaso(self)
        self.editor.pack(side="top", fill="both", expand=True, padx=10)
        self._vigilar_cambios()

    def _botones(self, barra):
        """La barra de arriba. El menú de ejemplos va junto a «Abrir caso»."""
        self.botones = {}
        columna = 0
        for texto, accion in (("Caso nuevo", self.nuevo),
                              ("Abrir caso", self.abrir)):
            self._boton(barra, texto, accion, columna)
            columna += 1
        self._menu_de_ejemplos(barra, columna)
        columna += 1
        for texto, accion in (("Guardar caso", self.guardar),
                              ("Calcular", self.calcular),
                              ("Informe", self.informe),
                              ("Volver", self.volver)):
            self._boton(barra, texto, accion, columna)
            columna += 1

    def _boton(self, barra, texto, accion, columna):
        boton = ttk.Button(barra, text=texto, command=accion)
        boton.grid(row=0, column=columna, padx=(0, 6))
        self.botones[texto] = boton

    def _menu_de_ejemplos(self, barra, columna):
        """Los cuatro ejemplos del Anexo E, a un clic y sin buscar carpeta."""
        self.boton_ejemplos = ttk.Menubutton(barra, text="Ejemplos de la norma")
        self.menu_ejemplos = tk.Menu(self.boton_ejemplos, tearoff=False)
        self.boton_ejemplos.configure(menu=self.menu_ejemplos)
        for texto, archivo in EJEMPLOS_DE_LA_NORMA:
            self.menu_ejemplos.add_command(
                label=texto,
                command=lambda archivo=archivo: self.abrir_ejemplo(archivo))
        self.boton_ejemplos.grid(row=0, column=columna, padx=(0, 6))

    def _casillas_de_riesgo(self, barra):
        ttk.Label(barra, text="    Evaluar:").grid(row=0, column=9)
        self.marcas = {}
        for posicion, (tipo, nombre) in enumerate(NOMBRES_RIESGOS.items()):
            marca = tk.BooleanVar(value=(tipo == 1))
            ttk.Checkbutton(barra, text=nombre, variable=marca,
                            command=self.revisar_cambios).grid(
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
            self.huella_calculo = None
            messagebox.showinfo(title="Faltan datos", message=str(error))
            return None
        self.huella_calculo = self.huella()
        self.resultados.mostrar(self.ultimo_calculo)
        return self.ultimo_calculo

    def nuevo(self, confirmado=None):
        """Deja la pantalla en cero: ni datos escritos ni resultados.

        Pregunta antes, porque se lleva por delante todo lo que haya. Las
        pruebas pasan `confirmado` y así no se abre ningún cuadro.
        """
        if confirmado is None:
            confirmado = messagebox.askyesno(
                title="Caso nuevo",
                message=("Se va a borrar todo lo escrito y los resultados.\n"
                         "¿Seguir?"))
        if not confirmado:
            return False
        self.editor.limpiar()
        self.resultados.limpiar()
        self.ultimo_calculo = None
        self.huella_calculo = None
        return True

    def abrir_ejemplo(self, archivo: str):
        """Abre uno de los ejemplos que vienen con el programa."""
        return self.abrir(CARPETA_DE_CASOS / archivo)

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
        self.ultimo_calculo = None
        self.huella_calculo = None
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
        """Escribe la memoria completa: .tex, PDF, figuras y CSV de medidas.

        Las figuras y el CSV quedan en la misma carpeta que el .tex, que es
        lo que LaTeX necesita para encontrar los PNG al compilar.
        """
        # Recalcular ANTES de escribir no es un lujo: la memoria se arma con
        # las entradas frescas del formulario, así que usar un resultado
        # viejo sacaría un documento con las tablas de entrada nuevas y los
        # riesgos antiguos. El entregable es material del artículo.
        if self.al_dia() is None:
            return None
        ruta = ruta or filedialog.asksaveasfilename(
            title="Guardar la memoria", defaultextension=".tex",
            initialfile="Memoria de calculo.tex",
            filetypes=[("LaTeX", "*.tex")])
        if not ruta:
            return None

        tipos = self.tipos()
        carpeta, archivo = os.path.split(str(ruta))
        nombre = os.path.splitext(archivo)[0] or "Memoria de calculo"
        ruta_tex, ruta_pdf = memoria.informe_completo_caso(
            carpeta or ".", self.editor.casos_por_tipo(tipos),
            self.ultimo_calculo, proyecto=self._datos_proyecto(),
            nombre=nombre, tipo=tipos[0])

        if ruta_pdf:
            messagebox.showinfo(title="Memoria de cálculo",
                                message=f"Memoria generada:\n{ruta_pdf}")
            return ruta_pdf
        messagebox.showinfo(
            title="Memoria de cálculo",
            message=(f"Se escribió el LaTeX:\n{ruta_tex}\n\n"
                     "Para obtener el PDF hace falta tener LaTeX instalado."))
        return ruta_tex

    def buscar_medidas(self):
        """Busca combinaciones de medidas para el primer riesgo que no cumple."""
        if self.ultimo_calculo is None or self.al_dia() is None:
            return None
        if all(r["cumple"] for r in self.ultimo_calculo.values()):
            return None
        tipo = self._primero_que_no_cumple()
        caso = self.editor.casos_por_tipo((tipo,))[tipo]

        soluciones = medidas.explorar(caso["estructura"], caso["lineas"],
                                      caso["zonas"], caso["N_G"], tipo=tipo)
        self._mostrar_soluciones(tipo, soluciones)
        return soluciones

    def de_donde_viene(self):
        """Abre el desglose del riesgo elegido en el panel (Paso 56).

        Si no hay ninguno elegido se toma el primero que no cumple, que es
        el que le interesa a quien está diseñando la protección.
        """
        if self.ultimo_calculo is None or self.al_dia() is None:
            return None
        tipo = self.resultados.riesgo_elegido() or self._primero_que_no_cumple()
        caso = self.editor.casos_por_tipo((tipo,))[tipo]
        aportes = medidas.de_donde_viene(caso["estructura"], caso["lineas"],
                                         caso["zonas"], caso["N_G"], tipo=tipo)
        self.ventana_desglose = desglose.VentanaDesglose(
            self, tipo, aportes, self.ultimo_calculo[tipo])
        return aportes

    def _primero_que_no_cumple(self) -> int:
        incumplen = [t for t, r in self.ultimo_calculo.items() if not r["cumple"]]
        return min(incumplen or self.ultimo_calculo)

    def volver(self):
        self.anterior_modo()

    # -- que lo que se ve corresponda a los datos ---------------------------

    def huella(self) -> tuple:
        """Todo lo que entra al cálculo: los riesgos marcados y el editor."""
        return (self.tipos(), self.editor.huella())

    def al_dia(self):
        """El resultado vigente, recalculándolo si los datos ya no son esos."""
        if self.ultimo_calculo is None or self.huella() != self.huella_calculo:
            return self.calcular()
        return self.ultimo_calculo

    def revisar_cambios(self) -> bool:
        """Pone el panel en gris si lo que se ve ya no sale de lo escrito.

        Si el cambio se deshace (se vuelve a escribir lo que había), el
        resultado sigue siendo válido y se devuelve a sus colores.
        """
        if self.huella_calculo is None:
            return False
        if self.huella() != self.huella_calculo:
            return self.resultados.marcar_obsoleto()
        if self.resultados.obsoleto:
            self.resultados.mostrar(self.ultimo_calculo)
        return False

    def _vigilar_cambios(self):
        """Se entera de que tocaron una casilla del editor.

        El enganche va en la ventana entera porque un Frame no recibe los
        eventos de sus hijos, y se filtra por la ruta del editor. Hecho así
        —y no campo por campo— quedan vigiladas también las casillas de una
        zona o una línea que se añadan después.
        """
        ventana = self.winfo_toplevel()
        for evento in ("<KeyRelease>", "<<ComboboxSelected>>", "<ButtonRelease-1>"):
            ventana.bind(evento, self._tocaron_el_editor, add="+")
        self.editor.al_cambiar = self.revisar_cambios

    def _tocaron_el_editor(self, evento):
        ruta, raiz = str(evento.widget), str(self.editor)
        if ruta == raiz or ruta.startswith(raiz + "."):
            self.revisar_cambios()

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