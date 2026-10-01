// La calculadora: la versión web de ventanas/principal_norma.py, editor_caso.py,
// resultados.py y desglose.py. Arma el caso con los formularios, lo manda al motor
// (en el servidor) y muestra lo que vuelve. Aquí no se calcula ningún riesgo.

import {CampoTexto, DatoFaltante, juntar} from "./campos.js";
import {FormularioEstructura, FormularioLinea, FormularioZona, ListaDeFormularios,
        PanelEmplazamiento, configurar, pestanas} from "./formularios.js";

const $ = (id) => document.getElementById(id);

const TITULOS = {1: "R1 · Pérdida de vidas humanas", 2: "R2 · Pérdida de servicio público",
                 3: "R3 · Pérdida de patrimonio cultural", 4: "R4 · Pérdida económica"};

// Los ejemplos resueltos del Anexo E que vienen con el programa.
const EJEMPLOS_DE_LA_NORMA = [
  ["E.2  Casa rural (1 zona)", "casa_rural"],
  ["E.3  Edificio de oficinas (5 zonas)", "E3_oficinas"],
  ["E.4  Hospital (4 zonas)", "E4_hospital"],
  ["E.5  Edificio de apartamentos (1 zona)", "E5_apartamentos"],
];

// 2.506e-05 -> «2,506e-05», como el panel del programa.
function numero(valor) {
  if (valor === 0) return "0";
  const [mantisa, exponente] = valor.toExponential(3).split("e");
  const signo = exponente.startsWith("-") ? "-" : "+";
  return `${mantisa.replace(".", ",")}e${signo}${exponente.replace(/^[-+]/, "").padStart(2, "0")}`;
}

function porcentaje(parte, total) {
  return total ? `${((parte / total) * 100).toFixed(1).replace(".", ",")} %` : "—";
}

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function decir(texto, esError = false) {
  const estado = $("estado");
  estado.textContent = texto;
  estado.className = esError ? "error multilinea" : "pequeno";
}

async function pedir(url, opciones = {}) {
  const respuesta = await fetch(url, opciones);
  if (!respuesta.ok) {
    let detalle = `Error ${respuesta.status}`;
    try {
      const cuerpo = await respuesta.json();
      detalle = typeof cuerpo.detail === "string" ? cuerpo.detail : JSON.stringify(cuerpo.detail);
    } catch { /* el cuerpo no era JSON */ }
    throw new DatoFaltante(detalle);
  }
  return respuesta;
}

const postJson = (url, datos) => pedir(url, {
  method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(datos),
});

// --- Datos del proyecto (la primera ventana del programa) -------------------------

class DatosProyecto {
  constructor(contenedor) {
    this.campos = {
      Proyecto: new CampoTexto(contenedor, "Proyecto:", {obligatorio: false, ancho: 40}),
      "Diseñador": new CampoTexto(contenedor, "Diseñador:", {obligatorio: false}),
      "Dirección": new CampoTexto(contenedor, "Dirección:", {obligatorio: false}),
      "Teléfono": new CampoTexto(contenedor, "Teléfono:", {obligatorio: false}),
    };
    const fila = document.createElement("div");
    fila.className = "campo";
    fila.innerHTML = '<label for="descripcion">Descripción:</label><span class="control">' +
      '<textarea id="descripcion" rows="4" cols="40"></textarea></span>';
    contenedor.append(fila);
    this.descripcion = fila.querySelector("textarea");
  }

  leer() {
    const datos = {};
    for (const [nombre, campo] of Object.entries(this.campos)) datos[nombre] = campo.crudo();
    datos["Descripción"] = this.descripcion.value.trim();
    return datos;
  }
}

// --- El editor del caso: N_G, estructura, zonas y líneas -----------------------------

class EditorCaso {
  constructor(contenedor) {
    this.contenedor = contenedor;
    this.construir();
  }

