"""
La prueba que más vale es test_el_formulario_pregunta_todos_los_campos:
compara los nombres del formulario con los campos de la dataclass. Si el
modelo gana un campo y la pantalla no lo pregunta, falla — que es la clase
de hueco por el que existen las limitaciones H16-H19.
"""
from dataclasses import fields

import pytest

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

from calculate_risk.norma import casos                    # noqa: E402
from calculate_risk.norma.modelo import Estructura        # noqa: E402
from ventanas import campos, formularios                  # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def formulario(raiz):
    return formularios.FormularioEstructura(raiz)


# ---------------------------------------------------------------------------
# Que el formulario y el modelo no se separen
# ---------------------------------------------------------------------------

def test_el_formulario_pregunta_todos_los_campos(formulario):
    del_modelo = {campo.name for campo in fields(Estructura)}

    assert set(formulario.campos) == del_modelo


def test_los_valores_iniciales_son_los_de_la_dataclass(formulario):
    d = formularios.por_defecto(Estructura)

    assert formulario.campos["H_p"].valor() == d["H_p"]
    assert formulario.campos["n_t"].valor() == d["n_t"]
    assert formulario.campos["c_t"].valor() == d["c_t"]
    assert formulario.campos["hay_animales"].valor() is d["hay_animales"]


# ---------------------------------------------------------------------------
# Contra el caso resuelto de la norma (Anexo E.2)
# ---------------------------------------------------------------------------

def test_la_casa_rural_sale_igual_que_su_json(formulario):
    del_json = casos.cargar_caso(RUTA_CASA_RURAL)["estructura"]

    formulario.campos["L"].poner(15)
    formulario.campos["W"].poner(20)
    formulario.campos["H"].poner(6)
    formulario.campos["n_t"].poner(5)
    formulario.campos["C_D"].poner_llave("aislada")

    assert formulario.leer() == del_json


def test_lo_que_se_pone_es_lo_que_se_lee(formulario):
    # Ida y vuelta: es lo que hace falta para abrir un caso guardado.
    original = Estructura(L=17.3, W=23.8, H=9.5, H_p=12.0, C_D=0.25,
                          n_t=340, c_t=2_500_000,
                          riesgo_explosion_o_vital=True, hay_animales=True)

    formulario.poner(original)

    assert formulario.leer() == original


# ---------------------------------------------------------------------------
# Que no se pueda calcular con datos que no están
# ---------------------------------------------------------------------------

def test_sin_dimensiones_no_devuelve_una_estructura_a_medias(formulario):
    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.leer()

    mensaje = str(fallo.value)
    for falta in ("Longitud (L)", "Ancho (W)", "Altura (H)"):
        assert falta in mensaje
    # y la localización tampoco viene puesta sola
    assert "Localización (C_D)" in mensaje


def test_una_dimension_en_cero_no_pasa(formulario):
    # Con L = 0 el área da cero y el riesgo da cero, sin decir nada.
    formulario.poner(Estructura(L=15, W=20, H=6))
    formulario.campos["L"].poner(0)

    with pytest.raises(campos.DatoFaltante, match="mayor que cero"):
        formulario.leer()


def test_una_dimension_negativa_tampoco(formulario):
    formulario.poner(Estructura(L=15, W=20, H=6))
    formulario.campos["H"].poner(-3)

    with pytest.raises(campos.DatoFaltante, match="mayor que cero"):
        formulario.leer()


def test_el_saliente_del_techo_si_puede_ser_cero(formulario):
    # H_p = 0 significa "no hay saliente"; areas.py lo trata así.
    formulario.poner(Estructura(L=15, W=20, H=6, H_p=0))

    assert formulario.leer().H_p == 0


# ---------------------------------------------------------------------------
# El factor de localización sale de la Tabla A.1
# ---------------------------------------------------------------------------

def test_la_localizacion_no_viene_elegida_de_fabrica(formulario):
    # La primera fila de la Tabla A.1 es C_D = 0,25, la más favorable: dejarla
    # puesta sola sería calcular con un factor que nadie eligió.
    from calculate_risk.norma import tablas

    campo = formulario.campos["C_D"]

    assert campo.valores == list(tablas.CD.values())
    with pytest.raises(campos.DatoFaltante, match="Falta elegir"):
        campo.valor()

    campo.poner_llave("aislada")
    assert campo.valor() == tablas.CD["aislada"]


def test_un_c_d_que_no_esta_en_la_tabla_avisa(formulario):
    with pytest.raises(campos.DatoFaltante, match="Tabla A.1"):
        formulario.poner(Estructura(L=15, W=20, H=6, C_D=0.75))