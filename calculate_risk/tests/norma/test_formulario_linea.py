"""

H16 - la longitud L_L deja de estar clavada en 1000 m.
H18 - la línea puede llegar a otra estructura, y eso mete N_DJ en R_U, R_V
      y R_W por la ec. (A.5).

La prueba que cierra el paso mide H16: con la misma casa rural pero la línea
de 400 m en vez de 1000, el riesgo tiene que bajar en la proporción que
manda la norma, porque A_L y A_I son proporcionales a L_L.
"""
from dataclasses import fields

import pytest
from pytest import approx

tkinter = pytest.importorskip("tkinter")


def _hay_pantalla() -> bool:
    try:
        raiz = tkinter.Tk()
    except Exception:
        return False
    raiz.destroy()
    return True


pytestmark = pytest.mark.skipif(not _hay_pantalla(),
                                reason="no hay pantalla gráfica (ni Xvfb)")

from calculate_risk.norma import casos, probabilidades, riesgos, tablas   # noqa: E402
from calculate_risk.norma.modelo import Estructura, Linea                 # noqa: E402
from ventanas import campos, formularios                                  # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def caso():
    return casos.cargar_caso(RUTA_CASA_RURAL)


@pytest.fixture
def formulario(raiz):
    return formularios.FormularioLinea(raiz)


# ---------------------------------------------------------------------------
# El formulario cubre la dataclass entera
# ---------------------------------------------------------------------------

def test_el_formulario_cubre_todos_los_campos_de_la_linea(formulario):
    del_modelo = {campo.name for campo in fields(Linea)}
    del_formulario = set(formulario.campos)
    del_formulario |= {"C_LD", "C_LI", "P_LD", "P_LI"}   # de las listas derivadas
    del_formulario |= {"adyacente", "C_DJ"}              # del bloque de H18

    assert del_formulario == del_modelo


def test_las_dos_lineas_de_la_casa_rural_van_y_vuelven(formulario, caso):
    for original in caso["lineas"]:
        formulario.poner(original)

        assert formulario.leer() == original


# ---------------------------------------------------------------------------
# H16: la longitud ya no está clavada en 1000 m
# ---------------------------------------------------------------------------

def test_la_longitud_es_una_casilla_libre(formulario, caso):
    formulario.poner(caso["lineas"][0])
    formulario.campos["L_L"].poner(250)

    assert formulario.leer().L_L == 250


def test_acortar_la_linea_baja_el_riesgo_en_proporcion(formulario, caso):
    # A_L y A_I son proporcionales a L_L (ec. A.9 y A.11), y en la casa rural
    # R_V es el 96 % del riesgo: con la línea a 400 m en vez de 1000, la parte
    # que viene de las líneas tiene que quedar en 0,4 de la de antes.
    def riesgo_con(longitud):
        lineas = []
        for original in caso["lineas"]:
            formulario.poner(original)
            formulario.campos["L_L"].poner(longitud)
            lineas.append(formulario.leer())
        return riesgos.evaluar(caso["estructura"], lineas, caso["zonas"],
                               caso["N_G"], tipos=(1,))[1]

    mil = riesgo_con(1000)
    cuatrocientos = riesgo_con(400)

    assert mil["total"] == approx(2.506e-5, rel=0.01)          # Anexo E.2
    assert cuatrocientos["R_V"] == approx(0.4 * mil["R_V"], rel=1e-9)
    assert cuatrocientos["total"] < mil["total"]


def test_una_longitud_en_cero_no_pasa(formulario, caso):
    formulario.poner(caso["lineas"][0])
    formulario.campos["L_L"].poner(0)

    with pytest.raises(campos.DatoFaltante, match="mayor que cero"):
        formulario.leer()


# ---------------------------------------------------------------------------
# P_LD y P_LI salen de las tablas, no se escriben
# ---------------------------------------------------------------------------