  construir() {
    this.contenedor.replaceChildren();
    this.emplazamiento = new PanelEmplazamiento(this.contenedor);
    const p = pestanas(this.contenedor, ["Estructura", "Zonas", "Líneas"]);
    this.elegirPestana = p.elegir;
    this.estructura = new FormularioEstructura(p.paneles[0]);
    // Sin zonas no hay riesgo que calcular: el mínimo es 1. Las líneas pueden ser cero.
    this.zonas = new ListaDeFormularios(p.paneles[1], (c) => new FormularioZona(c),
                                        {titulo: "Zonas de la estructura", singular: "zona", minimo: 1});
    this.lineas = new ListaDeFormularios(p.paneles[2], (c) => new FormularioLinea(c),
                                         {titulo: "Líneas que entran a la estructura", singular: "línea"});
  }

  // El caso en el formato de casos/*.json, con las pérdidas de cada riesgo pedido.
  async caso(tipos) {
    await this.emplazamiento.preparar();
    const partes = juntar({
      ng: ["N_G", () => this.emplazamiento.resolver()],
      estructura: ["Estructura", () => this.estructura.leer()],
      lineas: ["Líneas", () => this.lineas.leer()],
      zonas: ["Zonas", () => this.zonas.leer(tipos)],
    });
    return {
      N_G: partes.ng.N_G,
      emplazamiento: partes.ng.emplazamiento,
      tipos,
      estructura: partes.estructura,
      lineas: partes.lineas,
      zonas: partes.zonas.map(({comun, perdidas}) => ({
        ...comun,
        perdidas: Object.fromEntries(tipos.map((t) => [String(t), perdidas[t]])),
      })),
    };
  }

  // Abre lo que devuelve /api/abrir: {por_tipo: {tipo: caso}, N_G_guardado}.
  poner({por_tipo: casos, N_G_guardado}) {
    this.construir();
    const tipos = Object.keys(casos).sort();
    const alguno = casos[tipos[0]];
    const problemas = [];
    const intentar = (encabezado, f) => {
      try {
        f();
      } catch (error) {
        if (!(error instanceof DatoFaltante)) throw error;
        problemas.push(`${encabezado}:\n${error.message}`);
      }
    };
    this.emplazamiento.poner(alguno.N_G, alguno.emplazamiento, N_G_guardado);
    intentar("Estructura", () => this.estructura.poner(alguno.estructura));
    intentar("Líneas", () => this.lineas.poner(alguno.lineas));
    intentar("Zonas", () => this.zonas.poner(alguno.zonas.map(
      (_, i) => Object.fromEntries(tipos.map((t) => [t, casos[t].zonas[i]])))));
    if (problemas.length) throw new DatoFaltante(problemas.join("\n\n"));
  }
}

// --- Resultados ------------------------------------------------------------------------

class PanelResultados {
  constructor() {
    this.cuerpo = $("filas-resultados");
    this.resumen = $("resumen");
    this.notas = $("notas");
    this.boton = $("b-desglose");
    this.elegido = null;
    this.obsoleto = false;
    this.resultados = null;
  }

  limpiar() {
    this.cuerpo.innerHTML = '<tr><td colspan="4" class="pequeno">Pulse «Calcular».</td></tr>';
    this.resumen.textContent = "";
    this.resumen.className = "";
    this.notas.replaceChildren();
    this.boton.disabled = true;
    this.elegido = null;
    this.resultados = null;
    this.marcarObsoleto(false);
  }

