// Los formularios de la calculadora: la versión web de ventanas/formularios.py,
// ventanas/listas.py y ventanas/emplazamiento.py.
//
// Cada formulario pregunta EXACTAMENTE los campos de la dataclass del motor, con los
// mismos rótulos del programa de escritorio. Las listas desplegables se arman con el
// esquema que manda el servidor (tablas.py + etiquetas.py): aquí no hay ni un número
// de la norma escrito a mano. Todos tienen leer() y poner(); los que van en una lista,
// además nombre() y raiz (el elemento que se muestra u oculta).

import {CampoLista, CampoNumero, CampoSiNo, CampoTabla, CampoTexto, DatoFaltante,
        filasDe, fotoDe, juntar, ponerFotoEn, recoger} from "./campos.js";

let E = null;                       // el esquema de /api/esquema
export function configurar(esquema) {
  E = esquema;
}

const D = (clase) => E.por_defecto[clase];
const T = (tabla) => E.tablas[tabla];

export const TITULOS_PESTANA = {1: "R1 Vidas humanas", 2: "R2 Servicio público",
                                3: "R3 Patrimonio", 4: "R4 Económica"};

function marco(contenedor, titulo) {
  const fieldset = document.createElement("fieldset");
  const legend = document.createElement("legend");
  legend.textContent = titulo;
  fieldset.append(legend);
  contenedor.append(fieldset);
  return fieldset;
}

function ponerEn(campo, valor, llave) {
  if (campo instanceof CampoTabla) campo.ponerValor(valor, llave);
  else campo.poner(valor);
}

// Pone cada valor en su campo y, si alguno no está en la norma, los dice todos.
function ponerTodos(campos, objeto) {
  const problemas = [];
  for (const [nombre, campo] of Object.entries(campos)) {
    try {
      ponerEn(campo, objeto[nombre], objeto._filas?.[nombre]);
    } catch (error) {
      if (!(error instanceof DatoFaltante)) throw error;
      problemas.push(error.message);
    }
  }
  if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
}

// --- Pestañas ------------------------------------------------------------------

export function pestanas(contenedor, titulos) {
  const caja = document.createElement("div");
  caja.className = "pestanas";
  const barra = document.createElement("div");
  barra.className = "pestanas-barra";
  barra.setAttribute("role", "tablist");
  caja.append(barra);
  const paneles = titulos.map((titulo, i) => {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = titulo;
    boton.setAttribute("role", "tab");
    boton.addEventListener("click", () => elegir(i));
    barra.append(boton);
    const panel = document.createElement("div");
    panel.className = "pestanas-panel";
    panel.setAttribute("role", "tabpanel");
    caja.append(panel);
    return {boton, panel};
  });
  function elegir(i) {
    paneles.forEach((p, j) => {
      p.boton.setAttribute("aria-selected", String(i === j));
      p.panel.hidden = i !== j;
    });
  }
  elegir(0);
  contenedor.append(caja);
  return {paneles: paneles.map((p) => p.panel), elegir};
}

// --- Estructura -----------------------------------------------------------------

// L, W y H no traen valor inicial a propósito: son los únicos que la dataclass exige.
export class FormularioEstructura {
  constructor(contenedor, titulo = "Estructura") {
    const d = D("Estructura");
    const m = marco(contenedor, titulo);
    this.raiz = m;
    this.campos = {
      L: new CampoNumero(m, "Longitud (L)", {unidad: "m", positivo: true}),
      W: new CampoNumero(m, "Ancho (W)", {unidad: "m", positivo: true}),
      H: new CampoNumero(m, "Altura (H)", {unidad: "m", positivo: true}),
      H_p: new CampoNumero(m, "Altura del saliente del techo (H_p)",
                           {valor: d.H_p, unidad: "m", minimo: 0}),
      C_D: new CampoTabla(m, T("CD"), "Localización (C_D)"),
      n_t: new CampoNumero(m, "Personas en la estructura (n_t)", {valor: d.n_t, minimo: 0}),
      c_t: new CampoNumero(m, "Valor total de la estructura (c_t)",
                           {valor: d.c_t, minimo: 0, unidad: "para R4"}),
      riesgo_explosion_o_vital: new CampoSiNo(m, "Riesgo de explosión o sistemas vitales",
                                              {valor: d.riesgo_explosion_o_vital}),
      hay_animales: new CampoSiNo(m, "Hay animales", {valor: d.hay_animales}),
    };
  }

  leer() {
    return recoger(this.campos);
  }

  poner(estructura) {
    ponerTodos(this.campos, estructura);
  }

  foto() {
    return fotoDe(this.campos);
  }

  ponerFoto(foto) {
    ponerFotoEn(this.campos, foto);
  }

  filas() {
    return filasDe(this.campos);
  }
}

// --- Sistemas internos ----------------------------------------------------------

