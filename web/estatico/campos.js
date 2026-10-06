// Las piezas con que se arman los formularios: la versión web de ventanas/campos.py.
//
//   CampoNumero  casilla de número. Vacía o con basura AVISA; nunca devuelve 0 sola.
//   CampoTexto   casilla de texto, para los nombres.
//   CampoTabla   lista con las filas de una tabla de la norma (el valor viene del servidor).
//   CampoLista   lista con opciones que no son una tabla entera (U_W, blindaje, P_LI).
//   CampoSiNo    casilla de verificación.
//
// Cada campo se dibuja en una fila: rótulo a la izquierda, casilla a la derecha.
// Cuando un dato está mal, el rótulo se pone rojo. recoger() lee un grupo de campos y,
// si falta más de uno, los dice TODOS juntos.

export class DatoFaltante extends Error {}

let contador = 0;

class Campo {
  constructor(contenedor, etiqueta) {
    this.etiqueta = etiqueta;
    this.id = `campo-${++contador}`;
    this.fila = document.createElement("div");
    this.fila.className = "campo";
    const rotulo = document.createElement("label");
    rotulo.htmlFor = this.id;
    rotulo.textContent = etiqueta;
    this.control = document.createElement("span");
    this.control.className = "control";
    this.fila.append(rotulo, this.control);
    contenedor.append(this.fila);
  }

  // Una línea gris debajo de la casilla: qué es el dato y cuándo cambiarlo.
  ayudar(texto) {
    if (!texto) return;
    const ayuda = document.createElement("span");
    ayuda.className = "ayuda";
    ayuda.textContent = texto;
    this.control.append(ayuda);
  }

  marcar(hayError) {
    this.fila.classList.toggle("en-error", hayError);
  }

  fallar(mensaje) {
    this.marcar(true);
    throw new DatoFaltante(mensaje);
  }

  mostrar(visible) {
    this.fila.hidden = !visible;
  }

  // Lo que hay en la casilla tal cual, sin validar: para guardar el borrador.
  foto() {
    if (this.casilla) return this.casilla.checked;
    return (this.entrada || this.select).value;
  }

  ponerFoto(valor) {
    if (valor === undefined) return;
    if (this.casilla) this.casilla.checked = Boolean(valor);
    else (this.entrada || this.select).value = valor;
  }
}

// La foto de un grupo de campos {nombre: campo}, y al revés.
export function fotoDe(campos) {
  return Object.fromEntries(Object.entries(campos).map(([nombre, campo]) => [nombre, campo.foto()]));
}

export function ponerFotoEn(campos, foto = {}) {
  for (const [nombre, campo] of Object.entries(campos)) campo.ponerFoto(foto[nombre]);
}

// Qué fila de la norma se eligió en cada lista: {campo: llave}. Va con el caso guardado
// para que, al abrirlo, se vea la fila que se eligió y no otra con el mismo valor.
export function filasDe(campos) {
  const filas = {};
  for (const [nombre, campo] of Object.entries(campos)) {
    if (campo instanceof CampoTabla && campo.llaveElegida()) filas[nombre] = campo.llaveElegida();
  }
  return filas;
}

export class CampoNumero extends Campo {
  constructor(contenedor, etiqueta, {valor = null, unidad = "", positivo = false,
                                     minimo = null, maximo = null, ayuda = ""} = {}) {
    super(contenedor, etiqueta);
    Object.assign(this, {positivo, minimo, maximo});
    this.entrada = document.createElement("input");
    this.entrada.id = this.id;
    this.entrada.type = "text";
    this.entrada.inputMode = "decimal";
    this.entrada.size = 12;
    this.control.append(this.entrada);
    if (unidad) {
      const u = document.createElement("span");
      u.className = "unidad";
      u.textContent = unidad;
      this.control.append(u);
    }
    if (valor !== null) this.poner(valor);
    this.ayudar(ayuda);
  }

  poner(valor) {
    this.entrada.value = valor === null || valor === undefined ? "" : String(valor).replace(".", ",");
    this.marcar(false);
  }

  soloLectura(si) {
    this.entrada.readOnly = si;
  }