  mostrar(datos) {
    this.marcarObsoleto(false);
    this.resultados = datos.riesgos;
    const filas = [];
    for (const [tipo, r] of Object.entries(datos.riesgos)) {
      const clase = r.cumple ? "cumple" : "no-cumple";
      filas.push(`<tr class="riesgo ${clase}" data-tipo="${tipo}" tabindex="0">
        <td><b>${TITULOS[tipo]}</b></td><td class="num">${numero(r.total)}</td>
        <td class="num">${numero(r.R_T)}</td><td class="num">${r.cumple ? "Cumple" : "No cumple"}</td></tr>`);
      for (const [nombre, z] of Object.entries(r.zonas)) {
        filas.push(`<tr class="zona" data-tipo="${tipo}"><td class="sangria">${escapar(nombre)}</td>
          <td class="num">${numero(z.total)}</td><td></td><td class="num">${porcentaje(z.total, r.total)}</td></tr>`);
      }
    }
    this.cuerpo.innerHTML = filas.join("");
    this.cuerpo.querySelectorAll("tr").forEach((fila) => {
      fila.addEventListener("click", () => this.elegir(fila.dataset.tipo));
    });
    const incumplen = Object.entries(datos.riesgos).filter(([, r]) => !r.cumple).map(([t]) => `R${t}`);
    this.resumen.textContent = incumplen.length
      ? `No cumple: ${incumplen.join(", ")}. Hace falta protección.`
      : "Los riesgos evaluados están por debajo del tolerable.";
    this.resumen.className = incumplen.length ? "no-cumple" : "cumple";
    this.notas.replaceChildren(...datos.avisos.map((a) => {
      const p = document.createElement("p");
      p.className = "aviso";
      p.textContent = `Ojo: ${a}`;
      return p;
    }));
    this.boton.disabled = false;
    this.elegido = null;
  }

  elegir(tipo) {
    if (this.obsoleto) return;
    this.elegido = tipo;
    this.cuerpo.querySelectorAll("tr").forEach((f) => f.classList.toggle("elegida", f.dataset.tipo === tipo));
  }

  // Si no hay ninguno elegido, el primero que no cumple.
  riesgoParaDesglose() {
    if (this.elegido) return Number(this.elegido);
    const entradas = Object.entries(this.resultados || {});
    const incumple = entradas.find(([, r]) => !r.cumple);
    return Number((incumple || entradas[0])[0]);
  }

  // Los datos cambiaron: lo que se ve ya no sale de lo escrito.
  marcarObsoleto(si = true) {
    if (si && !this.resultados) return;
    this.obsoleto = si;
    $("panel-resultados").classList.toggle("obsoleto", si);
    if (si) {
      this.resumen.textContent = "Los datos cambiaron: hay que volver a calcular.";
      this.resumen.className = "";
      this.boton.disabled = true;
      $("panel-desglose").hidden = true;
    }
  }
}

// --- ¿De dónde viene el riesgo? ---------------------------------------------------------

const SIN_MEDIDAS = "Ninguna medida del catálogo baja este componente. Aquí se baja el riesgo " +
  "reduciendo la pérdida: n_z/n_t, t_z, o separando la zona.";

function mostrarDesglose(d) {
  $("panel-desglose").hidden = false;
  const titulo = $("desglose-titulo");
  titulo.className = d.cumple ? "cumple" : "no-cumple";
  titulo.textContent = `${TITULOS[d.tipo]}   ${numero(d.total)} 1/año   ` +
    `(tolerable ${numero(d.R_T)})   ${d.cumple ? "Cumple" : "No cumple"}`;
  $("desglose-queda").textContent = `R${d.tipo} queda en`;
  const total = d.aportes.reduce((s, a) => s + a.valor, 0);
  const cuerpo = $("desglose-componentes");
  cuerpo.innerHTML = d.aportes.map((a, i) => `<tr data-i="${i}" tabindex="0">
    <td>${escapar(a.texto)}</td><td class="num">${numero(a.valor)}</td>
    <td class="num">${porcentaje(a.valor, total)}</td></tr>`).join("");
  const elegir = (i) => {
    cuerpo.querySelectorAll("tr").forEach((f) => f.classList.toggle("elegida", f.dataset.i === String(i)));
    const a = d.aportes[i];
    $("desglose-medidas-titulo").textContent = `Medidas que bajan ${a.componente} en este caso`;
    $("desglose-medidas").innerHTML = a.rebajas.length
      ? a.rebajas.map((r) => `<tr class="${r.cumple ? "cumple" : ""}"><td>${escapar(r.medida)}</td>
          <td class="num">${numero(r.componente)}</td><td class="num">${numero(r.total)}</td>
          <td class="num">${r.cumple ? "Sí, ya cumple" : "No, ella sola no"}</td></tr>`).join("")
      : `<tr><td colspan="4">${SIN_MEDIDAS}</td></tr>`;
  };
  cuerpo.querySelectorAll("tr").forEach((f) => f.addEventListener("click", () => elegir(Number(f.dataset.i))));
  if (d.aportes.length) elegir(0);
  else $("desglose-medidas").innerHTML = "";
  $("panel-desglose").scrollIntoView({behavior: "smooth", block: "start"});
}

