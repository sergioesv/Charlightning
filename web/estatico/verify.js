// La página a la que lleva el QR de la memoria: pregunta al servidor qué quedó registrado.

const CODIGO = /^CHL-\d{4}-[0-9A-F]{6}$/;
const resultado = document.getElementById("resultado");
const campo = document.getElementById("codigo");

function elemento(etiqueta, texto, clase) {
  const e = document.createElement(etiqueta);
  if (texto !== undefined) e.textContent = texto;
  if (clase) e.className = clase;
  return e;
}

function cientifico(valor) {
  if (valor === null || valor === undefined) return "—";
  const [mantisa, exponente] = Number(valor).toExponential(3).split("e");
  const sup = elemento("sup", String(parseInt(exponente, 10)));
  const celda = document.createDocumentFragment();
  celda.append(`${mantisa.replace(".", ",")} × 10`, sup);
  return celda;
}

function fila(rotulo, contenido, clase) {
  const tr = elemento("tr");
  tr.append(elemento("th", rotulo), elemento("td", undefined, clase));
  tr.lastChild.append(contenido);
  return tr;
}

function mostrarRegistro(r) {
  const tabla = elemento("table");
  const cumple = r.verdict === "CUMPLE";
  const veredicto = elemento("b", r.verdict, cumple ? "veredicto-si" : "veredicto-no");
  tabla.append(
    fila("Código", r.id, "codigo"),
    fila("Registrada", new Date(r.created_at).toLocaleString("es-CO")),
    fila("Veredicto", veredicto),
    fila("R₁ calculado", cientifico(r.risk_r1)),
    fila("Coordenadas (≈ 0,01°)", r.coordinates ? r.coordinates.split(",").map((x) => x.replace(".", ",")).join("; ") : "no se registraron"),
    fila("Huella de los datos", r.data_hash, "codigo huella"),
    fila("Versión del motor", r.engine_version),
  );
  resultado.replaceChildren(
    elemento("h2", "Memoria registrada"),
    tabla,
    elemento("p", `La huella impresa en el PDF empieza por ${r.huella}.`, "pequeno"));
  resultado.hidden = false;
}

function mostrarError(texto) {
  resultado.replaceChildren(elemento("h2", "No se pudo verificar"), elemento("p", texto, "aviso"));
  resultado.hidden = false;
}

async function verificar(codigo) {
  campo.value = codigo;
  if (!CODIGO.test(codigo)) {
    return mostrarError("Un código de memoria se ve así: CHL-2026-7F3A9C.");
  }
  try {
    const r = await fetch(`/api/verificar/${encodeURIComponent(codigo)}`);
    if (r.ok) return mostrarRegistro(await r.json());
    const detalle = (await r.json().catch(() => ({}))).detail;
    mostrarError(r.status === 404
      ? "No hay ninguna memoria registrada con ese código. Revise que lo haya escrito bien: "
        + "si el documento trae un código y no aparece aquí, no fue generado por Charlightning."
      : (detalle || "El servidor no pudo responder."));
  } catch {
    mostrarError("No hay conexión con el servidor.");
  }
}

document.getElementById("buscar").addEventListener("submit", (evento) => {
  evento.preventDefault();
  const codigo = campo.value.trim().toUpperCase();
  if (codigo) location.assign(`/verify/${encodeURIComponent(codigo)}`);
});

const inicial = decodeURIComponent(location.pathname.split("/").filter(Boolean)[1] || "")
  .trim().toUpperCase();
if (inicial) verificar(inicial);
