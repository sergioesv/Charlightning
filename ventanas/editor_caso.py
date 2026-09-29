"""
Paso 47b: el editor del caso completo. Aquí cae H19.

Un caso son cuatro cosas: la densidad de descargas N_G, la estructura, las
zonas y las líneas. Las dos últimas son LISTAS, y eso es lo que la pantalla
vieja no podía expresar: tenía una zona y tres ranuras fijas de línea
horneadas en los nombres de sus widgets.

La norma define el riesgo como R = suma sobre zonas de la suma de sus
componentes, y los ejemplos E.3 y E.4 tienen cinco y cuatro zonas. Con esto
el programa ya puede plantearlos.

casos_por_tipo() devuelve un caso por cada riesgo pedido, en el mismo
formato que casos.cargar_caso(), porque las pérdidas de una zona son de un
tipo de riesgo (ver el reparto COMUNES / POR_TIPO de formularios.py).
"""
from tkinter import ttk

from calculate_risk.norma import casos, riesgos
from ventanas import campos, emplazamiento, formularios, listas


class EditorCaso(ttk.Frame):
    """N_G, la estructura, la lista de zonas y la lista de líneas."""

    def __init__(self, padre):
        super().__init__(padre, padding=6)
        # Quien quiera enterarse de que se tocó un dato se apunta aquí.
        self.al_cambiar = lambda: None

        # De dónde sale N_G: por coordenadas o declarado con su fuente (Paso 58c).
        # `al_cambiar` se busca en el momento, porque quien vigila lo reemplaza.
        self.emplazamiento = emplazamiento.PanelEmplazamiento(
            self, al_cambiar=lambda: self.al_cambiar())
        self.emplazamiento.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.N_G = self.emplazamiento.N_G      
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.grid(row=1, column=0, sticky="nsew")

        self.estructura = formularios.FormularioEstructura(self.cuaderno)
        self.cuaderno.add(self.estructura, text="Estructura")
        # El cuaderno es lo que tiene que crecer con la ventana.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Sin zonas no hay riesgo que calcular: por eso el mínimo es 1.
        self.zonas = listas.ListaDeFormularios(
            self.cuaderno, formularios.FormularioZona,
            titulo="Zonas de la estructura", singular="zona", minimo=1)
        self.cuaderno.add(self.zonas, text="Zonas")

        # Las líneas sí pueden ser cero: una estructura aislada no tiene.
        self.lineas = listas.ListaDeFormularios(
            self.cuaderno, formularios.FormularioLinea,
            titulo="Líneas que entran a la estructura", singular="línea")
        self.cuaderno.add(self.lineas, text="Líneas")

    # -- lectura -----------------------------------------------------------


    def huella(self) -> tuple:
        """Foto cruda de todas las casillas, sin validar y sin calcular nada.

        Sirve para saber si un resultado ya mostrado sigue correspondiendo a
        lo que hay escrito. Se recorre el árbol de widgets y no una lista de
        campos, así una zona o una línea añadidas después entran solas, y la
        propia ruta del widget delata que se añadió o se quitó algo.
        """
        return tuple((str(w), _contenido(w)) for w in _descendientes(self))

    def casos_por_tipo(self, tipos=(1, 2, 3, 4)) -> dict:
        """{tipo: {"estructura":…, "lineas":[…], "zonas":[…], "N_G":…}}.

        La estructura y las líneas son las mismas para los cuatro riesgos;
        lo que cambia de un tipo a otro son las pérdidas de cada zona.
        """
        problemas = []
        partes = {}
        for nombre, leer in (("N_G", self.emplazamiento.resolver),
                             ("estructura", self.estructura.leer),
                             ("lineas", self.lineas.leer),
                             ("zonas", lambda: self.zonas.leer(tipos=tipos))):
            try:
                partes[nombre] = leer()
            except campos.DatoFaltante as error:
                problemas.append(f"{nombre.capitalize()}:\n{error}")
        if problemas:
            raise campos.DatoFaltante("\n\n".join(problemas))

        N_G, donde = partes["N_G"]
        return {
            tipo: {
                "estructura": partes["estructura"],
                "lineas": partes["lineas"],
                "zonas": [por_tipo[tipo] for por_tipo in partes["zonas"]],
                "N_G": N_G,
                "emplazamiento": donde,
            }
            for tipo in tipos
        }

    # -- escritura ---------------------------------------------------------
    
    def limpiar(self):
        """Deja el caso como recién abierto el programa: todo en blanco.

        La estructura se vuelve a crear entera en vez de ir vaciando casilla
        por casilla: así queda EXACTAMENTE igual que al arrancar —listas sin
        elegir y valores por defecto puestos— y no se puede olvidar ningún
        campo que se añada mañana. Las zonas y las líneas ya se rehacen
        solas, porque `poner([])` destruye sus formularios.
        """
        self.emplazamiento.limpiar()
        indice = self.cuaderno.index(self.estructura)
        self.estructura.destroy()
        self.estructura = formularios.FormularioEstructura(self.cuaderno)
        self.cuaderno.insert(indice, self.estructura, text="Estructura")
        self.zonas.poner([])
        self.lineas.poner([])
        self.cuaderno.select(indice)
        self.al_cambiar()


    def poner_caso(self, caso: dict, tipo: int = 1):
        """Abre un caso del formato de casos.cargar_caso().

        Ese formato trae las pérdidas de UN riesgo, así que las pestañas de
        los otros tres quedan en blanco y hay que llenarlas antes de pedir
        esos riesgos. El Paso 48 amplía el formato para guardar los cuatro.
        """
        self.emplazamiento.poner(caso["N_G"], caso.get("emplazamiento"))
        self.estructura.poner(caso["estructura"])
        self.lineas.poner(caso["lineas"])
        self.zonas.poner([{tipo: zona} for zona in caso["zonas"]])

    def poner(self, casos: dict):
        """Abre lo que devuelve casos_por_tipo()."""
        alguno = casos[sorted(casos)[0]]
        self.emplazamiento.poner(alguno["N_G"], alguno.get("emplazamiento"))
        self.estructura.poner(alguno["estructura"])
        self.lineas.poner(alguno["lineas"])
        self.zonas.poner([
            {tipo: casos[tipo]["zonas"][indice] for tipo in casos}
            for indice in range(len(alguno["zonas"]))
        ])


    def evaluar(self, tipos=(1, 2, 3, 4)) -> dict:
        """{tipo: resultado} corriendo el motor con las zonas de cada riesgo.

        No basta con una sola llamada a riesgos.evaluar con tipos=(1,2,3,4):
        las zonas de cada riesgo son objetos distintos, porque sus pérdidas
        lo son. Por eso el bucle.
        """
        resultados = {}
        vacios = []
        for tipo, caso in self.casos_por_tipo(tipos).items():
            if riesgos.sin_perdidas(caso["zonas"], tipo):
                vacios.append(SIN_PERDIDAS.format(
                    tipo=tipo, pestana=formularios.FormularioZona.TITULOS[tipo],
                    zonas=", ".join(z.nombre for z in caso["zonas"]) or "no hay zonas"))
                continue
            resultados[tipo] = riesgos.evaluar(
                caso["estructura"], caso["lineas"], caso["zonas"],
                caso["N_G"], tipos=(tipo,))[tipo]
        if vacios:
            raise campos.DatoFaltante("\n\n".join(vacios))
        return resultados
        
    # -- archivo -----------------------------------------------------------

    def guardar(self, ruta, tipos=(1, 2, 3, 4)) -> str:
        """Escribe el caso en un archivo JSON. Avisa si falta algo antes."""
        return casos.guardar_caso(ruta, self.casos_por_tipo(tipos))

    def abrir(self, ruta):
        """Abre un archivo JSON, del formato que sea."""
        self.poner(casos.cargar_casos(ruta))

SIN_PERDIDAS = ("R{tipo} no tiene pérdidas cargadas en ninguna zona ({zonas}): daría 0 y "
                "«Cumple» sin haber evaluado nada. Carga las pérdidas en la pestaña "
                "«{pestana}» de cada zona, o desmarca R{tipo} arriba.")

def _descendientes(widget):
    """El widget y todo lo que cuelga de él, en orden."""
    yield widget
    for hijo in widget.winfo_children():
        yield from _descendientes(hijo)


def _contenido(widget):
    """Lo que el usuario escribió o eligió; None si el widget no guarda datos."""
    if isinstance(widget, ttk.Combobox):
        return widget.current()
    if isinstance(widget, ttk.Entry):
        return widget.get()
    if isinstance(widget, (ttk.Checkbutton, ttk.Radiobutton)):
        variable = str(widget.cget("variable"))
        return widget.getvar(variable) if variable else None
    return None