"""
Paso 45b: las pérdidas de la zona, una pestaña por riesgo.

La prueba que cierra el paso es test_la_zona_de_la_casa_rural_da_el_riesgo_de_la_norma:
se arma la zona en el formulario, se calcula, y tiene que salir el 2,506e-5
que publica el Anexo E.2. Es la primera vez en la Fase 5 que un número de la
norma sale de la pantalla nueva.
"""
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

from calculate_risk.norma import casos, riesgos, tablas             # noqa: E402
from calculate_risk.norma.modelo import Zona                        # noqa: E402
from ventanas import campos, formularios                            # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def caso_casa_rural():
    return casos.cargar_caso(RUTA_CASA_RURAL)


@pytest.fixture
def formulario(raiz):
    return formularios.FormularioZona(raiz)


# ---------------------------------------------------------------------------
# Cada pestaña pregunta lo que le toca
# ---------------------------------------------------------------------------

def test_cada_pestana_devuelve_los_campos_de_su_riesgo(formulario):
    for tipo, pestana in formulario.pestanas.items():
        _elegir_todo(pestana)

        assert set(pestana.leer()) == set(formularios.POR_TIPO[tipo])


def test_hay_una_pestana_por_riesgo(formulario):
    assert sorted(formulario.pestanas) == [1, 2, 3, 4]
    assert formulario.cuaderno.tab(0, "text") == "R1 Vidas humanas"


def _elegir_todo(pestana):
    """Elige la primera fila de cada lista obligatoria de la pestaña."""
    for campo in pestana.campos.values():
        if isinstance(campo, campos.CampoTabla) and not campo.opcional:
            campo.poner_llave(campo.llaves[0])


# ---------------------------------------------------------------------------
# "No aplica" es una respuesta, no un olvido
# ---------------------------------------------------------------------------

def test_una_zona_sin_servicio_publico_da_perdidas_cero(formulario):
    # R2 entero es opcional: hay estructuras que no prestan ningún servicio.
    perdidas = formulario.pestanas[2].leer()

    assert perdidas == {"L_F": 0, "L_O": 0}


def test_sin_patrimonio_cultural_la_perdida_es_cero(formulario):
    perdidas = formulario.pestanas[3].leer()

    assert perdidas["L_F"] == 0


def test_con_patrimonio_cultural_sale_el_valor_de_la_tabla(formulario):
    # Tabla C.10: L_F = 0,1 para museos y galerías.
    bandera, _ = formulario.pestanas[3].banderas["L_F"]
    bandera.poner(True)

    assert formulario.pestanas[3].leer()["L_F"] == tablas.LF_L3


def test_los_animales_deciden_la_perdida_por_lesiones_en_r4(formulario):
    # Tabla C.12: L_T = 1e-2 solo en estructuras con animales.
    pestana = formulario.pestanas[4]
    bandera, _ = pestana.banderas["L_T"]
    pestana.campos["L_F"].poner_llave("otros")

    assert pestana.leer()["L_T"] == 0
    bandera.poner(True)
    assert pestana.leer()["L_T"] == tablas.LT_L4


def test_la_perdida_por_falla_de_sistemas_en_r1_es_opcional(formulario):
    # Sin explosión ni sistemas vitales, R_C/R_M/R_W/R_Z no intervienen en R1
    # (numeral 4.3), así que esta pérdida puede no aplicar.
    assert formulario.pestanas[1].campos["L_O"].opcional is True
    assert formulario.pestanas[1].campos["L_O"].valor() == 0


def test_lo_obligatorio_de_r1_si_avisa(formulario):
    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.pestanas[1].leer()

    mensaje = str(fallo.value)
    assert "Pérdida por daño físico (L_F)" in mensaje
    assert "Daño especial (h_z)" in mensaje


# ---------------------------------------------------------------------------
# La bandera de la nota "a" de la Tabla C.11
# ---------------------------------------------------------------------------

def test_r4_arranca_comparando_contra_el_valor_representativo(formulario):
    # Al revés que la dataclass: con todos los valores economicos en 0, sin
    # esta bandera R4 daria 0 y parecería que no hay riesgo.
    pestana = formulario.pestanas[4]
    pestana.campos["L_F"].poner_llave("otros")

    assert pestana.leer()["razones_l4_unitarias"] is True


# ---------------------------------------------------------------------------
# Las cuatro zonas, y el número de la norma
# ---------------------------------------------------------------------------

def _llenar_casa_rural(formulario, zona_json):
    formulario.comun.poner(zona_json)
    r1 = formulario.pestanas[1]
    r1.campos["L_T"].poner(zona_json.L_T)
    r1.campos["L_F"].poner_valor(zona_json.L_F)
    r1.campos["h_z"].poner_valor(zona_json.h_z)


def test_zonas_por_tipo_devuelve_cuatro_zonas(formulario, caso_casa_rural):
    _llenar_casa_rural(formulario, caso_casa_rural["zonas"][0])
    formulario.pestanas[4].campos["L_F"].poner_llave("otros")

    zonas = formulario.zonas_por_tipo()

    assert sorted(zonas) == [1, 2, 3, 4]
    assert all(isinstance(z, Zona) for z in zonas.values())
    # Lo común se repite en las cuatro; lo que cambia son las pérdidas
    assert {z.nombre for z in zonas.values()} == {caso_casa_rural["zonas"][0].nombre}
    assert zonas[1].L_F != zonas[2].L_F


def test_la_zona_de_la_casa_rural_da_el_riesgo_de_la_norma(formulario, caso_casa_rural):
    # Anexo E.2: R1 = 2,506e-5. Ahora sale de la pantalla, no del JSON.
    _llenar_casa_rural(formulario, caso_casa_rural["zonas"][0])
    formulario.pestanas[4].campos["L_F"].poner_llave("otros")

    zona1 = formulario.zonas_por_tipo()[1]
    r = riesgos.evaluar(caso_casa_rural["estructura"], caso_casa_rural["lineas"],
                        [zona1], caso_casa_rural["N_G"], tipos=(1,))[1]

    assert r["total"] == approx(2.506e-5, rel=0.01)
    assert r["cumple"] is False


def test_lo_que_falta_dice_de_que_riesgo_es(formulario):
    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.zonas_por_tipo()

    mensaje = str(fallo.value)
    assert "Nombre de la zona" in mensaje          # de la parte común
    assert "R1 Vidas humanas" in mensaje           # y de la pestaña
    assert "R4 Económica" in mensaje


def test_las_cuatro_zonas_van_y_vuelven(formulario, caso_casa_rural):
    _llenar_casa_rural(formulario, caso_casa_rural["zonas"][0])
    formulario.pestanas[4].campos["L_F"].poner_llave("otros")
    antes = formulario.zonas_por_tipo()

    formulario.poner(antes)

    assert formulario.zonas_por_tipo() == antes