from calculate_risk.opciones import VALORES_OPCIONES

# Número de opciones que tiene cada combo en la pantalla
NUMERO_DE_OPCIONES = {
    "Ks3": 2, "pl": 3, "P_LD0": 2, "C_t0": 2, "P_LD1": 2, "P_LD2": 2,
    "h_1": 7, "L_f1": 4, "L_o1": 4, "L_f2": 7, "L_o2": 7, "L_f3": 2,
    "h4": 3, "L_f4": 8, "L_o4": 8, "L_t4": 3, "R_T4": 5,
    "E": 5, "r": 3, "SP": 3,
    "P_TU": 4, "C_LD": 2, "C_LI": 2, "P_LI": 2,
}


def test_un_valor_por_cada_opcion():
    for clave, cantidad in NUMERO_DE_OPCIONES.items():
        assert len(VALORES_OPCIONES[clave]) == cantidad, clave


def test_no_sobran_tablas():
    assert set(VALORES_OPCIONES) == set(NUMERO_DE_OPCIONES)


def test_correcciones():
    # "Contaminación del ambiente alrededor" (última opción) vale 50
    assert VALORES_OPCIONES["h_1"][6] == 50
    # "1 en 10000 años" es 1e-4 (antes decía 1e-5, igual que 1 en 100000)
    assert VALORES_OPCIONES["R_T4"][3] == 0.0001
    # En la Tabla B.4, una línea apantallada conectada
    # a la misma barra tiene CLD = 1.
    assert VALORES_OPCIONES["C_LD"][1] == 1

    # Para ese mismo caso, CLI = 0.
    assert VALORES_OPCIONES["C_LI"][1] == 0