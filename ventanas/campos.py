"""
Tres piezas, y la pantalla entera se arma con ellas:

  CampoNumero  una casilla de número. Si está vacía o tiene basura, AVISA;
               nunca devuelve 0 por su cuenta. Ese es el error que hoy está
               vivo en la pantalla vieja: si la casilla de la densidad de
               descargas no se puede leer, el programa calcula con N_G = 0
               y da riesgo cero sin decir nada.
  CampoTabla   una lista desplegable armada desde una tabla de tablas.py.
               El texto lo pone etiquetas.py; el valor sale de la tabla.
  CampoSiNo    una casilla de verificación para las banderas del modelo.

Los tres se dibujan solos en la fila que se les diga del padre, con el
rótulo en la columna 0. Cuando un dato está mal, el rótulo se pone rojo, que
es lo único que se ve igual en todos los temas de ttk.

recoger() lee un grupo de campos de una vez y, si falta más de uno, los
reporta TODOS juntos en vez de uno por uno.
"""
from tkinter import ttk
import tkinter as tk

from calculate_risk.norma import etiquetas

ROJO = "#c0392b"


class DatoFaltante(ValueError):
    """Una casilla está vacía, tiene basura o el número está fuera de rango."""


class _Campo:
    """Lo común: el rótulo de la izquierda y la marca de error."""

    def __init__(self, padre, etiqueta, fila):
        self.etiqueta = etiqueta
        self.rotulo = ttk.Label(padre, text=etiqueta)
        self.rotulo.grid(row=fila, column=0, padx=5, pady=2, sticky="w")

    def marcar(self, hay_error: bool):
        self.rotulo.configure(foreground=ROJO if hay_error else "")

    @property
    def en_error(self) -> bool:
        return str(self.rotulo.cget("foreground")) == ROJO


class CampoNumero(_Campo):
    """Casilla de número. Acepta coma o punto como separador decimal."""

    def __init__(self, padre, etiqueta, fila, valor=None, unidad="", positivo=False,
                 minimo=None, maximo=None, ancho=12):
        super().__init__(padre, etiqueta, fila)
        self.positivo = positivo
        self.minimo = minimo
        self.maximo = maximo
        self.entrada = ttk.Entry(padre, width=ancho)
        self.entrada.grid(row=fila, column=1, padx=3, pady=2, sticky="w")
        if unidad:
            ttk.Label(padre, text=unidad).grid(row=fila, column=2, sticky="w")
        if valor is not None:
            self.poner(valor)

    def poner(self, valor):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, str(valor))
        self.marcar(False)

    def valor(self) -> float:
        crudo = self.entrada.get().strip()
        if not crudo:
            self._fallar(f"Falta {self.etiqueta}")
        try:
            numero = float(crudo.replace(",", "."))
        except ValueError:
            self._fallar(f"{self.etiqueta}: «{crudo}» no es un número")
        if self.positivo and numero <= 0:
            self._fallar(f"{self.etiqueta} tiene que ser mayor que cero")
        if self.minimo is not None and numero < self.minimo:
            self._fallar(f"{self.etiqueta} no puede ser menor que {self.minimo}")
        if self.maximo is not None and numero > self.maximo:
            self._fallar(f"{self.etiqueta} no puede ser mayor que {self.maximo}")
        self.marcar(False)
        return numero

    def _fallar(self, mensaje):
        self.marcar(True)
        raise DatoFaltante(mensaje)


class CampoTexto(_Campo):
    """Casilla de texto, para los nombres (de la zona, de la línea…).

    Un nombre en blanco no rompe el cálculo, pero sí el informe y el árbol
    del caso, donde la zona quedaría sin cómo llamarse. Por eso también avisa.
    """

    def __init__(self, padre, etiqueta, fila, valor="", ancho=28, obligatorio=True):
        super().__init__(padre, etiqueta, fila)
        self.obligatorio = obligatorio
        self.entrada = ttk.Entry(padre, width=ancho)
        self.entrada.grid(row=fila, column=1, columnspan=2, padx=3, pady=2, sticky="w")
        self.poner(valor)

    def poner(self, valor):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, str(valor))
        self.marcar(False)

    def valor(self) -> str:
        texto = self.entrada.get().strip()
        if self.obligatorio and not texto:
            self.marcar(True)
            raise DatoFaltante(f"Falta {self.etiqueta}")
        self.marcar(False)
        return texto