  valor() {
    const crudo = this.entrada.value.trim();
    if (!crudo) this.fallar(`Falta ${this.etiqueta}`);
    const numero = Number(crudo.replace(",", "."));
    if (!Number.isFinite(numero)) this.fallar(`${this.etiqueta}: «${crudo}» no es un número`);
    if (this.positivo && numero <= 0) this.fallar(`${this.etiqueta} tiene que ser mayor que cero`);
    if (this.minimo !== null && numero < this.minimo)
      this.fallar(`${this.etiqueta} no puede ser menor que ${this.minimo}`);
    if (this.maximo !== null && numero > this.maximo)
      this.fallar(`${this.etiqueta} no puede ser mayor que ${this.maximo}`);
    this.marcar(false);
    return numero;
  }
}

export class CampoTexto extends Campo {
  constructor(contenedor, etiqueta, {valor = "", obligatorio = true, ancho = 28} = {}) {
    super(contenedor, etiqueta);
    this.obligatorio = obligatorio;
    this.entrada = document.createElement("input");
    this.entrada.id = this.id;
    this.entrada.type = "text";
    this.entrada.size = ancho;
    this.control.append(this.entrada);
    this.poner(valor);
  }

  poner(valor) {
    this.entrada.value = valor ?? "";
    this.marcar(false);
  }

  crudo() {
    return this.entrada.value.trim();
  }

  valor() {
    const texto = this.crudo();
    if (this.obligatorio && !texto) this.fallar(`Falta ${this.etiqueta}`);
    this.marcar(false);
    return texto;
  }
}

const SIN_ELEGIR = "— elegir —";
const NO_APLICA = "— no aplica —";

