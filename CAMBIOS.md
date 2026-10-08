# Cambios

## 2.0.0 — octubre de 2026

La versión 1.x fue el programa anterior (rama `legacy-v1`). La 2.0 es el motor actual, que
usan el programa de escritorio y la web <https://charlightning.org>.

**Motor de cálculo**
- El cálculo vive en `calculate_risk/`, separado de las pantallas, y se prueba sin interfaz.
- Un caso admite varias zonas y varias líneas, y cada zona puede tener varios sistemas internos.
- Los cuatro riesgos (R1 a R4) se evalúan con las pérdidas propias de cada uno.
- Los cuatro ejemplos del Anexo E de la NTC 4552-2 son pruebas automáticas y se muestran en
  <https://charlightning.org/validacion.html>.
- Se revisó el cálculo contra la IEC 62305-2: L<sub>E</sub> también en R1 (ec. C.5 y C.6),
  filas «DPS mejores que NPR I» de las Tablas B.3 y B.7, y aviso de las medidas que la norma
  solo da por efectivas con un SPCR.
- Un riesgo marcado sin pérdidas cargadas avisa en lugar de calcularse.

**Densidad de descargas a tierra (N_G)**
- Se puede obtener desde latitud y longitud con la climatología LIS/OTD de la NASA, o declarar
  con su fuente. La ficha del dato (celda, distancia, tiempo de observación y fracción
  nube-tierra) queda en la memoria de cálculo.
- La fracción nube-tierra por omisión es 0,25 (Rakov, 2016), editable.
- La latitud o la longitud 0 son coordenadas válidas.

**Memoria de cálculo**
- Sale en PDF desde Python, sin instalar LaTeX: portada, desarrollo del cálculo, veredicto,
  medidas de protección con el porcentaje que reducen, figuras y referencias.
- Tamaño Carta, tablas y figuras nuevas, cuadro de firma del proyectista y bloque con la
  versión del motor y el enlace al código.
- Las memorias generadas en la web llevan un código y un QR para comprobar su registro en
  <https://charlightning.org/verify>.

**Web**
- Calculadora con los mismos formularios del programa de escritorio, ayudas en cada casilla,
  ejemplos de la norma, informe en PDF y tabla de N_G por ciudad de Colombia.
- API pública documentada en <https://charlightning.org/api/docs>.