class CampoTabla(_Campo):
    """Lista desplegable con las filas de una tabla de la norma.

    El valor NUNCA se escribe aquí: sale de tablas.py a través de
    etiquetas.opciones(). Con CLD_CLI el valor es el par {"CLD":…, "CLI":…}.

    Arranca SIN NADA ELEGIDO y, si no se elige, avisa igual que una casilla
    numérica vacía. No es un capricho: si arrancara en la primera fila, la
    Tabla A.1 dejaría C_D = 0,25 puesto solo, que es la fila más favorable y
    da cuatro veces menos N_D que la casa rural del Anexo E. Un factor que el
    usuario nunca eligió no puede entrar en el cálculo. Con inicial="llave"
    se puede arrancar en una fila concreta cuando sí se sabe cuál va.
    """

    SIN_ELEGIR = "— elegir —"
    NO_APLICA = "— no aplica —"

    def __init__(self, padre, tabla, fila, etiqueta=None, inicial=None, ancho=52,
                 opcional=False, valor_vacio=0):
        super().__init__(padre, etiqueta or etiquetas.NOMBRES[tabla][1], fila)
        self.tabla = tabla
        self.opcional = opcional
        self.valor_vacio = valor_vacio
        self.textos = [texto for texto, _ in etiquetas.opciones(tabla)]
        self.valores = [valor for _, valor in etiquetas.opciones(tabla)]
        self.llaves = etiquetas.llaves(tabla)

        marcador = self.NO_APLICA if opcional else self.SIN_ELEGIR
        self.combo = ttk.Combobox(padre, state="readonly", width=ancho,
                                  values=[marcador] + self.textos)
        self.combo.grid(row=fila, column=1, columnspan=2, padx=3, pady=2, sticky="w")
        self.combo.current(0)
        if inicial is not None:
            self.poner_llave(inicial)

    def _fila_elegida(self) -> int:
        """Índice en la tabla, o -1 si todavía no se ha elegido nada."""
        return self.combo.current() - 1

    def valor(self):
        fila = self._fila_elegida()
        if fila < 0:
            if self.opcional:
                # "No aplica" es una respuesta, no un olvido: hay zonas sin
                # servicio publico, sin patrimonio y sin sistemas vitales.
                self.marcar(False)
                return self.valor_vacio
            self.marcar(True)
            raise DatoFaltante(f"Falta elegir: {self.etiqueta}")
        self.marcar(False)
        return self.valores[fila]


    def llave(self) -> str:
        fila = self._fila_elegida()
        if fila < 0:
            self.marcar(True)
            raise DatoFaltante(f"Falta elegir: {self.etiqueta}")
        return self.llaves[fila]

    def poner_llave(self, llave: str):
        self.combo.current(self.llaves.index(llave) + 1)
        self.marcar(False)

    def poner_valor(self, valor):
        """Selecciona la primera fila que tenga ese valor.

        Es lo que hace falta al abrir un caso guardado, porque el caso
        guarda el valor, no la fila. Si dos filas comparten valor (pasa en
        las Tablas B.1 y C.5) queda la primera: el cálculo es el mismo, solo
        puede cambiar el texto que se muestra. Si ninguna fila lo tiene, avisa
        — eso significa que el caso trae un valor que no está en la norma.
        """
        if self.opcional and valor == self.valor_vacio:
            self.combo.current(0)
            self.marcar(False)
            return
        for indice, candidato in enumerate(self.valores):


        for indice, candidato in enumerate(self.valores):
            if candidato == valor:
                self.combo.current(indice + 1)
                self.marcar(False)
                return
        self.marcar(True)
        raise DatoFaltante(
            f"{self.etiqueta}: {valor} no es ninguna fila de "
            f"{etiquetas.NOMBRES[self.tabla][0]}"
        )

class CampoSiNo(_Campo):
    """Casilla de verificación, para las banderas del modelo."""

    def __init__(self, padre, etiqueta, fila, valor=False):
        super().__init__(padre, etiqueta, fila)
        self.marca = tk.BooleanVar(value=bool(valor))
        self.casilla = ttk.Checkbutton(padre, variable=self.marca)
        self.casilla.grid(row=fila, column=1, padx=3, pady=2, sticky="w")

    def valor(self) -> bool:
        return bool(self.marca.get())

    def poner(self, valor):
        self.marca.set(bool(valor))


def recoger(campos: dict) -> dict:
    """Lee todos los campos y devuelve {nombre: valor}.

    Si falta algo, los junta TODOS en un solo aviso: al usuario le sirve más
    ver de una vez los cuatro datos que le faltan que descubrirlos uno a uno.
    """
    valores = {}
    problemas = []
    for nombre, campo in campos.items():
        try:
            valores[nombre] = campo.valor()
        except DatoFaltante as error:
            problemas.append(str(error))
    if problemas:
        raise DatoFaltante("\n".join(problemas))
    return valores