function iguales(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function lista(id, marcador, textos) {
  const select = document.createElement("select");
  select.id = id;
  select.add(new Option(marcador, ""));
  textos.forEach((texto, i) => select.add(new Option(texto, String(i))));
  return select;
}

// Arranca SIN NADA ELEGIDO: un factor que el usuario nunca eligió no entra al cálculo
// (si arrancara en la primera fila, C_D quedaría en 0,25 sin que nadie lo viera).
export class CampoTabla extends Campo {
  constructor(contenedor, tabla, etiqueta, {opcional = false, valorVacio = 0} = {}) {
    super(contenedor, etiqueta);
    Object.assign(this, {tabla, opcional, valorVacio});
    this.opciones = tabla.opciones;
    this.select = lista(this.id, opcional ? NO_APLICA : SIN_ELEGIR, this.opciones.map((o) => o.texto));
    this.select.title = tabla.nombre;
    this.control.append(this.select);
  }

  valor() {
    const fila = this.fila_();
    if (fila === "ambiguo") {
      this.marcar(false);
      return this.ambiguo;
    }
    if (fila < 0) {
      if (this.opcional) {
        this.marcar(false);
        return this.valorVacio;
      }
      this.fallar(`Falta elegir: ${this.etiqueta}`);
    }
    this.marcar(false);
    return this.opciones[fila].valor;
  }

  // La llave de la fila elegida, o "" si no hay una fila concreta.
  llaveElegida() {
    const fila = this.fila_();
    return Number.isInteger(fila) && fila >= 0 ? this.opciones[fila].llave : "";
  }

  // Un caso guardado trae el valor y, si se guardó desde la web, también la fila (llave).
  // Sin la fila, y si varias filas de la tabla tienen ese valor, no se adivina: la lista
  // lo dice y pide elegir, y mientras tanto el cálculo usa el valor guardado.
  ponerValor(valor, llave = null) {
    this._quitarAmbiguo();
    if (this.opcional && iguales(valor, this.valorVacio)) {
      this.select.value = "";
      this.marcar(false);
      return;
    }
    const filas = this.opciones.flatMap((o, i) => (iguales(o.valor, valor) ? [i] : []));
    if (!filas.length) {
      this.select.value = "";
      this.fallar(`${this.etiqueta}: ${JSON.stringify(valor)} no es ninguna fila de ${this.tabla.nombre}`);
    }
    const porLlave = filas.find((i) => this.opciones[i].llave === llave);
    if (porLlave !== undefined || filas.length === 1) {
      this.select.value = String(porLlave ?? filas[0]);
    } else {
      this._ponerAmbiguo(valor, filas);
    }
    this.marcar(false);
  }

  _ponerAmbiguo(valor, filas) {
    this.ambiguo = valor;
    const textos = filas.map((i) => this.opciones[i].texto);
    const opcion = new Option(`Valor ${textoDeValor(valor)}: ${textos.join(" o ")} — elija cuál`, "ambiguo");
    this.select.add(opcion, 1);
    this.select.value = "ambiguo";
    this.select.classList.add("por-elegir");
    this.select.addEventListener("change", () => {
      if (this.select.value !== "ambiguo") this._quitarAmbiguo();
    }, {once: true});
  }

  _quitarAmbiguo() {
    this.ambiguo = undefined;
    this.select.querySelector('option[value="ambiguo"]')?.remove();
    this.select.classList.remove("por-elegir");
  }

  fila_() {
    if (this.select.value === "ambiguo") return "ambiguo";
    return this.select.value === "" ? -1 : Number(this.select.value);
  }

  foto() {
    return this.select.value === "ambiguo" ? {ambiguo: this.ambiguo} : this.select.value;
  }

  ponerFoto(valor) {
    if (valor === undefined) return;
    if (valor && typeof valor === "object" && "ambiguo" in valor) {
      try {
        this.ponerValor(valor.ambiguo);
      } catch { /* la tabla cambió: queda sin elegir */ }
      return;
    }
    this._quitarAmbiguo();
    this.select.value = valor;
  }
}

function textoDeValor(valor) {
  if (valor && typeof valor === "object") {
    return Object.entries(valor).map(([k, v]) => `${k} = ${String(v).replace(".", ",")}`).join(", ");
  }
  return String(valor).replace(".", ",");
}

export class CampoLista extends Campo {
  constructor(contenedor, etiqueta, opciones) {
    super(contenedor, etiqueta);
    this.opciones = opciones;            // [{texto, valor}]
    this.select = lista(this.id, SIN_ELEGIR, opciones.map((o) => o.texto));
    this.control.append(this.select);
  }

  valor() {
    if (this.select.value === "") this.fallar(`Falta elegir: ${this.etiqueta}`);
    this.marcar(false);
    return this.opciones[Number(this.select.value)].valor;
  }

  poner(valor) {
    const fila = this.opciones.findIndex((o) => iguales(o.valor, valor));
    if (fila < 0) this.fallar(`${this.etiqueta}: ${valor} no es una opción válida`);
    this.select.value = String(fila);
    this.marcar(false);
  }
}

export class CampoSiNo extends Campo {
  constructor(contenedor, etiqueta, {valor = false, ayuda = ""} = {}) {
    super(contenedor, etiqueta);
    this.casilla = document.createElement("input");
    this.casilla.type = "checkbox";
    this.casilla.id = this.id;
    this.control.append(this.casilla);
    this.poner(valor);
    this.ayudar(ayuda);
  }

  valor() {
    return this.casilla.checked;
  }

  poner(valor) {
    this.casilla.checked = Boolean(valor);
  }
}

// Lee todos los campos; si falta algo, los junta TODOS en un solo aviso.
export function recoger(campos) {
  const valores = {};
  const problemas = [];
  for (const [nombre, campo] of Object.entries(campos)) {
    try {
      valores[nombre] = campo.valor();
    } catch (error) {
      if (!(error instanceof DatoFaltante)) throw error;
      problemas.push(error.message);
    }
  }
  if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
  return valores;
}

// Corre varias lecturas y junta lo que falte de todas, con su encabezado.
export function juntar(partes) {
  const valores = {};
  const problemas = [];
  for (const [nombre, [encabezado, leer]] of Object.entries(partes)) {
    try {
      valores[nombre] = leer();
    } catch (error) {
      if (!(error instanceof DatoFaltante)) throw error;
      problemas.push(encabezado ? `${encabezado}:\n${error.message}` : error.message);
    }
  }
  if (problemas.length) throw new DatoFaltante(problemas.join("\n\n"));
  return valores;
}
