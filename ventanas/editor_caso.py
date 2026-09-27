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
from ventanas import campos, dialogo_densidad, formularios, listas


class EditorCaso(ttk.Frame):
    """N_G, la estructura, la lista de zonas y la lista de líneas."""

    def __init__(self, padre):
        super().__init__(padre, padding=6)
        # Quien quiera enterarse de que se tocó un dato se apunta aquí.
        self.al_cambiar = lambda: None
        
        cabecera = ttk.Frame(self)
        cabecera.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.N_G = campos.CampoNumero(
            cabecera, "Densidad de descargas a tierra (N_G)", 0,
            unidad="rayos/km² año", positivo=True)
        # El botón que tenía la pantalla vieja: N_G desde lat/lon.
        self.boton_densidad = ttk.Button(cabecera, text="Calcular con lat/lon",
                                         command=self.pedir_densidad)
        self.boton_densidad.grid(row=0, column=3, padx=8)

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

    def pedir_densidad(self):
        """Abre el diálogo de la climatología y deja el N_G que devuelva.

        El diálogo es otra ventana, así que el cambio de N_G no pasa por los
        eventos del editor: hay que avisar a mano.
        """
        self.dialogo = dialogo_densidad.DialogoDensidad(self, self._poner_densidad)
        return self.dialogo

    def _poner_densidad(self, valor):
        self.N_G.poner(valor)
        self.al_cambiar()

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
        for nombre, leer in (("N_G", self.N_G.valor),
                             ("estructura", self.estructura.leer),
                             ("lineas", self.lineas.leer),
                             ("zonas", lambda: self.zonas.leer(tipos=tipos))):
            try:
                partes[nombre] = leer()
            except campos.DatoFaltante as error:
                problemas.append(f"{nombre.capitalize()}:\n{error}")
        if problemas:
            raise campos.DatoFaltante("\n\n".join(problemas))

        return {
            tipo: {
                "estructura": partes["estructura"],
                "lineas": partes["lineas"],
                "zonas": [por_tipo[tipo] for por_tipo in partes["zonas"]],
                "N_G": partes["N_G"],
            }
            for tipo in tipos
        }

    # -- escritura ---------------------------------------------------------

    def poner_caso(self, caso: dict, tipo: int = 1):
        """Abre un caso del formato de casos.cargar_caso().

        Ese formato trae las pérdidas de UN riesgo, así que las pestañas de
        los otros tres quedan en blanco y hay que llenarlas antes de pedir
        esos riesgos. El Paso 48 amplía el formato para guardar los cuatro.
        """
        self.N_G.poner(caso["N_G"])
        self.estructura.poner(caso["estructura"])
        self.lineas.poner(caso["lineas"])
        self.zonas.poner([{tipo: zona} for zona in caso["zonas"]])

    def poner(self, casos: dict):
        """Abre lo que devuelve casos_por_tipo()."""
        alguno = casos[sorted(casos)[0]]
        self.N_G.poner(alguno["N_G"])
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
        for tipo, caso in self.casos_por_tipo(tipos).items():
            resultados[tipo] = riesgos.evaluar(
                caso["estructura"], caso["lineas"], caso["zonas"],
                caso["N_G"], tipos=(tipo,))[tipo]
        return resultados
        
    # -- archivo -----------------------------------------------------------

    def guardar(self, ruta, tipos=(1, 2, 3, 4)) -> str:
        """Escribe el caso en un archivo JSON. Avisa si falta algo antes."""
        return casos.guardar_caso(ruta, self.casos_por_tipo(tipos))

    def abrir(self, ruta):
        """Abre un archivo JSON, del formato que sea."""
        self.poner(casos.cargar_casos(ruta))


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
    if isinstance(widget, ttk.Checkbutton):
        variable = str(widget.cget("variable"))
        return widget.getvar(variable) if variable else None
    return None