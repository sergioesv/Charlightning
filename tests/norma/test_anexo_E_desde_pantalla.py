"""
Paso 51b: los cuatro ejemplos del Anexo E, planteados DESDE LA PANTALLA.

Es el primer criterio del Hito F. Hasta ahora los ejemplos se armaban en
Python y se le pasaban al motor; aquí cada caso se mete en la pantalla, se
vuelve a leer de los widgets y se calcula. Si el formulario no pudiera
expresar algún dato, la lectura fallaría o el número saldría distinto.

E.3 y E.4 son los que de verdad prueban H19: cinco y cuatro zonas.

Sobre las zonas exteriores (Z1 y Z2 del E.3, Z1 del E.4): la norma las
evalúa sin las líneas, porque a un patio no llega una línea que alguien
pueda tocar. En el modelo eso se dice con P_TU = 0, que es una fila de la
Tabla B.6 ("restricciones físicas"), y da los mismos números que publica la
norma. No hace falta ningún caso especial.
"""
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

from calculate_risk.norma import casos                                  # noqa: E402
from calculate_risk.norma.modelo import (Estructura, Linea,             # noqa: E402
                                         SistemaInterno, Zona)
from ventanas import editor_caso                                        # noqa: E402

E5 = 1e-5


def cercano(calculado, esperado, tol_abs=0.0015) -> bool:
    """En unidades de 1e-5; medio dígito de la norma o 1 %, lo que sea mayor."""
    return abs(calculado / E5 - esperado) <= max(tol_abs, 0.011 * abs(esperado))


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


def _por_la_pantalla(raiz, caso):
    """Mete el caso en la pantalla, lo lee de los widgets y lo evalúa."""
    editor = editor_caso.EditorCaso(raiz)
    editor.poner_caso(caso, tipo=1)
    return editor, editor.evaluar(tipos=(1,))[1]


# ---------------------------------------------------------------------------
# Los cuatro casos, tal como los define la norma
# ---------------------------------------------------------------------------

def casa_rural():
    """E.2 — 15 x 20 x 6 m, una zona, dos líneas. Total publicado: 2,51."""
    return casos.cargar_caso("casos/casa_rural.json")


def oficinas():
    """E.3 — cinco zonas, dos de ellas exteriores. Total publicado: 9,65."""
    est = Estructura(L=20, W=40, H=25, C_D=1, n_t=200)
    pot = Linea("potencia", L_L=200, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                C_LD=1, C_LI=1, P_LD=1, P_LI=0.3, P_EB=1.0)
    tel = Linea("telecom", L_L=1000, C_I=0.5, C_T=1, C_E=1, U_W=1.5,
                C_LD=1, C_LI=1, P_LD=1, P_LI=0.5, P_EB=1.0)

    def sistemas():
        return [SistemaInterno("pot", "potencia", K_S3=0.2, U_W=2.5),
                SistemaInterno("tel", "telecom", K_S3=1.0, U_W=1.5)]

    comun = dict(P_B=1.0, L_T=1e-2, t_z=8760)
    dentro = dict(r_t=1e-5, h_z=2, L_F=0.02, sistemas_internos=None, **comun)
    zonas = [
        Zona("Z1", r_t=1e-3, P_TA=1, P_TU=0, r_f=0, n_z=4, **comun),
        Zona("Z2", r_t=1e-2, P_TA=0, P_TU=0, r_f=0, n_z=2, **comun),
        Zona("Z3", r_f=1e-1, n_z=20, **{**dentro, "sistemas_internos": sistemas()}),
        Zona("Z4", r_f=1e-3, n_z=160, **{**dentro, "sistemas_internos": sistemas()}),
        Zona("Z5", r_f=1e-3, n_z=14, **{**dentro, "sistemas_internos": sistemas()}),
    ]
    return {"estructura": est, "lineas": [pot, tel], "zonas": zonas, "N_G": 4.0}


def hospital():
    """E.4 — cuatro zonas y estructura vecina en la línea. Publicado: 69,96."""
    est = Estructura(L=50, W=150, H=10, C_D=1, n_t=1000, c_t=90.0,
                     riesgo_explosion_o_vital=True)
    pot = Linea("potencia", L_L=500, C_I=0.5, C_T=0.2, C_E=0.5, U_W=2.5,
                C_LD=1, C_LI=0, P_LD=0.2, P_LI=0.3, P_EB=1.0)
    tel = Linea("telecom", L_L=300, C_I=0.5, C_T=1, C_E=0.5, U_W=1.5,
                C_LD=1, C_LI=0, P_LD=0.8, P_LI=0.5, P_EB=1.0,
                adyacente=Estructura(L=20, W=30, H=5), C_DJ=1)

    def sistemas():
        return [SistemaInterno("pot", "potencia", K_S3=0.2, U_W=2.5),
                SistemaInterno("tel", "telecom", K_S3=0.01, U_W=1.5)]

    dentro = dict(r_t=1e-5, h_z=5, L_T=1e-2, L_F=1e-1)
    zonas = [
        Zona("Z1", r_t=1e-2, P_TU=0, r_f=0, L_T=1e-2, n_z=10),
        Zona("Z2", r_f=1e-2, L_O=1e-3, n_z=950, sistemas_internos=sistemas(), **dentro),
        Zona("Z3", r_f=1e-3, L_O=1e-2, n_z=35, sistemas_internos=sistemas(), **dentro),
        Zona("Z4", r_f=1e-3, L_O=1e-2, n_z=5, sistemas_internos=sistemas(), **dentro),
    ]
    return {"estructura": est, "lineas": [pot, tel], "zonas": zonas, "N_G": 4.0}


