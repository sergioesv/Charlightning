"""Valor numérico de cada opción de los combos de la pantalla.

Cada lista tiene un valor por opción, en el mismo orden en que
aparecen en el combo (la opción 0 es la primera).
"""

VALORES_OPCIONES = {
    # Cableado interno: Apantallado, No apantallado
    "Ks3": [0.1, 1],
    # Línea eléctrica: Aérea (1), Subterránea (2), Ninguna (0)
    "pl": [1, 2, 0],
    # Apantallamiento de la línea eléctrica: No apantallado, Apantallado
    "P_LD0": [1, 0.4],
    # Transformador: Con transformador, Sin transformador
    "C_t0": [0.2, 1],
    # Otros servicios aéreos: No apantallado, Apantallado
    "P_LD1": [1, 0.4],
    # Otros servicios subterráneos: No apantallado, Apantallado
    "P_LD2": [1, 0.4],
    # R1 - riesgo especial: sin riesgo, pánico bajo, medio, alto,
    # problemas de evacuación, peligro alrededor, contaminación alrededor
    "h_1": [1, 2, 5, 10, 5, 20, 50],
    # R1 - pérdida por daño físico: otras, iglesias/museos,
    # comercios/colegios, hospitales/hoteles
    "L_f1": [0.01, 0.02, 0.05, 0.1],
    # R1 - pérdida por falla de sistemas: no aplica, explosión,
    # hospitales, sistemas de seguridad críticos
    # PENDIENTE: verificar con IEC 62305-2:2024
    "L_o1": [0, 0.1, 0.001, 0.00001],
    # R2 - servicio público (daño físico): ninguno, ferrocarril, electricidad,
    # telecomunicaciones, radio y TV, agua, gas
    "L_f2": [0, 0.01, 0.01, 0.01, 0.01, 0.1, 0.1],
    # R2 - servicio público (falla de sistemas): mismas opciones
    "L_o2": [0, 0.001, 0.001, 0.001, 0.001, 0.01, 0.01],
    # R3 - patrimonio cultural: sin valor histórico, pérdidas irremplazables
    "L_f3": [0, 0.1],
    # R4 - riesgo especial: sin riesgo, medioambiental, contaminación
    "h4": [1, 20, 50],
    # R4 - pérdida por daño físico: no aplica, otras, prisión/iglesia,
    # comercial, oficina/escuela, pública, hospitales/hoteles, museo/agrícola
    # PENDIENTE: verificar con IEC 62305-2:2024
    "L_f4": [0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.5, 0.5],
    # R4 - pérdida por falla de sistemas: no aplica, otras,
    # iglesia/prisión/pública, museo/escuela, agrícola,
    # industrial/comercial, hospital/hotel/oficina, explosión
    "L_o4": [0, 0.0001, 0.001, 0.001, 0.001, 0.01, 0.01, 0.1],
    # R4 - lesiones a seres vivos: sin riesgo, ganado dentro, ganado fuera
    "L_t4": [0, 0.01, 0.01],
    # R4 - riesgo tolerable: 1 en 10, 100, 1000, 10000, 100000 años
    "R_T4": [0.1, 0.01, 0.001, 0.0001, 0.00001],
    # Nivel del SPCR: no protegida, nivel IV, III, II, I
    "E": [0, 0.8, 0.9, 0.95, 0.98],
    # Medidas contra incendio: ninguna, manuales, automáticas
    "r": [1, 0.5, 0.2],
    # DPS: ninguno, solo en la entrada de servicios, según NTC 4552-4
    "SP": [0, 1, 2],
    # Medidas contra tensión de contacto en las líneas (Tabla B.6):
    # sin medidas, avisos de peligro, aislamiento eléctrico, restricciones físicas
    "P_TU": [1, 0.1, 0.01, 0],
    # Apantallamiento/puesta a tierra de la línea para daño por corriente
    # directa en la línea (Tabla B.4, simplificado a los dos casos más
    # comunes: normal, o apantallada y puesta a tierra en la entrada)
    "C_LD": [1, 0],
    # Igual que C_LD, pero para la sobretensión inducida por un impacto
    # cerca de la línea (Tabla B.4, misma simplificación)
    "C_LI": [1, 0],
    # Tensión soportada de los equipos conectados a las líneas (Tabla B.9,
    # simplificado a dos casos representativos: equipos sensibles con
    # U_W bajo, o tensión soportada típica U_W = 2,5 kV)
    "P_LI": [1, 0.3],
}