// P_DPS sale de la Tabla B.3 por su cuenta, no deducido del nivel del SPCR (H17).
export class FormularioSistemaInterno {
  constructor(contenedor, titulo = "Sistema interno") {
    const d = D("SistemaInterno");
    const m = marco(contenedor, titulo);
    this.raiz = m;
    this.campos = {
      nombre: new CampoTexto(m, "Nombre"),
      linea: new CampoTexto(m, "Lo alimenta la línea", {valor: d.linea, obligatorio: false}),
      K_S3: new CampoTabla(m, T("KS3"), "Cableado interno (K_S3)"),
      U_W: new CampoNumero(m, "Tensión soportada (U_W)", {valor: d.U_W, unidad: "kV", positivo: true}),
      P_DPS: new CampoTabla(m, T("PDPS"), "DPS coordinado (P_DPS)"),
    };
  }

  nombre() {
    return this.campos.nombre.crudo();
  }

  leer() {
    return recoger(this.campos);
  }

  poner(sistema) {
    ponerTodos(this.campos, sistema);
  }

  foto() {
    return fotoDe(this.campos);
  }

  ponerFoto(foto) {
    ponerFotoEn(this.campos, foto);
  }

  filas() {
    return filasDe(this.campos);
  }
}

// --- Lista de formularios (zonas, líneas, sistemas internos) --------------------

export class ListaDeFormularios {
  constructor(contenedor, fabrica, {titulo = "Elementos", singular = "elemento", minimo = 0} = {}) {
    Object.assign(this, {fabrica, singular, minimo});
    this.formularios = [];
    const m = marco(contenedor, titulo);
    this.raiz = m;
    const doble = document.createElement("div");
    doble.className = "lista-doble";
    m.append(doble);

    const izquierda = document.createElement("div");
    izquierda.className = "lista-izquierda";
    this.lista = document.createElement("select");
    this.lista.size = 5;
    this.lista.addEventListener("change", () => this.mostrarSeleccionado());
    const botones = document.createElement("div");
    botones.className = "lista-botones";
    const mayuscula = singular[0].toUpperCase() + singular.slice(1);
    this.botonAnadir = this._boton(botones, `+ ${mayuscula}`, () => this.anadir());
    this.botonQuitar = this._boton(botones, `− ${mayuscula}`, () => this.pedirQuitar());
    // Un botón apagado sin explicación es otra forma de no decir nada.
    this.razonQuitar = document.createElement("div");
    this.razonQuitar.className = "pequeno";
    izquierda.append(this.lista, botones, this.razonQuitar);

    this.zonaFormulario = document.createElement("div");
    this.zonaFormulario.className = "lista-derecha";
    // Los nombres de la lista siguen lo que se escribe en el formulario.
    this.zonaFormulario.addEventListener("input", () => this.refrescarNombres());
    doble.append(izquierda, this.zonaFormulario);
    this._actualizarBotones();
  }

  _boton(padre, texto, accion) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = texto;
    boton.addEventListener("click", accion);
    padre.append(boton);
    return boton;
  }

  anadir(objeto = null) {
    const formulario = this.fabrica(this.zonaFormulario);
    this.formularios.push(formulario);
    this.refrescarNombres();
    this.lista.value = String(this.formularios.length - 1);
    this.mostrarSeleccionado();
    try {
      if (objeto !== null) formulario.poner(objeto);
    } finally {
      this.refrescarNombres();
      this.zonaFormulario.dispatchEvent(new Event("change", {bubbles: true}));
    }
    return formulario;
  }

  seleccionado() {
    return this.lista.value === "" ? null : Number(this.lista.value);
  }

  razonParaNoQuitar() {
    if (!this.formularios.length) return "No hay nada que quitar.";
    if (this.formularios.length <= this.minimo)
      return `Tiene que quedar al menos ${this.minimo} ${this.singular}.`;
    if (this.seleccionado() === null) return `Elige en la lista qué ${this.singular} quitar.`;
    return "";
  }

  pedirQuitar() {
    const razon = this.razonParaNoQuitar();
    if (razon) {
      alert(razon);
      return;
    }
    const indice = this.seleccionado();
    this.formularios.splice(indice, 1)[0].raiz.remove();
    this.refrescarNombres();
    if (this.formularios.length) this.lista.value = String(Math.min(indice, this.formularios.length - 1));
    this.mostrarSeleccionado();
    this.zonaFormulario.dispatchEvent(new Event("change", {bubbles: true}));
  }

  mostrarSeleccionado() {
    const indice = this.seleccionado();
    this.formularios.forEach((f, i) => { f.raiz.hidden = i !== indice; });
    this._actualizarBotones();
  }

  _actualizarBotones() {
    const razon = this.razonParaNoQuitar();
    this.botonQuitar.disabled = Boolean(razon);
    this.razonQuitar.textContent = razon;
  }

  nombres() {
    return this.formularios.map((f) => f.nombre() || `(${this.singular} sin nombre)`);
  }

  refrescarNombres() {
    const seleccion = this.lista.value;
    this.lista.replaceChildren(...this.nombres().map((n, i) => new Option(n, String(i))));
    if (seleccion !== "" && Number(seleccion) < this.formularios.length) this.lista.value = seleccion;
  }

  // Lee todos; si falta algo, junta todo en un aviso («Zona 2: ...»).
  leer(...argumentos) {
    const objetos = [];
    const problemas = [];
    const mayuscula = this.singular[0].toUpperCase() + this.singular.slice(1);
    this.formularios.forEach((formulario, i) => {
      try {
        objetos.push(formulario.leer(...argumentos));
      } catch (error) {
        if (!(error instanceof DatoFaltante)) throw error;
        problemas.push(`${mayuscula} ${i + 1}:\n${error.message}`);
      }
    });
    if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
    if (objetos.length < this.minimo)
      throw new DatoFaltante(`Hace falta al menos ${this.minimo} ${this.singular}`);
    return objetos;
  }

  // Deja la lista con exactamente estos elementos.
  poner(objetos) {
    this.formularios.forEach((f) => f.raiz.remove());
    this.formularios = [];
    const problemas = [];
    objetos.forEach((objeto, i) => {
      try {
        this.anadir(objeto);
      } catch (error) {
        if (!(error instanceof DatoFaltante)) throw error;
        problemas.push(`${this.singular} ${i + 1}: ${error.message}`);
      }
    });
    if (this.formularios.length) this.lista.value = "0";
    this.mostrarSeleccionado();
    if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
  }

  foto() {
    return this.formularios.map((f) => f.foto());
  }

  filas(...argumentos) {
    return this.formularios.map((f) => f.filas(...argumentos));
  }

  ponerFoto(fotos = []) {
    this.formularios.forEach((f) => f.raiz.remove());
    this.formularios = [];
    for (const foto of fotos) this.anadir().ponerFoto(foto);
    this.refrescarNombres();
    if (this.formularios.length) this.lista.value = "0";
    this.mostrarSeleccionado();
  }
}

