// Las ayudas que salen al tocar cada casilla: qué es el dato, de dónde sale y qué se
// suele poner. La llave es el rótulo de la casilla; cuando un mismo rótulo sale en varias
// pestañas con tablas distintas (L_F, L_O), la llave lleva además la tabla: «rótulo@C.8».
// Solo es texto: los valores de la norma siguen saliendo de calculate_risk/norma/tablas.py.

export const AYUDAS = {
  // --- Datos del proyecto ---
  "Proyecto:": "Nombre del proyecto u obra. Sale en la portada de la memoria de cálculo.",
  "Diseñador:": "Quien firma el estudio. Sale como autor del informe.",
  "Matrícula profesional:": "Número de su matrícula profesional (COPNIA, CONTE u otra). Sale en el cuadro de firma del informe.",
  "Dirección:": "Dónde queda la estructura. Solo para el informe.",
  "Teléfono:": "Contacto del diseñador. Solo para el informe.",

  // --- N_G ---
  "Latitud": "Latitud del sitio en grados decimales (por ejemplo 6,25 para Medellín). " +
    "Negativa al sur del ecuador. Se puede copiar de Google Maps.",
  "Longitud": "Longitud del sitio en grados decimales (por ejemplo -75,56 para Medellín). " +
    "Negativa al oeste de Greenwich, como toda Colombia.",
  "Fracción nube-tierra": "El satélite de la NASA cuenta todos los destellos; solo una parte cae a " +
    "tierra. 0,25 es la fracción usual: cerca de la cuarta parte cae a tierra (Rakov, 2016). " +
    "Cámbiela solo si tiene un dato local.",
  "Fuente de N_G": "De dónde sale el N_G que escribe: red local de detección de rayos, mapa oficial, " +
    "un estudio… La norma pide que el dato tenga su fuente.",
  "N_G": "Densidad de descargas a tierra: rayos por km² al año en el sitio. Es el dato que más pesa " +
    "en todo el cálculo. Con coordenadas se toma de la NASA; si no, escríbalo con su fuente.",

  // --- Estructura ---
  "Longitud (L)": "Largo de la estructura en metros. Con L, W y H se calcula el área donde un rayo " +
    "la alcanzaría (área de captación, Anexo A).",
  "Ancho (W)": "Ancho de la estructura en metros.",
  "Altura (H)": "Altura de la estructura en metros, hasta la cubierta. El área de captación crece " +
    "rápido con la altura (se extiende 3 veces H alrededor).",
  "Altura del saliente del techo (H_p)": "Si hay un elemento que sobresale bastante de la cubierta " +
    "(chimenea, antena, tanque), su altura sobre el suelo. Si no hay, déjelo en 0.",
  "Localización (C_D)": "Tabla A.1: qué tan expuesta está la estructura. Rodeada de edificios más " +
    "altos se protege (0,25); aislada o en una colina recibe más rayos (1 y 2).",
  "Personas en la estructura (n_t)": "Total de personas que suele haber en toda la estructura. Las " +
    "pérdidas de cada zona se reparten según n_z / n_t.",
  "Valor total de la estructura (c_t)": "Solo para R4 (pérdida económica): el valor total en la " +
    "moneda que use. Con la nota «a» de la Tabla C.11 marcada, este valor no influye.",
  "Riesgo de explosión o sistemas vitales": "Márquelo si hay riesgo de explosión o sistemas cuya " +
    "falla pone vidas en peligro (por ejemplo un hospital). Activa en R1 los componentes por falla " +
    "de sistemas internos (R_C, R_M, R_W, R_Z).",
  "Hay animales": "Márquelo en estructuras con animales (fincas, establos). Activa en R4 las " +
    "pérdidas por tensiones de paso y contacto (R_A, R_U).",

  // --- Zona: lo común ---
  "Nombre de la zona": "Un nombre para reconocerla (sala, parqueadero, cocina…). Una zona es una " +
    "parte de la estructura con características parecidas: mismo piso, mismo uso, mismas medidas.",
  "Tensiones de paso y contacto (P_TA)": "Tabla B.1: qué protege a las personas de las tensiones " +
    "cuando el rayo cae en la estructura. Sin medidas = 1. Avisos, aislamiento de las bajantes o " +
    "equipotencializar el terreno la reducen. Ojo: la norma solo las da por efectivas con SPCR.",
  "Protección contra daño físico (P_B)": "Tabla B.2: el sistema de protección contra rayos (SPCR: " +
    "pararrayos, bajantes y puesta a tierra) y su nivel. Sin SPCR = 1; el nivel I es el más eficaz.",
  "Tensiones de contacto por línea (P_TU)": "Tabla B.6: medidas contra las tensiones de contacto " +
    "cuando el rayo cae en una línea que entra (avisos, aislamiento, restricciones físicas).",
  "Superficie del piso (r_t)": "Tabla C.3: el tipo de piso donde están las personas. Un piso más " +
    "aislante (asfalto, madera) reduce el riesgo de las tensiones de paso y contacto.",
  "Medidas contra incendio (r_p)": "Tabla C.4: lo que hay para limitar un incendio: extintores, " +
    "alarmas, rutas de evacuación (reducen a la mitad) o extinción automática (aún más).",
  "Riesgo de incendio (r_f)": "Tabla C.5: qué tan fácil se incendia o explota la zona. Depende de la " +
    "carga de fuego: oficinas y viviendas suelen ser riesgo normal o bajo; bodegas de material " +
    "inflamable, alto. Las zonas con atmósferas explosivas van por clasificación (0/20, 1/21, 2/22).",
  "Personas o usuarios en la zona (n_z)": "Cuántas personas suele haber en esta zona.",
  "Horas al año de presencia (t_z)": "Cuántas horas al año hay gente en la zona. 8760 = siempre " +
    "(24 h × 365 días). Una oficina de lunes a viernes ronda las 2500.",
  "Zona exterior sin personas (anula R_A y R_U)": "Márquelo para zonas exteriores donde no " +
    "permanece gente: ahí no hay víctimas por tensiones de paso y contacto.",
  "Hay apantallamiento espacial": "Si la zona está dentro de una malla metálica (armadura, " +
    "fachada metálica) que apantalla los campos del rayo. Mejora la protección de los equipos.",
  "Ancho de la malla exterior (w_m1)": "Separación en metros entre los conductores de la malla del " +
    "edificio (límite exterior). Malla más fina = mejor apantallamiento (K_S1 = 0,12 × w_m1).",
  "Ancho de la malla interior (w_m2)": "Separación en metros de una malla interior, si hay otra " +
    "dentro (K_S2 = 0,12 × w_m2). Si no hay malla interior, ponga 8,4 m o más: equivale a " +
    "K_S2 = 1, sin apantallamiento.",

  // --- Pérdidas R1 ---
  "Pérdida por lesiones (L_T)": "Qué fracción de las personas resultaría herida por tensiones de " +
    "paso y contacto. La Tabla C.2 da 0,01 para cualquier estructura.",
  "Pérdida por daño físico (L_F)@C.2": "Tabla C.2: qué tan grave es un incendio o explosión para las " +
    "vidas según el uso de la estructura (hospital, colegio, evento público, comercio…). " +
    "«No aplica» si la zona no tiene ese riesgo (un patio, por ejemplo).",
  "Pérdida por falla de sistemas (L_O)@C.2": "Tabla C.2: solo para estructuras donde la falla de los " +
    "equipos pone vidas en peligro: riesgo de explosión o áreas de hospital (cuidados intensivos, " +
    "quirófanos). En las demás, «no aplica».",
  "Daño especial (h_z)": "Tabla C.6: aumenta la pérdida si un incendio causaría pánico o la " +
    "evacuación es difícil (muchas personas, varios pisos, hospitales).",
  "Horas al año con personas en peligro afuera (t_e)": "Solo si un daño en la estructura afecta a " +
    "personas de afuera (una explosión, una nube tóxica). Si no, 0.",
  "Pérdida típica por daño físico fuera (L_FE)": "Qué fracción de esas personas de afuera se vería " +
    "afectada. Si no se conoce, la norma usa 1.",

  // --- Pérdidas R2 ---
  "Pérdida por daño físico (L_F)@C.8": "Tabla C.8: solo si la estructura presta un servicio público " +
    "(agua, gas, energía, telecomunicaciones) que se interrumpiría. Si no, «no aplica».",
  "Pérdida por falla de sistemas (L_O)@C.8": "Tabla C.8: servicio público interrumpido por la falla " +
    "de los equipos internos. Si la estructura no presta servicio público, «no aplica».",

  // --- Pérdidas R3 ---
  "Hay patrimonio cultural irremplazable": "Márquelo si en la zona hay patrimonio cultural que no " +
    "se puede reponer (museo, archivo histórico, obras de arte).",
  "Valor del patrimonio en la zona (c_z)": "Valor del patrimonio cultural de esta zona, en la moneda " +
    "que use. Se compara con el total de la estructura.",

  // --- Pérdidas R4 ---
  "Hay animales en la zona": "Márquelo si hay animales en esta zona (pérdida por lesiones de " +
    "animales, Tabla C.12).",
  "Pérdida por daño físico (L_F)@C.12": "Tabla C.12: pérdida económica típica por incendio o " +
    "explosión según el tipo de estructura.",
  "Pérdida por falla de sistemas (L_O)@C.12": "Tabla C.12: pérdida económica típica por falla de " +
    "los equipos internos según el tipo de estructura.",
  "Valor de los animales (c_a)": "Valor de los animales de la zona.",
  "Valor del edificio (c_b)": "Valor de la parte del edificio que corresponde a la zona.",
  "Valor del contenido (c_c)": "Valor de lo que hay dentro de la zona (muebles, mercancía…).",
  "Valor de los sistemas internos (c_s)": "Valor de los equipos eléctricos y electrónicos de la zona.",
  "Valor de los bienes en sitios peligrosos fuera (c_e)": "Valor de bienes de afuera que un daño en " +
    "la estructura pondría en riesgo. Normalmente 0.",
  "Comparar R4 contra el valor representativo (nota «a», Tabla C.11)": "Con la casilla marcada, R4 " +
    "se compara contra el valor tolerable de la Tabla 4 sin necesidad de los valores reales.",

  // --- Sistemas internos ---
  "Nombre": "Un nombre para reconocer el sistema (potencia, datos, alarma…).",
  "Lo alimenta la línea": "El nombre de la línea (pestaña Líneas) que alimenta este sistema, " +
    "escrito igual. Así se sabe qué rayos en qué línea le llegan.",
  "Cableado interno (K_S3)": "Tabla B.5: cómo va el cableado dentro. Bucles grandes captan más " +
    "sobretensión; cable blindado o en tubo metálico casi nada.",
  "Tensión soportada (U_W)": "Tensión de impulso que aguantan los equipos de este sistema, en kV. " +
    "Valores usuales si no se conoce: 2,5 kV equipos de potencia, 1,5 kV telecomunicaciones, " +
    "1 kV electrónica sensible.",
  "DPS coordinado (P_DPS)": "Tabla B.3: si hay un sistema de DPS (protectores contra sobretensiones) " +
    "coordinado según la IEC 62305-4, y de qué nivel.",

  // --- Líneas ---
  "Nombre de la línea": "Un nombre para la línea (potencia, telecomunicaciones…). Se usa para " +
    "conectar los sistemas internos con su línea.",
  "Longitud de la sección (L_L)": "Largo de la línea desde la estructura hasta el primer nodo " +
    "(transformador, caja de distribución), en metros. Si no se conoce, la norma usa 1000 m.",
  "Instalación (C_I)": "Tabla A.2: si la línea es aérea, enterrada, o enterrada bajo una malla de " +
    "puesta a tierra. Una línea aérea recibe muchos más rayos.",
  "Tipo de línea (C_T)": "Tabla A.3: baja tensión o telecomunicaciones (1), o alta tensión con " +
    "transformador a la entrada (el transformador atenúa).",
  "Entorno (C_E)": "Tabla A.4: dónde va la línea. En zona rural recibe más rayos que entre " +
    "edificios de ciudad.",
  "Tensión soportada del equipo (U_W)": "La menor tensión de impulso que aguantan los equipos " +
    "conectados a esta línea, en kV. Con ella se buscan P_LD y P_LI.",
  "Equipotencialización con DPS (P_EB)": "Tabla B.7: DPS en la entrada de la línea, unidos a la " +
    "barra equipotencial, y su nivel de protección.",
  "Blindaje y puesta a tierra (C_LD y C_LI)": "Tabla B.4: cómo es la línea por fuera: sin blindaje, " +
    "apantallada, en conducto metálico, con el blindaje conectado o no a la barra equipotencial.",
  "Conexión del blindaje (P_LD)": "Tabla B.8: si la línea tiene blindaje, cómo está conectado y su " +
    "resistencia por km. Sin blindaje, elija «sin conectar».",
  "Servicio que transporta (P_LI)": "Tabla B.9: si es una línea de potencia o de " +
    "telecomunicaciones.",
  "La línea llega a otra estructura (N_DJ)": "Márquelo si en el otro extremo de la línea hay otra " +
    "estructura: los rayos que le caen a ella también llegan por la línea.",
  "Localización de esa estructura (C_DJ)": "Tabla A.1, para la estructura del otro extremo: qué tan " +
    "expuesta está.",
  "Altura del saliente (H_p)": "Altura de algo que sobresalga de la cubierta de la otra estructura. " +
    "Si no hay, 0.",
};

// La ayuda de una casilla por su rótulo y, si hace falta, por la tabla de la norma.
export function ayudaDe(etiqueta, tabla = "") {
  const numero = (tabla.match(/Tabla ([A-Z]\.\d+)/) || [])[1];
  return (numero && AYUDAS[`${etiqueta}@${numero}`]) || AYUDAS[etiqueta] || "";
}
