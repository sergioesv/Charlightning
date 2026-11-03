// Avisa al servidor de un paso dado en la calculadora (solo el nombre del paso; ver web/eventos.py).
// Una vez por paso y por sesión del navegador, para que el embudo cuente personas y no clics.

const hechos = new Set();

export function registrar(paso) {
  if (hechos.has(paso)) return;
  hechos.add(paso);
  try {
    fetch("/api/evento", {
      method: "POST", keepalive: true,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({paso}),
    }).catch(() => {});
  } catch { /* medir nunca debe estorbar */ }
}