// --- Zona -------------------------------------------------------------------------

// Lo común a los cuatro riesgos. K_S1 y K_S2 no se eligen de una lista: son
// K_S = 0,12 × w_m (ec. B.5 y B.6), así que se pregunta el ancho de la malla.
class FormularioZonaComun {
  constructor(contenedor, titulo) {
    const d = D("Zona");
    const m = marco(contenedor, titulo);
    this.campos = {
      nombre: new CampoTexto(m, "Nombre de la zona"),
      P_TA: new CampoTabla(m, T("PTA"), "Tensiones de paso y contacto (P_TA)"),
      P_B: new CampoTabla(m, T("PB"), "Protección contra daño físico (P_B)"),
      P_TU: new CampoTabla(m, T("PTU"), "Tensiones de contacto por línea (P_TU)"),
      r_t: new CampoTabla(m, T("N_SUPERFICIE"), "Superficie del piso (r_t)"),
      r_p: new CampoTabla(m, T("RP"), "Medidas contra incendio (r_p)"),
      r_f: new CampoTabla(m, T("RF"), "Riesgo de incendio (r_f)"),
      n_z: new CampoNumero(m, "Personas o usuarios en la zona (n_z)", {valor: d.n_z, minimo: 0}),
      t_z: new CampoNumero(m, "Horas al año de presencia (t_z)",
                           {valor: d.t_z, minimo: 0, maximo: 8760, unidad: "h"}),
      exterior_sin_personas: new CampoSiNo(m, "Zona exterior sin personas (anula R_A y R_U)",
                                           {valor: d.exterior_sin_personas}),
    };
    this.blindaje = new CampoSiNo(m, "Hay apantallamiento espacial");
    this.w_m1 = new CampoNumero(m, "Ancho de la malla exterior (w_m1)", {unidad: "m", positivo: true});
    this.w_m2 = new CampoNumero(m, "Ancho de la malla interior (w_m2)", {unidad: "m", positivo: true});
    this.blindaje.casilla.addEventListener("change", () => this._verMalla());
    this._verMalla();
  }

  _verMalla() {
    const si = this.blindaje.valor();
    this.w_m1.mostrar(si);
    this.w_m2.mostrar(si);
  }

  leer() {
    const d = D("Zona");
    const f = E.constantes.FACTOR_MALLA;
    const grupo = {...this.campos};
    if (this.blindaje.valor()) Object.assign(grupo, {w_m1: this.w_m1, w_m2: this.w_m2});
    const valores = recoger(grupo);
    if (this.blindaje.valor()) {
      valores.K_S1 = Math.min(f * valores.w_m1, 1);
      valores.K_S2 = Math.min(f * valores.w_m2, 1);
      delete valores.w_m1;
      delete valores.w_m2;
    } else {
      valores.K_S1 = d.K_S1;
      valores.K_S2 = d.K_S2;
    }
    return valores;
  }

