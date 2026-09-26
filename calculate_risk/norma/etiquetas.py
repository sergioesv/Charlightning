"""
Este módulo es SOLO presentación: no contiene ni un número. Los valores
siguen viviendo únicamente en tablas.py, que es la fuente verificada contra
las capturas de la NTC 4552-2:2023.

La prueba tests/norma/test_etiquetas.py exige que cada llave de cada tabla
tenga su texto y que no sobre ninguno, que es justo lo que faltaba para que
las dos cosas no se separaran.
"""
from calculate_risk.norma import tablas


# Tabla de la norma y título de cada una, para los rótulos de la pantalla.
NOMBRES = {
    "RT": ("Tabla 4", "Riesgo tolerable"),
    "CD": ("Tabla A.1", "Factor de localización de la estructura"),
    "CI": ("Tabla A.2", "Factor de instalación de la línea"),
    "CT": ("Tabla A.3", "Factor por tipo de línea"),
    "CE": ("Tabla A.4", "Factor medioambiental de la línea"),
    "PTA": ("Tabla B.1", "Medidas contra tensiones de paso y de contacto"),
    "PB": ("Tabla B.2", "Protección contra daño físico (SPCR)"),
    "PDPS": ("Tabla B.3", "Sistema de DPS coordinado"),
    "CLD_CLI": ("Tabla B.4", "Blindaje, puesta a tierra y aislamiento de la línea"),
    "KS3": ("Tabla B.5", "Cableado interno"),
    "PTU": ("Tabla B.6", "Medidas contra tensiones de contacto por la línea"),
    "PEB": ("Tabla B.7", "Equipotencialización con DPS"),
    "PLD": ("Tabla B.8", "Blindaje de la línea y tensión soportada"),
    "PLI": ("Tabla B.9", "Tipo de línea y tensión soportada"),
    "N_SUPERFICIE": ("Tabla C.3", "Superficie del suelo o del piso"),
    "RP": ("Tabla C.4", "Medidas contra incendio"),
    "RF": ("Tabla C.5", "Riesgo de incendio o de explosión"),
    "HZ": ("Tabla C.6", "Daño especial (pánico y evacuación)"),
    "LF_L1": ("Tabla C.2", "L1 - pérdida por daño físico"),
    "LO_L1": ("Tabla C.2", "L1 - pérdida por falla de sistemas internos"),
    "LF_L2": ("Tabla C.8", "L2 - pérdida por daño físico"),
    "LO_L2": ("Tabla C.8", "L2 - pérdida por falla de sistemas internos"),
    "LF_L4": ("Tabla C.12", "L4 - pérdida por daño físico"),
    "LO_L4": ("Tabla C.12", "L4 - pérdida por falla de sistemas internos"),
}


# Tablas que una lista desplegable puede mostrar tal cual: una fila, un valor.
# Quedan fuera RT (no se elige, sale del tipo de riesgo) y PLD/PLI, que son
# tablas de doble entrada: hace falta elegir además la tensión soportada Uw.
SIMPLES = (
    "CD", "CI", "CT", "CE",
    "PTA", "PB", "PDPS", "CLD_CLI", "KS3", "PTU", "PEB",
    "N_SUPERFICIE", "RP", "RF", "HZ",
    "LF_L1", "LO_L1", "LF_L2", "LO_L2", "LF_L4", "LO_L4",
)