def apartamentos():
    """E.5 — una zona; el escenario H=20 m, r_f=0,01, sin SPCR: 8,364."""
    est = Estructura(L=30, W=20, H=20, C_D=1, n_t=200)
    pot = Linea("potencia", L_L=200, C_I=0.5, C_T=1, C_E=0.5, U_W=2.5,
                P_LI=0.3, P_EB=1)
    tel = Linea("telecom", L_L=100, C_I=0.5, C_T=1, C_E=0.5, U_W=1.5,
                P_LI=0.5, P_EB=1)
    zona = Zona("Z2", r_t=1e-5, P_B=1, r_f=1e-2, r_p=1, L_T=1e-2, L_F=0.1, n_z=200)
    return {"estructura": est, "lineas": [pot, tel], "zonas": [zona], "N_G": 4.0}


EJEMPLOS = [
    ("E.2 casa rural", casa_rural, 2.506, 1),
    ("E.3 oficinas", oficinas, 9.65, 5),
    ("E.4 hospital", hospital, 69.96, 4),
    ("E.5 apartamentos", apartamentos, 8.364, 1),
]


# ---------------------------------------------------------------------------
# El criterio del Hito F
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nombre, construir, publicado, cuantas_zonas", EJEMPLOS)
def test_el_ejemplo_da_el_valor_publicado_desde_la_pantalla(
        raiz, nombre, construir, publicado, cuantas_zonas):
    caso = construir()

    editor, r = _por_la_pantalla(raiz, caso)

    assert len(editor.zonas.formularios) == cuantas_zonas, nombre
    assert cercano(r["total"], publicado, tol_abs=0.05), (
        f"{nombre}: la pantalla da {r['total'] / E5:.3f} y la norma {publicado}")


@pytest.mark.parametrize("nombre, construir, publicado, cuantas_zonas", EJEMPLOS)
def test_la_pantalla_devuelve_el_caso_sin_cambiarlo(
        raiz, nombre, construir, publicado, cuantas_zonas):
    # Si algún dato no cupiera en los formularios, saldría distinto al leerlo.
    caso = construir()

    editor, _ = _por_la_pantalla(raiz, caso)
    leido = editor.casos_por_tipo(tipos=(1,))[1]

    assert leido["estructura"] == caso["estructura"], nombre
    assert leido["lineas"] == caso["lineas"], nombre
    assert leido["zonas"] == caso["zonas"], nombre
    assert leido["N_G"] == caso["N_G"], nombre


# ---------------------------------------------------------------------------
# Los componentes por zona, no solo el total
# ---------------------------------------------------------------------------

def test_las_oficinas_dan_los_componentes_publicados(raiz):
    _, r = _por_la_pantalla(raiz, oficinas())
    z = r["zonas"]

    assert cercano(z["Z1"]["R_A"], 0.002)
    assert cercano(z["Z2"]["R_A"], 0.0)
    assert cercano(z["Z3"]["R_B"], 4.395)
    assert cercano(z["Z3"]["R_V"], 4.480)
    assert cercano(z["Z4"]["R_B"], 0.352)
    assert cercano(z["Z5"]["R_B"], 0.031)


def test_el_hospital_da_los_componentes_publicados(raiz):
    _, r = _por_la_pantalla(raiz, hospital())
    z = r["zonas"]

    assert cercano(z["Z1"]["R_A"], 0.009)
    assert cercano(z["Z2"]["R_B"], 42.4, tol_abs=0.05)
    assert cercano(z["Z2"]["R_V"], 9.21)
    assert cercano(z["Z2"]["R_C"], 8.484)
    assert cercano(z["Z2"]["R_M"], 2.413)
    assert cercano(z["Z3"]["R_C"], 3.126)
    assert cercano(z["Z4"]["R_C"], 0.447)


def test_la_estructura_vecina_del_hospital_llega_a_la_pantalla(raiz):
    editor, _ = _por_la_pantalla(raiz, hospital())

    telecom = editor.casos_por_tipo(tipos=(1,))[1]["lineas"][1]

    assert telecom.adyacente == Estructura(L=20, W=30, H=5)
    assert editor.lineas.formularios[1].hay_adyacente.valor() is True


# ---------------------------------------------------------------------------
# Las zonas exteriores, sin caso especial
# ---------------------------------------------------------------------------

def test_una_zona_exterior_se_dice_con_p_tu_igual_a_cero(raiz):
    # La norma las evalúa sin líneas. P_TU = 0 (Tabla B.6) da lo mismo y es
    # una fila de verdad, así que se puede elegir en la pantalla.
    _, r = _por_la_pantalla(raiz, oficinas())

    assert r["zonas"]["Z1"]["R_U"] == 0
    assert r["zonas"]["Z1"]["R_A"] > 0      # pero sí hay personas afuera


def test_una_zona_exterior_no_tiene_dano_fisico_que_perder(raiz):
    # L_F = 0: en un patio no hay nada que se queme. Por eso la pérdida por
    # daño físico admite "no aplica" en el formulario.
    editor, r = _por_la_pantalla(raiz, oficinas())

    assert editor.zonas.formularios[0].pestanas[1].campos["L_F"].valor() == 0
    assert r["zonas"]["Z1"]["R_B"] == 0