  poner(zona) {
    ponerTodos(this.campos, zona);
    const d = D("Zona");
    const hay = zona.K_S1 !== d.K_S1 || zona.K_S2 !== d.K_S2;
    this.blindaje.poner(hay);
    if (hay) {
      this.w_m1.poner(zona.K_S1 / E.constantes.FACTOR_MALLA);
      this.w_m2.poner(zona.K_S2 / E.constantes.FACTOR_MALLA);
    }
    this._verMalla();
  }

  _todos() {
    return {...this.campos, blindaje: this.blindaje, w_m1: this.w_m1, w_m2: this.w_m2};
  }

  foto() {
    return fotoDe(this._todos());
  }

  ponerFoto(foto) {
    ponerFotoEn(this._todos(), foto);
    this._verMalla();
  }

  filas() {
    return filasDe(this.campos);
  }
}

// Las pérdidas de una zona para UN riesgo. Lo que no aplica se deja en «no aplica» y
// vale 0: una zona puede no prestar servicio público, y eso es una respuesta.
class PestanaPerdidas {
  constructor(m, tipo) {
    const d = D("Zona");
    const c = E.constantes;
    this.campos = {};
    this.banderas = {};
    if (tipo === 1) {
      this.campos.L_T = new CampoNumero(m, "Pérdida por lesiones (L_T)", {
        valor: c.LT_L1, minimo: 0, maximo: 1,
        ayuda: "Ya trae el valor típico de la Tabla C.2 (0,01), que vale para cualquier " +
               "estructura. Déjelo así salvo que tenga un dato propio."});
      this.campos.L_F = new CampoTabla(m, T("LF_L1"), "Pérdida por daño físico (L_F)", {opcional: true});
      this.campos.L_O = new CampoTabla(m, T("LO_L1"), "Pérdida por falla de sistemas (L_O)", {opcional: true});
      this.campos.h_z = new CampoTabla(m, T("HZ"), "Daño especial (h_z)");
      this.campos.t_e = new CampoNumero(m, "Horas al año con personas en peligro afuera (t_e)", {
        valor: d.t_e, minimo: 0, maximo: 8760, unidad: "h",
        ayuda: "Solo si un daño en la estructura pone en peligro a gente de afuera " +
               "(explosión, emisiones tóxicas). Si no, déjelo en 0."});
      this.campos.L_FE = new CampoNumero(m, "Pérdida típica por daño físico fuera (L_FE)", {
        valor: d.L_FE, minimo: 0, maximo: 1,
        ayuda: "Solo cuenta si t_e es mayor que 0. Si no se conoce, la norma usa 1."});
    } else if (tipo === 2) {
      this.campos.L_F = new CampoTabla(m, T("LF_L2"), "Pérdida por daño físico (L_F)", {opcional: true});
      this.campos.L_O = new CampoTabla(m, T("LO_L2"), "Pérdida por falla de sistemas (L_O)", {opcional: true});
    } else if (tipo === 3) {
      this.banderas.L_F = [new CampoSiNo(m, "Hay patrimonio cultural irremplazable"), c.LF_L3];
      this.campos.c_z = new CampoNumero(m, "Valor del patrimonio en la zona (c_z)", {valor: d.c_z, minimo: 0});
    } else {
      this.banderas.L_T = [new CampoSiNo(m, "Hay animales en la zona"), c.LT_L4];
      this.campos.L_F = new CampoTabla(m, T("LF_L4"), "Pérdida por daño físico (L_F)", {opcional: true});
      this.campos.L_O = new CampoTabla(m, T("LO_L4"), "Pérdida por falla de sistemas (L_O)", {opcional: true});
      this.campos.c_a = new CampoNumero(m, "Valor de los animales (c_a)", {valor: d.c_a, minimo: 0});
      this.campos.c_b = new CampoNumero(m, "Valor del edificio (c_b)", {valor: d.c_b, minimo: 0});
      this.campos.c_c = new CampoNumero(m, "Valor del contenido (c_c)", {valor: d.c_c, minimo: 0});
      this.campos.c_s = new CampoNumero(m, "Valor de los sistemas internos (c_s)", {valor: d.c_s, minimo: 0});
      this.campos.c_e = new CampoNumero(m, "Valor de los bienes en sitios peligrosos fuera (c_e)",
                                        {valor: d.c_e, minimo: 0});
      this.campos.L_FE = new CampoNumero(m, "Pérdida típica por daño físico fuera (L_FE)", {
        valor: d.L_FE, minimo: 0, maximo: 1,
        ayuda: "Solo cuenta si c_e es mayor que 0. Si no se conoce, la norma usa 1."});
      // Nota «a» de la Tabla C.11. Arranca en SÍ, como en la pantalla del programa.
      this.campos.razones_l4_unitarias = new CampoSiNo(
        m, "Comparar R4 contra el valor representativo (nota «a», Tabla C.11)", {
          valor: true,
          ayuda: "Déjelo marcado si no va a hacer el análisis de costo-beneficio del Anexo D."});
    }
  }

