"""

Las pérdidas de la zona cambian con el tipo de riesgo (R1 a R4), así que van
aparte, en el 45b. Lo que se prueba aquí es que el reparto entre lo común y
lo que va por riesgo cubra TODOS los campos de la dataclass Zona, y que K_S1
y K_S2 salgan de la fórmula (B.5) y no de una lista inventada.
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

from calculate_risk.norma import casos, probabilidades, tablas      # noqa: E402
from calculate_risk.norma.modelo import SistemaInterno, Zona        # noqa: E402
from ventanas import campos, formularios                            # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def zona_casa_rural():
    return casos.cargar_caso(RUTA_CASA_RURAL)["zonas"][0]


def _zona_valida(**cambios) -> Zona:
    """Una zona cuyos factores SÍ son filas de las tablas.

    Los valores por defecto de la dataclass son neutros (todo 1), no filas:
    r_t = 1 no existe en la Tabla C.3, que va de 10^-2 a 10^-5. Sirven para
    programar, no para que la pantalla los muestre como si fueran una opción.
    """
    base = dict(P_TA=tablas.PTA["sin_medidas"],
                P_TU=tablas.PTU["sin_medidas"],
                P_B=tablas.PB["sin_spcr"],
                r_t=tablas.N_SUPERFICIE["agricola_hormigon"],
                r_p=tablas.RP["sin_medidas"],
                r_f=tablas.RF["sin_riesgo"])
    base.update(cambios)
    return Zona("prueba", **base)


# ---------------------------------------------------------------------------
# El reparto común / por riesgo cubre toda la dataclass
# ---------------------------------------------------------------------------

def test_entre_lo_comun_y_lo_de_cada_riesgo_estan_todos_los_campos():
    del_modelo = {campo.name for campo in fields(Zona)}
    del_formulario = set(formularios.COMUNES)
    for nombres in formularios.POR_TIPO.values():
        del_formulario |= set(nombres)

    assert del_formulario == del_modelo


def test_ningun_campo_por_riesgo_esta_tambien_en_lo_comun():
    for tipo, nombres in formularios.POR_TIPO.items():
        repetidos = set(nombres) & set(formularios.COMUNES)

        assert repetidos == set(), f"R{tipo} repite {repetidos}"


# ---------------------------------------------------------------------------
# Sistema interno: aquí cae H17
# ---------------------------------------------------------------------------

def test_el_formulario_del_sistema_pregunta_todos_sus_campos(raiz):
    formulario = formularios.FormularioSistemaInterno(raiz)
    del_modelo = {campo.name for campo in fields(SistemaInterno)}

    assert set(formulario.campos) == del_modelo


def test_el_dps_se_elige_solo_no_sale_del_nivel_del_spcr(raiz):
    # H17: la pantalla vieja deducía P_DPS del SPCR. Aquí es la Tabla B.3.
    formulario = formularios.FormularioSistemaInterno(raiz)

    assert formulario.campos["P_DPS"].valores == list(tablas.PDPS.values())
    formulario.campos["P_DPS"].poner_llave("npr_I")

    assert formulario.campos["P_DPS"].valor() == tablas.PDPS["npr_I"]


def test_el_sistema_de_la_casa_rural_va_y_vuelve(raiz, zona_casa_rural):
    original = zona_casa_rural.sistemas_internos[0]
    formulario = formularios.FormularioSistemaInterno(raiz, sistema=original)

    assert formulario.leer() == original


def test_un_sistema_sin_nombre_avisa(raiz):
    formulario = formularios.FormularioSistemaInterno(raiz)
    formulario.campos["K_S3"].poner_llave("sin_blindar_sin_precauciones")
    formulario.campos["P_DPS"].poner_llave("sin_dps_coordinado")

    with pytest.raises(campos.DatoFaltante, match="Falta Nombre"):
        formulario.leer()


def test_la_linea_puede_ir_vacia(raiz):
    # linea="" significa "lo alimentan todas las líneas" (Paso 36b).
    formulario = formularios.FormularioSistemaInterno(
        raiz, sistema=SistemaInterno("equipos"))

    assert formulario.leer().linea == ""


# ---------------------------------------------------------------------------
# Parte común de la zona
# ---------------------------------------------------------------------------

def test_lo_comun_devuelve_exactamente_los_campos_comunes(raiz, zona_casa_rural):
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(zona_casa_rural)

    assert set(formulario.leer()) == set(formularios.COMUNES)


def test_la_parte_comun_de_la_casa_rural_va_y_vuelve(raiz, zona_casa_rural):
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(zona_casa_rural)

    leido = formulario.leer()
    for nombre in formularios.COMUNES:
        assert leido[nombre] == getattr(zona_casa_rural, nombre), nombre


def test_sin_apantallamiento_k_s_vale_uno(raiz):
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(_zona_valida())

    leido = formulario.leer()
    assert leido["K_S1"] == 1 and leido["K_S2"] == 1


def test_con_apantallamiento_k_s_sale_de_la_formula(raiz):
    # ec. (B.5): K_S1 = 0,12 x w_m1. Con malla de 2 m da 0,24.
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(_zona_valida())
    formulario.blindaje.poner(True)
    formulario.w_m1.poner(2)
    formulario.w_m2.poner(0.5)

    leido = formulario.leer()
    assert leido["K_S1"] == probabilidades.k_s1(2)
    assert leido["K_S2"] == probabilidades.k_s2(0.5)


def test_el_ancho_de_malla_vuelve_desde_un_caso_guardado(raiz):
    # El caso guarda K_S, no el ancho: hay que poder deshacer la fórmula.
    original = _zona_valida(K_S1=probabilidades.k_s1(2.5),
                            K_S2=probabilidades.k_s2(1.0))
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(original)

    assert formulario.blindaje.valor() is True
    assert formulario.w_m1.valor() == pytest.approx(2.5)
    leido = formulario.leer()
    assert leido["K_S1"] == original.K_S1 and leido["K_S2"] == original.K_S2


def test_las_horas_de_presencia_no_pasan_de_un_ano(raiz):
    formulario = formularios.FormularioZonaComun(raiz)
    formulario.poner(_zona_valida())
    formulario.campos["t_z"].poner(9000)

    with pytest.raises(campos.DatoFaltante, match="mayor que 8760"):
        formulario.leer()


def test_una_zona_recien_abierta_no_trae_nada_elegido(raiz):
    formulario = formularios.FormularioZonaComun(raiz)

    with pytest.raises(campos.DatoFaltante) as fallo:
        formulario.leer()

    mensaje = str(fallo.value)
    for falta in ("Nombre de la zona", "Superficie del piso (r_t)",
                  "Riesgo de incendio (r_f)"):
        assert falta in mensaje


def test_el_r_t_por_defecto_del_modelo_no_es_fila_de_la_tabla(raiz):
    """Queda escrito porque es un tropiezo real al armar la pantalla.

    Zona() trae r_t = 1, que es "sin reducción" y sirve como valor neutro
    para programar, pero la Tabla C.3 solo tiene 10^-2, 10^-3, 10^-4 y 10^-5.
    Por eso una zona recién creada NO se puede volcar en el formulario: hay
    que elegir la superficie. Es lo correcto, no un defecto.
    """
    formulario = formularios.FormularioZonaComun(raiz)

    assert 1 not in tablas.N_SUPERFICIE.values()
    with pytest.raises(campos.DatoFaltante, match="Tabla C.3"):
        formulario.poner(Zona("recien_creada"))