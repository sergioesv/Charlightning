"""
Paso 49: el panel de resultados de la pantalla nueva.

Muestra los cuatro riesgos con su tolerable y su veredicto, y debajo de cada
uno el desglose por zona, que es lo que la pantalla vieja no podía enseñar
porque solo manejaba una zona.

Sobre los colores: cumple va en azul y no cumple en naranja, NO en verde y
rojo. Verde y rojo son justo el par que no distingue una persona con
daltonismo (el más común); el validador da ΔE 4,1 para verde-rojo contra
24,7 para azul-naranja. Es la misma decisión y la misma paleta de
graficos.py, y hay una prueba que comprueba que sigan siendo los mismos.
Además el veredicto va escrito con todas las letras: el color nunca es lo
único que lleva el significado.
"""
from tkinter import ttk

from calculate_risk.norma import tablas

AZUL = "#2a78d6"        # cumple
NARANJA = "#eb6834"     # no cumple
GRIS = "#8a8a8a"        # el resultado ya no corresponde a los datos

TITULOS = {
    1: "R1 · Pérdida de vidas humanas",
    2: "R2 · Pérdida de servicio público",
    3: "R3 · Pérdida de patrimonio cultural",
    4: "R4 · Pérdida económica",
}


def numero(valor) -> str:
    """2.506e-05 -> '2,506e-05'. Coma decimal, como el resto del programa."""
    if valor == 0:
        return "0"
    return f"{valor:.3e}".replace(".", ",")


def porcentaje(parte, total) -> str:
    if not total:
        return "—"
    return f"{parte / total * 100:.1f} %".replace(".", ",")


class PanelResultados(ttk.LabelFrame):
    """Tabla de riesgos con sus zonas colgando de cada uno."""

    COLUMNAS = ("calculado", "tolerable", "veredicto")
    ENCABEZADOS = {"calculado": "Riesgo calculado [1/año]",
                   "tolerable": "Tolerable R_T",
                   "veredicto": "Veredicto"}

    def __init__(self, padre, titulo="Resultados"):
        super().__init__(padre, text=titulo, padding=8)

        self.arbol = ttk.Treeview(self, columns=self.COLUMNAS, height=6)
        self.arbol.heading("#0", text="Riesgo y zonas", anchor="w")
        self.arbol.column("#0", width=280, anchor="w")
        for columna in self.COLUMNAS:
            self.arbol.heading(columna, text=self.ENCABEZADOS[columna], anchor="e")
            self.arbol.column(columna, width=150, anchor="e")
        self.arbol.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(self, orient="vertical", command=self.arbol.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.arbol.configure(yscrollcommand=barra.set)

        self.arbol.tag_configure("cumple", foreground=AZUL)
        self.arbol.tag_configure("no_cumple", foreground=NARANJA)

        pie = ttk.Frame(self)
        pie.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.aviso = ttk.Label(pie, text="")
        self.aviso.grid(row=0, column=0, padx=(0, 12))
        self.boton_desglose = ttk.Button(pie, text="¿De dónde viene el riesgo?",
                                         state="disabled")
        self.boton_desglose.grid(row=0, column=2)
        self.obsoleto = False

    # -- contenido ---------------------------------------------------------

    def limpiar(self):
        for fila in self.arbol.get_children():
            self.arbol.delete(fila)
        self.aviso.configure(text="")
        self.boton_medidas.configure(state="disabled")
        self._colorear(AZUL, NARANJA)
        self.obsoleto = False

    def _colorear(self, cumple, no_cumple, zona=""):
        self.arbol.tag_configure("cumple", foreground=cumple)
        self.arbol.tag_configure("no_cumple", foreground=no_cumple)
        self.arbol.tag_configure("zona", foreground=zona)

    def marcar_obsoleto(self) -> bool:
        """Los datos cambiaron: lo que se ve ya no corresponde a lo escrito.

        Todo se pone en gris y el aviso lo dice. Es lo que pedía Sergio: un
        pantallazo del panel nunca puede enseñar un riesgo que no salga de
        los datos que se ven al lado.
        """
        if not self.arbol.get_children():
            return False
        self.obsoleto = True
        self._colorear(GRIS, GRIS, GRIS)
        self.aviso.configure(
            text="Los datos cambiaron: hay que volver a calcular.",
            foreground=GRIS)
        self.boton_desglose.configure(state="disabled")
        return True

    def mostrar(self, resultados: dict):
        """resultados = {tipo: lo que devuelve riesgos.evaluar para ese tipo}."""
        self.limpiar()
        for tipo in sorted(resultados):
            r = resultados[tipo]
            etiqueta = "cumple" if r["cumple"] else "no_cumple"
            padre = self.arbol.insert(
                "", "end", iid=f"R{tipo}", text=TITULOS[tipo], open=True,
                values=(numero(r["total"]), numero(r["R_T"]),
                        "Cumple" if r["cumple"] else "No cumple"),
                tags=(etiqueta,))

            for nombre, por_zona in r["zonas"].items():
                self.arbol.insert(
                    padre, "end", text=f"    {nombre}",
                    values=(numero(por_zona["total"]), "",
                            porcentaje(por_zona["total"], r["total"])),
                    tags=("zona",))

        self._resumir(resultados)

    def _resumir(self, resultados):
        # El desglose vale cumpla o no cumpla: saber de dónde viene el riesgo
        # es tan útil cuando cumple (¿por qué?) como cuando no.
        self.boton_desglose.configure(state="normal" if resultados else "disabled")
        incumplen = [tipo for tipo, r in resultados.items() if not r["cumple"]]
        if incumplen:
            cuales = ", ".join(f"R{tipo}" for tipo in sorted(incumplen))
            self.aviso.configure(
                text=f"No cumple: {cuales}. Hace falta protección.",
                foreground=NARANJA)
        else:
            self.aviso.configure(
                text="Los riesgos evaluados están por debajo del tolerable.",
                foreground=AZUL)

    def riesgo_elegido(self):
        """El tipo de riesgo seleccionado en el árbol, o None.

        Da igual si lo que se pulsó fue el riesgo o una de sus zonas: de una
        zona se sube al riesgo del que cuelga.
        """
        elegidos = self.arbol.selection()
        if not elegidos:
            return None
        fila = elegidos[0]
        fila = self.arbol.parent(fila) or fila
        return int(fila.removeprefix("R"))
        
    # -- para las pruebas y para el informe ---------------------------------

    def filas(self) -> list:
        """Lo que se ve, en texto: [(nivel, etiqueta, calculado, tolerable, veredicto)]."""
        salida = []
        for riesgo in self.arbol.get_children():
            salida.append(("riesgo", self.arbol.item(riesgo, "text"),
                           *self.arbol.item(riesgo, "values")))
            for zona in self.arbol.get_children(riesgo):
                salida.append(("zona", self.arbol.item(zona, "text").strip(),
                               *self.arbol.item(zona, "values")))
        return salida


def tolerable(tipo: int) -> float:
    """El R_T de la Tabla 4 para ese riesgo, sin pasar por el motor."""
    return tablas.RT[f"L{tipo}"]