  leer() {
    const valores = recoger(this.campos);
    for (const [nombre, [bandera, valorSi]] of Object.entries(this.banderas)) {
      valores[nombre] = bandera.valor() ? valorSi : 0;
    }
    return valores;
  }

  poner(zona) {
    ponerTodos(this.campos, zona);
    for (const [nombre, [bandera, valorSi]] of Object.entries(this.banderas)) {
      bandera.poner(zona[nombre] === valorSi);
    }
  }

  _todos() {
    const banderas = Object.fromEntries(Object.entries(this.banderas).map(([n, [b]]) => [`bandera_${n}`, b]));
    return {...this.campos, ...banderas};
  }

  foto() {
    return fotoDe(this._todos());
  }

  ponerFoto(foto) {
    ponerFotoEn(this._todos(), foto);
  }

  filas() {
    return filasDe(this.campos);
  }
}

// La zona completa: lo común arriba y una pestaña por riesgo abajo, más sus sistemas.
export class FormularioZona {
  constructor(contenedor, titulo = "Zona") {
    this.raiz = document.createElement("div");
    contenedor.append(this.raiz);
    this.comun = new FormularioZonaComun(this.raiz, titulo);
    const p = pestanas(this.raiz, [...Object.values(TITULOS_PESTANA), "Sistemas internos"]);
    this.pestanas = {};
    [1, 2, 3, 4].forEach((tipo, i) => {
      this.pestanas[tipo] = new PestanaPerdidas(p.paneles[i], tipo);
    });
    this.sistemas = new ListaDeFormularios(p.paneles[4], (c) => new FormularioSistemaInterno(c),
                                           {titulo: "Sistemas internos de la zona", singular: "sistema"});
  }

  nombre() {
    return this.comun.campos.nombre.crudo();
  }

  // {comun, perdidas: {tipo: {...}}}. Solo se miran las pestañas de los riesgos pedidos.
  leer(tipos = [1, 2, 3, 4]) {
    const partes = {
      sistemas: ["Sistemas internos", () => this.sistemas.leer()],
      comun: ["", () => this.comun.leer()],
    };
    for (const tipo of tipos) partes[tipo] = [TITULOS_PESTANA[tipo], () => this.pestanas[tipo].leer()];
    const v = juntar(partes);
    const perdidas = {};
    for (const tipo of tipos) perdidas[tipo] = v[tipo];
    return {comun: {...v.comun, sistemas_internos: v.sistemas}, perdidas};
  }

  // Desde {tipo: zona}; lo común sale de la primera.
  poner(zonas) {
    const tipos = Object.keys(zonas).map(Number).sort();
    const primera = zonas[tipos[0]];
    const problemas = [];
    const intentar = (f) => {
      try {
        f();
      } catch (error) {
        if (!(error instanceof DatoFaltante)) throw error;
        problemas.push(error.message);
      }
    };
    intentar(() => this.comun.poner(primera));
    intentar(() => this.sistemas.poner(primera.sistemas_internos || []));
    for (const tipo of tipos) intentar(() => this.pestanas[tipo].poner(zonas[tipo]));
    if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
  }

  foto() {
    return {
      comun: this.comun.foto(),
      perdidas: Object.fromEntries([1, 2, 3, 4].map((t) => [t, this.pestanas[t].foto()])),
      sistemas: this.sistemas.foto(),
    };
  }

  ponerFoto(foto) {
    this.comun.ponerFoto(foto.comun);
    for (const t of [1, 2, 3, 4]) this.pestanas[t].ponerFoto(foto.perdidas?.[t]);
    this.sistemas.ponerFoto(foto.sistemas);
  }

  filas(tipos = [1, 2, 3, 4]) {
    return {
      comun: this.comun.filas(),
      perdidas: Object.fromEntries(tipos.map((t) => [String(t), this.pestanas[t].filas()])),
      sistemas: this.sistemas.filas(),
    };
  }
}

// --- Línea --------------------------------------------------------------------------

// La estructura del extremo lejano (ec. A.5): solo sus dimensiones.
class FormularioAdyacente {
  constructor(contenedor) {
    const d = D("Estructura");
    const m = marco(contenedor, "Estructura del extremo lejano");
    this.raiz = m;
    this.campos = {
      L: new CampoNumero(m, "Longitud (L)", {unidad: "m", positivo: true}),
      W: new CampoNumero(m, "Ancho (W)", {unidad: "m", positivo: true}),
      H: new CampoNumero(m, "Altura (H)", {unidad: "m", positivo: true}),
      H_p: new CampoNumero(m, "Altura del saliente (H_p)", {valor: d.H_p, unidad: "m", minimo: 0}),
    };
  }

  poner(estructura) {
    for (const [nombre, campo] of Object.entries(this.campos)) campo.poner(estructura[nombre]);
  }
}