// --- La pantalla completa -----------------------------------------------------------------

class Calculadora {
  constructor() {
    this.proyecto = new DatosProyecto($("datos-proyecto"));
    this.editor = new EditorCaso($("editor"));
    this.resultados = new PanelResultados();
    this.ultimo = null;          // {caso, datos}
    this.ocupado = false;

    $("b-nuevo").addEventListener("click", () => this.nuevo());
    $("b-abrir").addEventListener("click", () => $("archivo").click());
    $("archivo").addEventListener("change", (e) => this.abrirArchivo(e.target));
    $("b-guardar").addEventListener("click", () => this.trabajar("b-guardar", () => this.guardar()));
    $("b-calcular").addEventListener("click", () => this.trabajar("b-calcular", () => this.calcular()));
    $("b-informe").addEventListener("click", () => this.trabajar("b-informe", () => this.informe()));
    $("b-desglose").addEventListener("click", () => this.trabajar("b-desglose", () => this.deDondeViene()));
    for (const [texto, archivo] of EJEMPLOS_DE_LA_NORMA) $("b-ejemplos").add(new Option(texto, archivo));
    $("b-ejemplos").addEventListener("change", (e) => {
      const archivo = e.target.value;
      e.target.value = "";
      if (archivo) this.trabajar("b-ejemplos", () => this.abrirEjemplo(archivo));
    });
    // Cualquier cambio en el caso deja en gris el resultado que ya no le corresponde.
    for (const evento of ["input", "change"]) {
      $("editor").addEventListener(evento, () => this.resultados.marcarObsoleto());
      document.querySelectorAll('input[name="tipo"]').forEach((c) =>
        c.addEventListener(evento, () => this.resultados.marcarObsoleto()));
    }
  }

  tipos() {
    const elegidos = [...document.querySelectorAll('input[name="tipo"]:checked')].map((c) => Number(c.value));
    return elegidos.length ? elegidos : [1];
  }

  async trabajar(id, accion) {
    if (this.ocupado) return;
    this.ocupado = true;
    const boton = $(id);
    boton.disabled = true;
    document.body.classList.add("trabajando");
    try {
      await accion();
    } catch (error) {
      if (error instanceof DatoFaltante) decir(error.message, true);
      else decir(`Algo falló: ${error.message}`, true);
    } finally {
      this.ocupado = false;
      boton.disabled = false;
      document.body.classList.remove("trabajando");
    }
  }

  async calcular() {
    decir("Calculando…");
    let caso;
    try {
      caso = await this.editor.caso(this.tipos());
    } catch (error) {
      this.resultados.limpiar();
      this.ultimo = null;
      throw new DatoFaltante(`Faltan datos:\n\n${error.message}`);
    }
    const datos = await (await postJson("/api/evaluar", caso)).json();
    this.editor.emplazamiento.usado(datos.N_G);
    this.resultados.mostrar(datos);
    $("panel-desglose").hidden = true;
    this.ultimo = {caso, datos};
    decir("Listo.");
    $("panel-resultados").scrollIntoView({behavior: "smooth", block: "start"});
    return this.ultimo;
  }