def test_p_ld_y_p_li_se_buscan_con_la_tension_elegida(formulario):
    formulario.campos["nombre"].poner("potencia")
    formulario.campos["C_I"].poner_llave("aerea")
    formulario.campos["C_T"].poner_llave("bt_datos_telecomunicacion")
    formulario.campos["C_E"].poner_llave("rural")
    formulario.campos["P_EB"].poner_llave("sin_dps")
    formulario.derivados["cld_cli"].poner_llave("aerea_sin_blindaje")
    formulario.derivados["blindaje"].poner("hasta_1_ohm_km")
    formulario.derivados["tipo_linea"].poner("potencia")
    formulario.campos["U_W"].poner(4)

    linea = formulario.leer()

    assert linea.P_LD == probabilidades.p_ld("hasta_1_ohm_km", 4)
    assert linea.P_LI == probabilidades.p_li("potencia", 4)


def test_cambiar_la_tension_cambia_las_dos_probabilidades(formulario, caso):
    formulario.poner(caso["lineas"][0])          # U_W = 2,5 kV
    antes = formulario.leer()
    formulario.derivados["blindaje"].poner("1_a_5_ohm_km")
    formulario.campos["U_W"].poner(6)

    despues = formulario.leer()

    assert despues.P_LD < antes.P_LD and despues.P_LI < antes.P_LI
    assert despues.P_LD == tablas.PLD["conectada_barra_equipotencial"]["1_a_5_ohm_km"][6]


def test_la_tabla_b4_da_los_dos_factores_de_una_vez(formulario, caso):
    formulario.poner(caso["lineas"][0])
    formulario.derivados["cld_cli"].poner_llave("potencia_multi_puesta_a_tierra_neutro")

    linea = formulario.leer()

    assert (linea.C_LD, linea.C_LI) == (1, 0.2)


def test_un_p_ld_que_no_esta_en_la_tabla_avisa_al_abrir(formulario, caso):
    # Un JSON con P_LD escrito a mano fuera de la Tabla B.8 se caza aquí.
    mala = caso["lineas"][0]
    mala.P_LD = 0.77

    with pytest.raises(campos.DatoFaltante, match="Tabla B.8"):
        formulario.poner(mala)


# ---------------------------------------------------------------------------
# H18: la estructura del extremo lejano
# ---------------------------------------------------------------------------

def test_sin_estructura_adyacente_no_hay_n_dj(formulario, caso):
    formulario.poner(caso["lineas"][0])

    linea = formulario.leer()

    assert linea.adyacente is None
    assert formulario.hay_adyacente.valor() is False


def test_con_estructura_adyacente_aparece_n_dj(formulario, caso):
    formulario.poner(caso["lineas"][0])
    formulario.hay_adyacente.poner(True)
    formulario.adyacente.campos["L"].poner(30)
    formulario.adyacente.campos["W"].poner(20)
    formulario.adyacente.campos["H"].poner(10)
    formulario.C_DJ.poner_llave("aislada")

    linea = formulario.leer()
    r = riesgos.evaluar(caso["estructura"], [linea], caso["zonas"],
                        caso["N_G"], tipos=(1,))[1]

    assert linea.adyacente == Estructura(L=30, W=20, H=10)
    assert linea.C_DJ == tablas.CD["aislada"]
    detalle = r["zonas"][caso["zonas"][0].nombre]["_detalle"]
    assert detalle["lineas"][linea.nombre]["N_DJ"] > 0


def test_la_estructura_adyacente_va_y_vuelve(formulario, caso):
    original = caso["lineas"][0]
    original.adyacente = Estructura(L=17.3, W=23.8, H=9.5, H_p=12.0)
    original.C_DJ = tablas.CD["rodeada_objetos_mas_altos"]

    formulario.poner(original)

    assert formulario.leer() == original


def test_si_se_marca_la_adyacente_hay_que_dar_sus_medidas(formulario, caso):
    formulario.poner(caso["lineas"][0])
    formulario.hay_adyacente.poner(True)

    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.leer()

    mensaje = str(fallo.value)
    assert "Longitud (L)" in mensaje and "Altura (H)" in mensaje
    # y tampoco viene elegida la localización de esa estructura
    assert "Localización de esa estructura (C_DJ)" in mensaje


# ---------------------------------------------------------------------------
# Nada viene elegido de fábrica
# ---------------------------------------------------------------------------

def test_una_linea_recien_abierta_no_calcula_nada(formulario):
    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.leer()

    mensaje = str(fallo.value)
    for falta in ("Nombre de la línea", "Instalación (C_I)", "Entorno (C_E)",
                  "Tensión soportada del equipo (U_W)",
                  "Conexión del blindaje (P_LD)"):
        assert falta in mensaje