const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// P_LD y P_LI no se escriben: salen de las Tablas B.8 y B.9 con el blindaje o el tipo
// de línea y la tensión soportada U_W.
export class FormularioLinea {
  constructor(contenedor, titulo = "Línea") {
    const d = D("Linea");
    this.raiz = document.createElement("div");
    contenedor.append(this.raiz);
    const m = marco(this.raiz, titulo);
    const doble = E.doble_entrada;
    this.campos = {
      nombre: new CampoTexto(m, "Nombre de la línea"),
      L_L: new CampoNumero(m, "Longitud de la sección (L_L)", {valor: d.L_L, unidad: "m", positivo: true}),
      C_I: new CampoTabla(m, T("CI"), "Instalación (C_I)"),
      C_T: new CampoTabla(m, T("CT"), "Tipo de línea (C_T)"),
      C_E: new CampoTabla(m, T("CE"), "Entorno (C_E)"),
      U_W: new CampoLista(m, "Tensión soportada del equipo (U_W)",
                          E.tensiones.map((u) => ({texto: `${String(u).replace(".", ",")} kV`, valor: u}))),
      P_EB: new CampoTabla(m, T("PEB"), "Equipotencialización con DPS (P_EB)"),
    };
    this.derivados = {
      cld_cli: new CampoTabla(m, T("CLD_CLI"), "Blindaje y puesta a tierra (C_LD y C_LI)"),
      blindaje: new CampoLista(m, "Conexión del blindaje (P_LD)",
                               doble.PLD.opciones.map((o) => ({texto: o.texto, valor: o.llave}))),
      tipo_linea: new CampoLista(m, "Servicio que transporta (P_LI)",
                                 doble.PLI.opciones.map((o) => ({texto: o.texto, valor: o.llave}))),
    };
    this.hayAdyacente = new CampoSiNo(m, "La línea llega a otra estructura (N_DJ)");
    this.C_DJ = new CampoTabla(m, T("CD"), "Localización de esa estructura (C_DJ)");
    this.adyacente = new FormularioAdyacente(this.raiz);
    this.hayAdyacente.casilla.addEventListener("change", () => this._verAdyacente());
    this._verAdyacente();
  }

  _verAdyacente() {
    const si = this.hayAdyacente.valor();
    this.C_DJ.mostrar(si);
    this.adyacente.raiz.hidden = !si;
  }

  nombre() {
    return this.campos.nombre.crudo();
  }

  leer() {
    const grupo = {...this.campos, ...this.derivados};
    const partes = {valores: ["", () => recoger(grupo)]};
    if (this.hayAdyacente.valor()) {
      // Las medidas de la vecina y su C_DJ se piden juntas, para que falten juntas.
      partes.vecina = ["", () => recoger({...this.adyacente.campos, C_DJ: this.C_DJ})];
    }
    const {valores, vecina} = juntar(partes);
    const par = valores.cld_cli;
    const u = String(valores.U_W);
    const fila = (tabla, llave) => E.doble_entrada[tabla].opciones.find((o) => o.llave === llave);
    const linea = {
      nombre: valores.nombre, L_L: valores.L_L, C_I: valores.C_I, C_T: valores.C_T,
      C_E: valores.C_E, U_W: valores.U_W, P_EB: valores.P_EB,
      C_LD: par.CLD, C_LI: par.CLI,
      P_LD: fila("PLD", valores.blindaje).valores[u],
      P_LI: fila("PLI", valores.tipo_linea).valores[u],
      adyacente: null,
    };
    if (vecina) {
      const {C_DJ, ...medidas} = vecina;
      linea.adyacente = medidas;
      linea.C_DJ = C_DJ;
    }
    return linea;
  }

  // P_LD y P_LI vienen como número: se busca de qué fila salieron con la U_W de la línea.
  poner(linea) {
    const problemas = [];
    const intentar = (f) => {
      try {
        f();
      } catch (error) {
        if (!(error instanceof DatoFaltante)) throw error;
        problemas.push(error.message);
      }
    };
    intentar(() => ponerTodos(this.campos, linea));
    intentar(() => this.derivados.cld_cli.ponerValor({CLD: linea.C_LD, CLI: linea.C_LI},
                                                      linea._filas?.cld_cli));
    const u = String(linea.U_W);
    for (const [campo, tabla, valor, nombre] of [["blindaje", "PLD", linea.P_LD, "Tabla B.8"],
                                                 ["tipo_linea", "PLI", linea.P_LI, "Tabla B.9"]]) {
      const fila = E.doble_entrada[tabla].opciones.find((o) => igual(o.valores[u], valor));
      if (fila) this.derivados[campo].poner(fila.llave);
      else problemas.push(`${tabla === "PLD" ? "P_LD" : "P_LI"} = ${valor} no está en la ${nombre} para U_W = ${linea.U_W} kV`);
    }
    this.hayAdyacente.poner(Boolean(linea.adyacente));
    if (linea.adyacente) {
      this.adyacente.poner(linea.adyacente);
      intentar(() => this.C_DJ.ponerValor(linea.C_DJ, linea._filas?.C_DJ));
    }
    this._verAdyacente();
    if (problemas.length) throw new DatoFaltante(problemas.join("\n"));
  }