  // El resultado vigente, recalculándolo si los datos ya no son esos.
  async alDia() {
    if (!this.ultimo || this.resultados.obsoleto) return this.calcular();
    return this.ultimo;
  }

  nuevo() {
    if (!confirm("Se va a borrar todo lo escrito y los resultados.\n¿Seguir?")) return;
    this.editor.construir();
    this.resultados.limpiar();
    $("panel-desglose").hidden = true;
    this.ultimo = null;
    decir("Caso nuevo.");
  }

  async abrirDatos(datos, nombre) {
    const abierto = await (await postJson("/api/abrir", datos)).json();
    const tipos = Object.keys(abierto.por_tipo).map(Number);
    document.querySelectorAll('input[name="tipo"]').forEach((c) => { c.checked = tipos.includes(Number(c.value)); });
    this.resultados.limpiar();
    $("panel-desglose").hidden = true;
    this.ultimo = null;
    try {
      this.editor.poner(abierto);
    } catch (error) {
      throw new DatoFaltante(`Se abrió «${nombre}», pero hay datos que revisar:\n\n${error.message}`);
    }
    decir(`Caso «${nombre}» abierto.`);
  }

  async abrirEjemplo(archivo) {
    const datos = await (await pedir(`/api/ejemplos/${encodeURIComponent(archivo)}`)).json();
    await this.abrirDatos(datos, archivo);
  }

  async abrirArchivo(entrada) {
    const archivo = entrada.files[0];
    entrada.value = "";
    if (!archivo) return;
    await this.trabajar("b-abrir", async () => {
      let datos;
      try {
        datos = JSON.parse(await archivo.text());
      } catch (error) {
        throw new DatoFaltante(`No se pudo abrir «${archivo.name}»: no es JSON válido.`);
      }
      await this.abrirDatos(datos, archivo.name);
    });
  }

  async guardar() {
    let caso;
    try {
      caso = await this.editor.caso(this.tipos());
    } catch (error) {
      throw new DatoFaltante(`Faltan datos:\n\n${error.message}`);
    }
    const nombre = (this.proyecto.leer().Proyecto || "caso").replace(/[^\w\- áéíóúñÁÉÍÓÚÑ]/g, "") || "caso";
    descargar(new Blob([JSON.stringify(caso, null, 2)], {type: "application/json"}), `${nombre}.json`);
    decir("Caso guardado. Se puede abrir aquí o en el programa de escritorio.");
  }

  // Recalcula ANTES de escribir: el informe no puede mezclar datos nuevos con riesgos viejos.
  async informe() {
    const {caso} = await this.alDia();
    decir("Generando el informe: buscando medidas de protección y dibujando las figuras…");
    const respuesta = await postJson("/api/informe", {caso, proyecto: this.proyecto.leer()});
    descargar(await respuesta.blob(), "Memoria de calculo.pdf");
    decir("Informe generado.");
  }

  async deDondeViene() {
    const {caso} = await this.alDia();
    const tipo = this.resultados.riesgoParaDesglose();
    decir(`Probando cada medida sobre R${tipo}…`);
    const d = await (await postJson(`/api/desglose?tipo=${tipo}`, caso)).json();
    mostrarDesglose(d);
    decir("");
  }
}

function descargar(blob, nombre) {
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(blob);
  enlace.download = nombre;
  document.body.append(enlace);
  enlace.click();
  enlace.remove();
  setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
}

async function arrancar() {
  try {
    configurar(await (await pedir("/api/esquema")).json());
  } catch (error) {
    $("cargando").textContent = `No se pudieron cargar las tablas de la norma: ${error.message}`;
    $("cargando").className = "error";
    return;
  }
  window.calculadora = new Calculadora();
  $("cargando").hidden = true;
  $("calculadora").hidden = false;
}

arrancar();
