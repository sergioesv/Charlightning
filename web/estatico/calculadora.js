// Calculadora: arma el JSON del caso, lo manda a /api y muestra lo que vuelve.
// Aquí no se calcula nada: los números salen del motor en el servidor.

const $ = (id) => document.getElementById(id);
const COMPONENTES = ["R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z"];
const NOMBRES = {
  1: "R1 · Pérdida de vida humana",
  2: "R2 · Pérdida de servicio al público",
  3: "R3 · Pérdida de patrimonio cultural",
  4: "R4 · Pérdida de valor económico",
};

const SUPER = {"-": "⁻", "+": "", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹"};
function cientifico(x) {
  if (x === 0) return "0";
  const [mantisa, exponente] = x.toExponential(3).split("e");
  return `${mantisa} × 10${[...exponente].map((c) => SUPER[c]).join("")}`;
}

function escribirEstado(texto, esError = false) {
  const estado = $("estado");
  estado.textContent = texto;
  estado.className = esError ? "error" : "pequeno";
}

function leerCaso() {
  try {
    return JSON.parse($("caso").value);
  } catch (error) {
    throw new Error("El caso no es JSON válido: " + error.message);
  }
}

function ponerCaso(caso) {
  $("caso").value = JSON.stringify(caso, null, 2);
  $("resultados").innerHTML = "";
  const empl = caso.emplazamiento || {};
  if (empl.modo === "coordenadas") {
    $("lat").value = empl.lat ?? "";
    $("lon").value = empl.lon ?? "";
  }
}

async function detalleDeError(respuesta) {
  try {
    const cuerpo = await respuesta.json();
    return typeof cuerpo.detail === "string" ? cuerpo.detail : JSON.stringify(cuerpo.detail);
  } catch {
    return `Error ${respuesta.status}`;
  }
}

async function ocupado(boton, trabajo) {
  boton.disabled = true;
  try {
    await trabajo();
  } catch (error) {
    escribirEstado(error.message, true);
  } finally {
    boton.disabled = false;
  }
}

// --- Ejemplos y archivo -------------------------------------------------------

async function cargarListaDeEjemplos() {
  const nombres = await (await fetch("/api/ejemplos")).json();
  for (const nombre of nombres) {
    $("ejemplo").add(new Option(nombre.replaceAll("_", " "), nombre));
  }
}

$("ejemplo").addEventListener("change", async (evento) => {
  if (!evento.target.value) return;
  const respuesta = await fetch("/api/ejemplos/" + encodeURIComponent(evento.target.value));
  ponerCaso(await respuesta.json());
  escribirEstado("Ejemplo cargado.");
});

$("archivo").addEventListener("change", async (evento) => {
  const archivo = evento.target.files[0];
  if (!archivo) return;
  try {
    ponerCaso(JSON.parse(await archivo.text()));
    escribirEstado(`Caso «${archivo.name}» cargado.`);
  } catch (error) {
    escribirEstado("El archivo no es JSON válido: " + error.message, true);
  }
});

// --- N_G desde coordenadas ---------------------------------------------------

$("usar-coordenadas").addEventListener("click", (evento) => ocupado(evento.target, async () => {
  const lat = parseFloat($("lat").value);
  const lon = parseFloat($("lon").value);
  if (Number.isNaN(lat) || Number.isNaN(lon)) throw new Error("Escriba latitud y longitud.");
  const respuesta = await fetch(`/api/ng?lat=${lat}&lon=${lon}`);
  if (!respuesta.ok) throw new Error(await detalleDeError(respuesta));
  const ficha = await respuesta.json();

  const caso = $("caso").value.trim() ? leerCaso() : {tipos: [1], estructura: {}, lineas: [], zonas: []};
  caso.N_G = ficha.N_G;
  caso.emplazamiento = {modo: "coordenadas", lat, lon, fraccion_nube_tierra: ficha.fraccion_nube_tierra};
  $("caso").value = JSON.stringify(caso, null, 2);

  $("ficha").textContent =
    `N_G = ${ficha.N_G.toFixed(3)} descargas/km²/año (celda ${ficha.celda_lat.toFixed(2)}, ` +
    `${ficha.celda_lon.toFixed(2)}, a ${ficha.distancia_km.toFixed(1)} km). ` +
    `Fuente: ${ficha.producto || "NASA LIS/OTD"}.` +
    (ficha.celda_en_cero ? " Atención: la celda tiene cero destellos registrados." : "");
  escribirEstado("N_G actualizado en el caso.");
}));

// --- Evaluar -----------------------------------------------------------------

function tablaDeRiesgo(tipo, r) {
  const filas = COMPONENTES.filter((c) => r.componentes[c] !== 0)
    .map((c) => `<tr><td>${c}</td><td class="num">${cientifico(r.componentes[c])}</td>
      <td class="num">${((100 * r.componentes[c]) / r.total).toFixed(1)} %</td></tr>`)
    .join("");
  const zonas = Object.entries(r.zonas)
    .map(([nombre, z]) => `<tr><td>${escaparHtml(nombre)}</td><td class="num">${cientifico(z.total)}</td></tr>`)
    .join("");
  const veredicto = r.cumple
    ? '<span class="cumple">Cumple</span>'
    : '<span class="no-cumple">No cumple: requiere medidas de protección</span>';
  return `<div class="tarjeta">
    <h2>${NOMBRES[tipo] || "R" + tipo}</h2>
    <p>R${tipo} = <strong>${cientifico(r.total)}</strong> · tolerable R_T = ${cientifico(r.R_T)} · ${veredicto}</p>
    <div class="rejilla">
      <div class="tabla-envuelta"><table>
        <thead><tr><th>Componente</th><th class="num">Valor</th><th class="num">Aporte</th></tr></thead>
        <tbody>${filas || '<tr><td colspan="3">Todos los componentes son cero.</td></tr>'}</tbody>
      </table></div>
      <div class="tabla-envuelta"><table>
        <thead><tr><th>Zona</th><th class="num">R${tipo}</th></tr></thead>
        <tbody>${zonas}</tbody>
      </table></div>
    </div>
  </div>`;
}

function mostrarResultados(datos) {
  const avisos = datos.avisos.map((a) => `<div class="aviso">${escaparHtml(a)}</div>`).join("");
  const riesgos = Object.entries(datos.riesgos).map(([t, r]) => tablaDeRiesgo(t, r)).join("");
  $("resultados").innerHTML =
    `<p class="pequeno">N_G usado: ${datos.N_G.toFixed(3)} descargas/km²/año</p>` + avisos + riesgos;
}

function escaparHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

$("evaluar").addEventListener("click", (evento) => ocupado(evento.target, async () => {
  escribirEstado("Evaluando…");
  const respuesta = await fetch("/api/evaluar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(leerCaso()),
  });
  if (!respuesta.ok) throw new Error(await detalleDeError(respuesta));
  mostrarResultados(await respuesta.json());
  escribirEstado("Listo.");
}));

// --- Informe PDF -------------------------------------------------------------

$("informe").addEventListener("click", (evento) => ocupado(evento.target, async () => {
  escribirEstado("Generando la memoria de cálculo; puede tardar unos segundos…");
  const proyecto = $("proyecto").value.trim();
  const respuesta = await fetch("/api/informe", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({caso: leerCaso(), proyecto: proyecto ? {Proyecto: proyecto} : {}}),
  });
  if (!respuesta.ok) throw new Error(await detalleDeError(respuesta));
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(await respuesta.blob());
  enlace.download = "Memoria de calculo.pdf";
  enlace.click();
  setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
  escribirEstado("Memoria descargada.");
}));

cargarListaDeEjemplos().catch(() => escribirEstado("No se pudo cargar la lista de ejemplos.", true));
