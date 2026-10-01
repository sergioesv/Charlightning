// El contador de visitas del pie de página, con sus dígitos de odómetro.
// Cada sesión del navegador suma una sola visita, aunque se recorran varias páginas.

const CLAVE = "charlightning:visita-contada";
const DIGITOS = 7;

function yaContada() {
  try {
    return sessionStorage.getItem(CLAVE) === "1";
  } catch {
    return false;
  }
}

function marcarContada() {
  try {
    sessionStorage.setItem(CLAVE, "1");
  } catch { /* sin almacenamiento: a lo sumo cuenta de más */ }
}

function pintar(caja, visitas) {
  const texto = String(visitas).padStart(DIGITOS, "0");
  caja.replaceChildren(...[...texto].map((d) => {
    const s = document.createElement("span");
    s.textContent = d;
    return s;
  }));
  caja.setAttribute("aria-label", `${visitas} visitas`);
}

async function contar() {
  const caja = document.getElementById("contador");
  if (!caja) return;
  try {
    const nueva = !yaContada();
    const r = await fetch("/api/visitas", {method: nueva ? "POST" : "GET"});
    if (!r.ok) return;
    if (nueva) marcarContada();
    pintar(caja, (await r.json()).visitas);
  } catch { /* sin red: el contador se queda en guiones */ }
}

contar();