ETIQUETAS = {

    "RT": {
        "L1": "R1 - Pérdida de vidas humanas",
        "L2": "R2 - Pérdida de servicio público",
        "L3": "R3 - Pérdida de patrimonio cultural",
        "L4": "R4 - Pérdida económica",
    },

    # ---------------- Anexo A ----------------

    "CD": {
        "rodeada_objetos_mas_altos": "Rodeada de objetos más altos",
        "rodeada_objetos_misma_altura_o_inferior":
            "Rodeada de objetos de la misma altura o más bajos",
        "aislada": "Aislada, sin otros objetos cerca",
        "aislada_colina_o_monticulo": "Aislada sobre una colina o un montículo",
    },

    "CI": {
        "aerea": "Aérea",
        "subterranea": "Subterránea",
        "subterranea_bajo_malla_puesta_a_tierra":
            "Subterránea, bajo una malla de puesta a tierra",
    },

    "CT": {
        "bt_datos_telecomunicacion":
            "Baja tensión, datos o telecomunicaciones",
        "at_con_transformador": "Alta tensión, con transformador AT/BT",
    },

    "CE": {
        "rural": "Rural",
        "suburbano": "Suburbano",
        "urbano": "Urbano",
        "urbano_edificios_altos": "Urbano con edificios altos",
    },

    # ---------------- Anexo B ----------------

    "PTA": {
        "sin_medidas": "Sin medidas de protección",
        "avisos_de_peligro": "Avisos de peligro",
        "aislamiento_electrico": "Aislamiento eléctrico de las bajantes expuestas",
        "equipotencializacion_terreno": "Equipotencialización efectiva del terreno",
        "restricciones_fisicas_o_armadura_bajada":
            "Restricciones físicas, o armadura del edificio usada como bajante",
    },

    "PB": {
        "sin_spcr": "Estructura no protegida",
        "spcr_nivel_IV": "SPCR de nivel IV",
        "spcr_nivel_III": "SPCR de nivel III",
        "spcr_nivel_II": "SPCR de nivel II",
        "spcr_nivel_I": "SPCR de nivel I",
        "captador_nivel_I_con_armadura_continua":
            "Captador de nivel I y armadura metálica continua como bajante",
        "techo_metalico_o_captacion_completa_con_armadura":
            "Techo metálico o captación completa, con armadura continua",
    },

    "PDPS": {
        "sin_dps_coordinado": "Sin sistema de DPS coordinado",
        "npr_III_IV": "DPS de NPR III-IV",
        "npr_II": "DPS de NPR II",
        "npr_I": "DPS de NPR I",
    },

    "CLD_CLI": {
        "aerea_sin_blindaje": "Aérea, sin blindaje",
        "enterrada_sin_blindaje": "Enterrada, sin blindaje",
        "potencia_multi_puesta_a_tierra_neutro":
            "De potencia, con el neutro puesto a tierra en varios puntos",
        "subterranea_blindada_sin_conectar_barra":
            "Subterránea blindada, blindaje sin conectar a la barra equipotencial",
        "aerea_apantallada_sin_conectar_barra":
            "Aérea apantallada, apantallamiento sin conectar a la barra equipotencial",
        "subterranea_apantallada_conectada_barra":
            "Subterránea apantallada, apantallamiento conectado a la barra equipotencial",
        "aerea_apantallada_conectada_barra":
            "Aérea apantallada, apantallamiento conectado a la barra equipotencial",
        "cable_en_conducto_metalico_conectado_barra":
            "Cable en conducto metálico conectado a la barra equipotencial",
        "sin_conexion_lineas_externas": "Sin líneas externas conectadas",
        "interfaz_aislamiento_IEC62305_4":
            "Con interfaz de aislamiento según IEC 62305-4",
    },

    "KS3": {
        "sin_blindar_sin_precauciones":
            "Cable sin blindar, sin precauciones para evitar bucles",
        "sin_blindar_precauciones_bucles_grandes":
            "Cable sin blindar, evitando bucles grandes",
        "sin_blindar_precauciones_bucles":
            "Cable sin blindar, evitando bucles",
        "con_blindaje_o_conducto_metalico":
            "Cable blindado o dentro de un conducto metálico",
    },

    "PTU": {
        "sin_medidas": "Sin medidas de protección",
        "avisos": "Avisos de peligro",
        "aislamiento_electrico": "Aislamiento eléctrico",
        "restricciones_fisicas": "Restricciones físicas",
    },

    "PEB": {
        "sin_dps": "Sin DPS de equipotencialización",
        "npr_III_IV": "DPS de NPR III-IV",
        "npr_II": "DPS de NPR II",
        "npr_I": "DPS de NPR I",
    },

    "PLD": {
        "sin_conectar_barra_equipotencial":
            "Blindaje sin conectar a la barra equipotencial",
        "conectada_barra_equipotencial":
            "Blindaje conectado a la barra equipotencial",
        "5_a_20_ohm_km": "Resistencia del blindaje entre 5 y 20 ohm/km",
        "1_a_5_ohm_km": "Resistencia del blindaje entre 1 y 5 ohm/km",
        "hasta_1_ohm_km": "Resistencia del blindaje hasta 1 ohm/km",
    },

    "PLI": {
        "potencia": "Línea de potencia",
        "telecomunicacion": "Línea de telecomunicaciones",
    },

    # ---------------- Anexo C ----------------

    "N_SUPERFICIE": {
        "agricola_hormigon": "Agrícola u hormigón",
        "marmol_ceramica": "Mármol o cerámica",
        "grava_tapetes_alfombra": "Grava, tapete o alfombra",
        "asfalto_linoleo_madera": "Asfalto, linóleo o madera",
    },

    "RP": {
        "sin_medidas": "Sin medidas contra incendio",
        "extintores_alarma_manual_o_evacuacion":
            "Extintores, alarma manual, hidrantes, compartimentación o rutas de evacuación",
        "extincion_o_alarma_automatica":
            "Extinción automática o alarma automática",
    },

    "RF": {
        "explosion_zonas_0_20": "Riesgo de explosión, zonas 0 y 20",
        "explosion_zonas_1_21": "Riesgo de explosión, zonas 1 y 21",
        "explosion_zona_2_22": "Riesgo de explosión, zonas 2 y 22",
        "fuego_alto": "Riesgo de incendio alto",
        "fuego_normal": "Riesgo de incendio normal",
        "fuego_bajo": "Riesgo de incendio bajo",
        "sin_riesgo": "Sin riesgo de incendio ni de explosión",
    },

    "HZ": {
        "sin_dano_especial": "Sin daño especial",
        "panico_bajo": "Nivel bajo de pánico",
        "panico_medio_o_dificultad_evacuacion":
            "Nivel medio de pánico, o dificultad de evacuación",
        "panico_alto": "Nivel alto de pánico",
    },

    "LF_L1": {
        "riesgo_explosion": "Con riesgo de explosión",
        "hospital_hotel_escuela_edificio_publico":
            "Hospital, hotel, escuela o edificio público",
        "evento_publico_iglesia_museo": "Evento público, iglesia o museo",
        "industrial_comercial": "Industrial o comercial",
        "otros": "Otras estructuras",
    },

    "LO_L1": {
        "riesgo_explosion": "Con riesgo de explosión",
        "hospital_uci_quirofano": "Hospital: unidad de cuidados intensivos y quirófanos",
        "hospital_otras_partes": "Hospital: otras dependencias",
    },

    "LF_L2": {
        "gas_agua_electricidad": "Gas, agua o suministro eléctrico",
        "tv_telecomunicacion": "Televisión o telecomunicaciones",
    },

    "LO_L2": {
        "gas_agua_electricidad": "Gas, agua o suministro eléctrico",
        "tv_telecomunicacion": "Televisión o telecomunicaciones",
    },

    "LF_L4": {
        "riesgo_explosion": "Con riesgo de explosión",
        "hospital_industria_museo_agricultura":
            "Hospital, industria, museo o agricultura",
        "hotel_escuela_oficina_iglesia_evento_publico_comercio":
            "Hotel, escuela, oficina, iglesia, evento público o comercio",
        "otros": "Otras estructuras",
    },

    "LO_L4": {
        "riesgo_explosion": "Con riesgo de explosión",
        "hospital_industria_oficina_hotel_comercio":
            "Hospital, industria, oficina, hotel o comercio",
        "museo_agricultura_escuela_iglesia_evento_publico":
            "Museo, agricultura, escuela, iglesia o evento público",
        "otros": "Otras estructuras",
    },
}


def nombre_de(tabla: str) -> str:
    """'CD' -> 'Tabla A.1 - Factor de localización de la estructura'."""
    numero, titulo = NOMBRES[tabla]
    return f"{numero} - {titulo}"


def texto(tabla: str, llave: str) -> str:
    """El texto que ve el usuario para una fila concreta."""
    return ETIQUETAS[tabla][llave]


def opciones(tabla: str) -> list:
    """[(texto, valor), ...] en el orden de la tabla, para armar una lista.

    El valor sale de tablas.py, nunca de aquí. En CLD_CLI el valor es el par
    {"CLD": ..., "CLI": ...}, porque esa tabla da los dos factores de una vez.
    """
    if tabla not in SIMPLES:
        raise ValueError(
            f"{tabla} no es una tabla de opción simple; no se puede armar una "
            f"lista con ella sola. Las simples son: {', '.join(SIMPLES)}"
        )
    valores = getattr(tablas, tabla)
    return [(ETIQUETAS[tabla][llave], valor) for llave, valor in valores.items()]