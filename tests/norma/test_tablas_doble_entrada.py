"""
Paso 46a: consulta de las Tablas B.8 y B.9, que son de doble entrada.

P_LD depende del blindaje de la línea Y de la tensión soportada U_W; P_LI,
del tipo de línea Y de U_W. Hasta ahora esos valores se escribían a mano en
los casos JSON; la pantalla nueva los tiene que buscar en la tabla.

Los valores esperados que aparecen aquí se leen de tablas.py, salvo cuatro
que se escriben a propósito para que la prueba falle si alguien toca la
tabla sin querer: son los de la casa rural y los de la fila mejor y peor.
"""
import pytest

from calculate_risk.norma import probabilidades, tablas


# ---------------------------------------------------------------------------
# Las tensiones tabuladas
# ---------------------------------------------------------------------------

def test_las_tensiones_son_las_cinco_de_la_norma():
    assert probabilidades.tensiones_soportadas() == [1, 1.5, 2.5, 4, 6]


def test_las_dos_tablas_usan_las_mismas_tensiones():
    tensiones = set(probabilidades.tensiones_soportadas())

    assert set(tablas.PLI["telecomunicacion"]) == tensiones
    for blindaje in probabilidades.BLINDAJES:
        assert set(_fila(blindaje)) == tensiones, blindaje


def _fila(blindaje):
    if blindaje == "sin_conectar_barra_equipotencial":
        return tablas.PLD[blindaje]
    return tablas.PLD["conectada_barra_equipotencial"][blindaje]


# ---------------------------------------------------------------------------
# Tabla B.8 - P_LD
# ---------------------------------------------------------------------------

def test_los_cuatro_blindajes_son_las_cuatro_filas_de_la_tabla():
    del_modulo = set(probabilidades.BLINDAJES)
    de_la_tabla = {"sin_conectar_barra_equipotencial"}
    de_la_tabla |= set(tablas.PLD["conectada_barra_equipotencial"])

    assert del_modulo == de_la_tabla


def test_sin_conectar_el_blindaje_p_ld_vale_uno_siempre():
    # Fila peor de la Tabla B.8: el blindaje sin conectar no protege nada.
    for u_w in probabilidades.tensiones_soportadas():
        assert probabilidades.p_ld("sin_conectar_barra_equipotencial", u_w) == 1


def test_la_mejor_fila_con_la_mayor_tension_da_el_valor_mas_bajo():
    # Blindaje de hasta 1 ohm/km con equipo de 6 kV: 0,02.
    assert probabilidades.p_ld("hasta_1_ohm_km", 6) == 0.02


def test_la_casa_rural_da_p_ld_igual_a_uno():
    # Sus dos líneas tienen P_LD = 1 en el JSON, que es la fila sin conectar.
    assert probabilidades.p_ld("sin_conectar_barra_equipotencial", 2.5) == 1
    assert probabilidades.p_ld("sin_conectar_barra_equipotencial", 1.5) == 1


def test_p_ld_baja_al_subir_la_tension_soportada():
    # Comprobación de sentido: equipo más robusto, menos probabilidad de daño.
    for blindaje in ("5_a_20_ohm_km", "1_a_5_ohm_km", "hasta_1_ohm_km"):
        valores = [probabilidades.p_ld(blindaje, u)
                   for u in probabilidades.tensiones_soportadas()]

        assert valores == sorted(valores, reverse=True), blindaje


def test_p_ld_baja_al_mejorar_el_blindaje():
    for u_w in probabilidades.tensiones_soportadas():
        valores = [probabilidades.p_ld(b, u_w) for b in probabilidades.BLINDAJES]

        assert valores == sorted(valores, reverse=True), u_w


# ---------------------------------------------------------------------------
# Tabla B.9 - P_LI
# ---------------------------------------------------------------------------

def test_p_li_distingue_potencia_de_telecomunicacion():
    # La misma tensión da distinto según el tipo de línea (Tabla B.9).
    assert probabilidades.p_li("potencia", 2.5) == 0.3
    assert probabilidades.p_li("telecomunicacion", 2.5) == 0.2


def test_la_casa_rural_sale_de_la_tabla_b9():
    # El JSON trae P_LI = 0,3 en la línea de potencia (U_W = 2,5 kV) y 0,5 en
    # la de telecomunicación (U_W = 1,5 kV). Ahora se pueden buscar.
    assert probabilidades.p_li("potencia", 2.5) == 0.3
    assert probabilidades.p_li("telecomunicacion", 1.5) == 0.5


def test_con_un_kilovoltio_ninguna_de_las_dos_protege():
    assert probabilidades.p_li("potencia", 1) == 1
    assert probabilidades.p_li("telecomunicacion", 1) == 1


# ---------------------------------------------------------------------------
# Lo que no está tabulado avisa, no se inventa
# ---------------------------------------------------------------------------

def test_una_tension_no_tabulada_avisa_y_dice_cuales_hay():
    # La norma NO interpola: 3 kV no existe, y devolver algo sería inventar.
    with pytest.raises(ValueError, match="Tabla B.8"):
        probabilidades.p_ld("1_a_5_ohm_km", 3)

    with pytest.raises(ValueError) as fallo:
        probabilidades.p_li("potencia", 3)
    assert "1, 1.5, 2.5, 4, 6" in str(fallo.value)


def test_un_tipo_de_linea_inventado_avisa():
    with pytest.raises(ValueError, match="Tabla B.9"):
        probabilidades.p_li("fibra_optica", 2.5)