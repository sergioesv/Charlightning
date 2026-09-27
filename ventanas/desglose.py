"""
Paso 56: de dónde viene el riesgo y qué medida baja cada parte.

Es el punto 4 de la Fase 6: «NO SE QUE VARIABLES INTERVIENEN PARA MITIGAR TAL
DAÑO». El panel de resultados dice cuánto vale R1 y si cumple, pero no de qué
está hecho ese número ni dónde hay que meter mano.

Arriba, los ocho componentes del numeral 4.2 con lo que aporta cada uno; al
elegir uno, abajo salen las medidas del catálogo que lo bajan EN ESTE CASO,
con a cuánto lo dejan y a cuánto queda el riesgo entero. Nada de esto se
escribe aquí: los números los calcula medidas.de_donde_viene() probando cada
medida sobre el caso, y los textos salen de etiquetas.py.
"""
import tkinter as tk
from tkinter import ttk

from calculate_risk.norma import etiquetas
from ventanas import resultados


class VentanaDesglose(tk.Toplevel):
    """De dónde viene un riesgo y qué medidas actúan sobre cada componente."""

    SIN_MEDIDAS = ("Ninguna medida del catálogo baja este componente. "
                   "Aquí se baja el riesgo reduciendo la pérdida: n_z/n_t, "
                   "t_z, o separando la zona.")

    def __init__(self, padre, tipo, aportes, resultado):
        super().__init__(padre)
        self.title(f"De dónde viene R{tipo}")
        self.tipo = tipo
        self.aportes = list(aportes)
        self.por_componente = {a.componente: a for a in self.aportes}

        self._encabezado(resultado)
        self._tabla_de_componentes()
        self._tabla_de_medidas()

        self.columnconfigure(0, weight=1)
        if self.aportes:
            self.elegir(self.aportes[0].componente)

    # -- dibujo ------------------------------------------------------------

    def _encabezado(self, resultado):
        cumple = resultado["cumple"]
        texto = (f"{resultados.TITULOS[self.tipo]}   "
                 f"{resultados.numero(resultado['total'])} 1/año   "
                 f"(tolerable {resultados.numero(resultado['R_T'])})   "
                 f"{'Cumple' if cumple else 'No cumple'}")
        self.titulo = ttk.Label(
            self, text=texto, padding=8,
            foreground=resultados.AZUL if cumple else resultados.NARANJA)
        self.titulo.grid(row=0, column=0, sticky="w")

    def _tabla_de_componentes(self):
        marco = ttk.LabelFrame(self, text="De qué está hecho el riesgo",
                               padding=8)
        marco.grid(row=1, column=0, sticky="nsew", padx=8)

        self.componentes = ttk.Treeview(
            marco, columns=("valor", "parte"), height=min(8, len(self.aportes) or 1))
        self.componentes.heading("#0", text="Componente", anchor="w")
        self.componentes.column("#0", width=620, anchor="w")
        self.componentes.heading("valor", text="1/año", anchor="e")
        self.componentes.column("valor", width=120, anchor="e")
        self.componentes.heading("parte", text="Parte del riesgo", anchor="e")
        self.componentes.column("parte", width=130, anchor="e")
        self.componentes.grid(row=0, column=0, sticky="nsew")
        self.componentes.bind("<<TreeviewSelect>>", self._cambio_de_componente)

        for aporte in self.aportes:
            self.componentes.insert(
                "", "end", iid=aporte.componente,
                text=etiquetas.texto_de_componente(aporte.componente),
                values=(resultados.numero(aporte.valor),
                        resultados.porcentaje(aporte.valor, self._total())))
        marco.columnconfigure(0, weight=1)

    def _tabla_de_medidas(self):
        self.marco_medidas = ttk.LabelFrame(self, text="Medidas", padding=8)
        self.marco_medidas.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)

        self.medidas = ttk.Treeview(
            self.marco_medidas, columns=("componente", "total", "veredicto"),
            height=10)
        self.medidas.heading("#0", text="Medida", anchor="w")
        self.medidas.column("#0", width=660, anchor="w")
        self.medidas.heading("componente", text="Lo deja en", anchor="e")
        self.medidas.column("componente", width=120, anchor="e")
        self.medidas.heading("total", text=f"R{self.tipo} queda en", anchor="e")
        self.medidas.column("total", width=130, anchor="e")
        self.medidas.heading("veredicto", text="¿Basta con ella?", anchor="e")
        self.medidas.column("veredicto", width=130, anchor="e")
        self.medidas.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(self.marco_medidas, orient="vertical",
                              command=self.medidas.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.medidas.configure(yscrollcommand=barra.set)
        self.medidas.tag_configure("cumple", foreground=resultados.AZUL)
        self.marco_medidas.columnconfigure(0, weight=1)

    # -- contenido ---------------------------------------------------------

    def _total(self) -> float:
        return sum(aporte.valor for aporte in self.aportes)

    def _cambio_de_componente(self, _evento=None):
        elegidos = self.componentes.selection()
        if elegidos:
            self.elegir(elegidos[0])

    def elegir(self, componente: str):
        """Llena la tabla de abajo con las medidas que bajan ese componente."""
        if self.componentes.selection() != (componente,):
            self.componentes.selection_set(componente)
        aporte = self.por_componente[componente]
        self.marco_medidas.configure(
            text=f"Medidas que bajan {componente} en este caso")

        for fila in self.medidas.get_children():
            self.medidas.delete(fila)

        if not aporte.rebajas:
            self.medidas.insert("", "end", text=self.SIN_MEDIDAS, values=("", "", ""))
            return

        for rebaja in aporte.rebajas:
            self.medidas.insert(
                "", "end", text=etiquetas.texto_de_medida(rebaja.medida.nombre),
                values=(resultados.numero(rebaja.componente),
                        resultados.numero(rebaja.total),
                        "Sí, ya cumple" if rebaja.cumple else "No, ella sola no"),
                tags=("cumple",) if rebaja.cumple else ())

    # -- para las pruebas --------------------------------------------------

    def filas_componentes(self) -> list:
        return [(fila, *self.componentes.item(fila, "values"))
                for fila in self.componentes.get_children()]

    def filas_medidas(self) -> list:
        return [(self.medidas.item(fila, "text"), *self.medidas.item(fila, "values"))
                for fila in self.medidas.get_children()]