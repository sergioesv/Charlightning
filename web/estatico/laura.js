// BROMA (temporal): el anuncio de Laura que se reproduce como un virus de pantalla.
// Cada clic saca una copia en otro lugar, hasta 3; el siguiente clic deja solo la original.
// La «x» cierra la ventanita; la original vuelve a los 30 segundos. Para quitar todo:
// borrar este archivo, el bloque BROMA de estilos.css y el <div id="laura"> de cada página.

(() => {
  const original = document.getElementById("laura");
  if (!original) return;
  const MAXIMO = 3;
  // Dónde salen las copias: lejos de la original, un poco al azar.
  const LUGARES = [
    {left: "8%", top: "18%"}, {left: "30%", top: "62%"}, {left: "52%", top: "12%"},
    {left: "14%", top: "70%"}, {left: "40%", top: "35%"},
  ];

  const copias = () => document.querySelectorAll(".publicidad.copia");

  function duplicar() {
    if (copias().length + 1 >= MAXIMO) {
      copias().forEach((c) => c.remove());
      return;
    }
    const copia = original.cloneNode(true);
    copia.removeAttribute("id");
    copia.classList.add("copia");
    copia.hidden = false;
    const lugar = LUGARES[Math.floor(Math.random() * LUGARES.length)];
    Object.assign(copia.style, {left: lugar.left, top: lugar.top, right: "auto", bottom: "auto",
                                animationDelay: `${-Math.random() * 3}s`});
    document.body.append(copia);
  }

  document.addEventListener("click", (e) => {
    const anuncio = e.target.closest(".publicidad");
    if (!anuncio) return;
    e.preventDefault();
    if (e.target.closest(".cerrar")) {
      if (anuncio === original) {
        original.hidden = true;
        setTimeout(() => { original.hidden = false; }, 30000);
      } else {
        anuncio.remove();
      }
      return;
    }
    if (e.target.closest("a")) duplicar();
  });
})();