  _todos() {
    const vecina = Object.fromEntries(Object.entries(this.adyacente.campos).map(([n, c]) => [`vecina_${n}`, c]));
    return {...this.campos, ...this.derivados, hayAdyacente: this.hayAdyacente, C_DJ: this.C_DJ, ...vecina};
  }

  foto() {
    return fotoDe(this._todos());
  }

  ponerFoto(foto) {
    ponerFotoEn(this._todos(), foto);
    this._verAdyacente();
  }

  filas() {
    const filas = {...filasDe(this.campos), cld_cli: this.derivados.cld_cli.llaveElegida()};
    if (this.hayAdyacente.valor()) filas.C_DJ = this.C_DJ.llaveElegida();
    return filas;
  }
}

// --- Emplazamiento: de dónde sale N_G ----------------------------------------------

const coma = (n, decimales) => n.toFixed(decimales).replace(".", ",");
const paraLaCasilla = (n) => Number(n.toPrecision(4));

export const CELDA_EN_CERO = "La celda de la NASA más cercana no registra descargas. Un cero puede ser " +
  "real o falta de dato (mar, desierto), y el programa no calcula un riesgo cero en silencio: " +
  "declara N_G con su fuente.";

export function textoDeFicha(f) {
  return `Celda de la NASA en (${coma(f.celda_lat, 2)}°; ${coma(f.celda_lon, 2)}°), ` +
    `a ${coma(f.distancia_km, 1)} km del sitio. ${coma(f.destellos_totales, 2)} destellos ` +
    `totales/km² año × ${coma(f.fraccion_nube_tierra, 3)} nube-tierra (relación intranube:tierra ≈ ` +
    `${coma(f.relacion_ic_cg, 1)}). Observada ${coma(f.horas_observadas, 0)} h.`;
}

export class PanelEmplazamiento {
  constructor(contenedor) {
    const m = marco(contenedor, "Densidad de descargas a tierra (N_G)");
    this.raiz = m;
    const radios = document.createElement("div");
    radios.className = "radios";
    this.radios = {};
    for (const [modo, texto] of [["coordenadas", "Por coordenadas (NASA LIS)"],
                                 ["declarado", "Declarado, con su fuente"]]) {
      const label = document.createElement("label");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "modo-ng";
      radio.value = modo;
      radio.addEventListener("change", () => {
        this._mostrarModo();
        this.decir("");
      });
      label.append(radio, ` ${texto}`);
      radios.append(label);
      this.radios[modo] = radio;
    }
    m.append(radios);

    this.marcoCoordenadas = document.createElement("div");
    m.append(this.marcoCoordenadas);
    this.lat = new CampoNumero(this.marcoCoordenadas, "Latitud", {unidad: "°", minimo: -90, maximo: 90});
    this.lon = new CampoNumero(this.marcoCoordenadas, "Longitud", {unidad: "°", minimo: -180, maximo: 180});
    this.fraccion = new CampoNumero(this.marcoCoordenadas, "Fracción nube-tierra",
                                    {valor: D("Emplazamiento").fraccion_nube_tierra, positivo: true, maximo: 1});
    this.botonBuscar = document.createElement("button");
    this.botonBuscar.type = "button";
    this.botonBuscar.textContent = "Buscar";
    this.botonBuscar.addEventListener("click", () => this.buscar());
    this.lat.control.append(" ", this.botonBuscar);

    this.marcoDeclarado = document.createElement("div");
    m.append(this.marcoDeclarado);
    this.fuente = new CampoTexto(this.marcoDeclarado, "Fuente de N_G", {ancho: 50});

    this.N_G = new CampoNumero(m, "N_G", {unidad: "rayos/km² año", positivo: true});
    this.aviso = document.createElement("p");
    this.aviso.className = "aviso-ng";
    m.append(this.aviso);
    this.limpiar();
  }

  modo() {
    return this.radios.declarado.checked ? "declarado" : "coordenadas";
  }

  ponerModo(modo) {
    this.radios[modo].checked = true;
    this._mostrarModo();
  }

  _mostrarModo() {
    const coordenadas = this.modo() === "coordenadas";
    this.marcoCoordenadas.hidden = !coordenadas;
    this.marcoDeclarado.hidden = coordenadas;
    this.N_G.soloLectura(coordenadas);
  }

  decir(mensaje) {
    this.aviso.textContent = mensaje;
    this.aviso.hidden = !mensaje;
  }

