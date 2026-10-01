// BROMA (temporal): el anuncio de Laura que actúa como virus de pantalla.
// No sale de entrada: aparece a los 4 o 5 minutos de estar en el sitio (el reloj sigue
// aunque se cambie de página). Cada clic saca una copia en otro lugar, hasta 3; el
// siguiente clic deja solo una. La «x» lo cierra… y a los 4 o 5 minutos vuelve.
// Para quitar todo: borrar este archivo, el bloque BROMA de estilos.css y el
// <div id="laura"> de cada página.

(() => {
  const original = document.getElementById("laura");
  if (!original) return;
  const MAXIMO = 3;
  const CLAVE = "charlightning:laura-aparece";
  const LUGARES = [
    {left: "8%", top: "18%"}, {left: "30%", top: "62%"}, {left: "52%", top: "12%"},
    {left: "14%", top: "70%"}, {left: "40%", top: "35%"},
  ];

  const entre4y5Minutos = () => (4 + Math.random()) * 60 * 1000;
  const leer = () => { try { return Number(sessionStorage.getItem(CLAVE)) || 0; } catch { return 0; } };
  const guardar = (t) => { try { sessionStorage.setItem(CLAVE, String(t)); } catch { /* da igual */ } };
  const copias = () => document.querySelectorAll(".publicidad.copia");
  let temporizador = null;

  function programar(cuando) {
    guardar(cuando);
    original.hidden = true;
    clearTimeout(temporizador);
    temporizador = setTimeout(() => { original.hidden = false; }, Math.max(0, cuando - Date.now()));
  }

  // Primera vez en la sesión: se agenda; si ya estaba agendado, se respeta la hora.
  programar(leer() || Date.now() + entre4y5Minutos());

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
        copias().forEach((c) => c.remove());
        programar(Date.now() + entre4y5Minutos());
      } else {
        anuncio.remove();
      }
      return;
    }
    if (e.target.closest("a")) duplicar();
  });
})();
