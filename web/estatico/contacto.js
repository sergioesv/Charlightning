// El formulario de contacto: manda el mensaje al servidor, que lo reenvía al autor.
// La dirección de destino no está aquí ni en ninguna página: solo la conoce el servidor.

const formulario = document.getElementById("contacto");
const estado = document.getElementById("c-estado");

// Desde «Servicios» se llega con /contacto.html?motivo=estudio: el motivo ya viene elegido.
const motivo = new URLSearchParams(location.search).get("motivo");
const lista = document.getElementById("c-motivo");
if (motivo && [...lista.options].some((o) => o.value === motivo)) lista.value = motivo;

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const boton = formulario.querySelector("button");
  const datos = Object.fromEntries(new FormData(formulario));
  if (!datos.nombre.trim() || !datos.mensaje.trim()) {
    estado.className = "error";
    estado.textContent = "Escriba su nombre y el mensaje.";
    return;
  }
  boton.disabled = true;
  estado.className = "pequeno";
  estado.textContent = "Enviando…";
  try {
    const r = await fetch("/api/contacto", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(datos),
    });
    const cuerpo = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(typeof cuerpo.detail === "string" ? cuerpo.detail : `Error ${r.status}`);
    formulario.reset();
    if (motivo) lista.value = motivo;
    estado.className = "cumple";
    estado.textContent = "¡Gracias! Su mensaje fue enviado.";
  } catch (error) {
    estado.className = "error";
    estado.textContent = `No se pudo enviar: ${error.message}`;
  } finally {
    boton.disabled = false;
  }
});