  _coordenadas() {
    const v = recoger({lat: this.lat, lon: this.lon, fraccion: this.fraccion});
    const limite = E.constantes.LIMITE_DE_LATITUD;
    if (Math.abs(v.lat) > limite && Math.abs(v.lon) <= limite) {
      // Casi seguro un error de tipeo: no se pasa a declarado, para que se vea qué se escribió.
      this.N_G.poner("");
      this.lat.marcar(true);
      this.lon.marcar(true);
      throw new DatoFaltante(
        `¿Pusiste latitud y longitud al revés? La latitud ${v.lat} queda fuera de la cobertura ` +
        `del sensor (±${limite}°), pero ${v.lon} sí cabría como latitud. Corrige las casillas; si el ` +
        "sitio de verdad está fuera de la cobertura, marca «Declarado, con su fuente» y escribe N_G.");
    }
    return v;
  }

  // Busca N_G en la climatología de la NASA y lo deja en la casilla.
  async buscar() {
    let v;
    try {
      v = this._coordenadas();
    } catch (error) {
      if (!(error instanceof DatoFaltante)) throw error;
      this.decir(error.message);
      return null;
    }
    this.botonBuscar.disabled = true;
    try {
      const r = await fetch(`/api/ng?lat=${v.lat}&lon=${v.lon}&fraccion=${v.fraccion}`);
      const datos = await r.json();
      if (!r.ok) {
        const detalle = typeof datos.detail === "string" ? datos.detail : "Coordenadas no válidas.";
        this.N_G.poner("");
        if (/cobertura/.test(detalle)) {
          this.ponerModo("declarado");
          this.decir(`${detalle} Se pasó al modo declarado.`);
        } else {
          this.decir(detalle);
        }
        return null;
      }
      if (datos.celda_en_cero) {
        this.N_G.poner("");
        this.decir(CELDA_EN_CERO);
        return null;
      }
      this.N_G.poner(paraLaCasilla(datos.N_G));
      this.decir(textoDeFicha(datos));
      this.N_G.entrada.dispatchEvent(new Event("change", {bubbles: true}));
      return datos;
    } finally {
      this.botonBuscar.disabled = false;
    }
  }

  // Antes de leer: con coordenadas y sin N_G en la casilla, se busca.
  async preparar() {
    if (this.modo() === "coordenadas" && !this.N_G.entrada.value.trim()) await this.buscar();
  }

  // {N_G, emplazamiento} para el caso, o DatoFaltante con el motivo.
  resolver() {
    if (this.modo() === "declarado") {
      const v = recoger({N_G: this.N_G, fuente: this.fuente});
      return {N_G: v.N_G, emplazamiento: {modo: "declarado", fuente: v.fuente}};
    }
    const v = this._coordenadas();
    if (!this.N_G.entrada.value.trim()) {
      const motivo = this.aviso.textContent || "Pulsa «Buscar» para traer N_G de la NASA.";
      throw new DatoFaltante(motivo);
    }
    return {
      N_G: this.N_G.valor(),
      emplazamiento: {modo: "coordenadas", lat: v.lat, lon: v.lon, fraccion_nube_tierra: v.fraccion},
    };
  }

  // Abre un caso. Sin emplazamiento (archivo viejo) queda declarado y SIN fuente.
  poner(N_G, emplazamiento, N_G_guardado) {
    this.limpiar();
    if (!emplazamiento || emplazamiento.modo === "declarado") {
      this.ponerModo("declarado");
      this.N_G.poner(N_G);
      if (emplazamiento) this.fuente.poner(emplazamiento.fuente);
      else this.decir("Este caso no dice de dónde sale N_G: escribe su fuente.");
      return;
    }
    this.lat.poner(emplazamiento.lat);
    this.lon.poner(emplazamiento.lon);
    this.fraccion.poner(emplazamiento.fraccion_nube_tierra);
    this.N_G.poner(paraLaCasilla(N_G));
    this.ponerModo("coordenadas");
    if (N_G_guardado !== undefined && N_G_guardado !== null && Math.abs(N_G_guardado - N_G) > 1e-9)
      this.decir("El N_G guardado no coincide con las coordenadas: al calcular se usa el que dan las coordenadas.");
  }

  // Al calcular, el servidor manda el N_G que de verdad usó.
  usado(N_G) {
    if (this.modo() === "coordenadas") this.N_G.poner(paraLaCasilla(N_G));
  }

  foto() {
    return {modo: this.modo(), aviso: this.aviso.textContent,
            ...fotoDe({lat: this.lat, lon: this.lon, fraccion: this.fraccion,
                       fuente: this.fuente, N_G: this.N_G})};
  }

  ponerFoto(foto) {
    this.ponerModo(foto.modo === "declarado" ? "declarado" : "coordenadas");
    ponerFotoEn({lat: this.lat, lon: this.lon, fraccion: this.fraccion,
                 fuente: this.fuente, N_G: this.N_G}, foto);
    this.decir(foto.aviso || "");
  }

  limpiar() {
    this.ponerModo("coordenadas");
    this.lat.poner("");
    this.lon.poner("");
    this.fraccion.poner(D("Emplazamiento").fraccion_nube_tierra);
    this.fuente.poner("");
    this.N_G.poner("");
    this.decir("");
  }
}
