"""
Paso 47a: la lista de formularios, y los sistemas internos de la zona.

Es la pieza que permite tener VARIOS de algo. Sin ella la pantalla solo
podía con un sistema interno, una zona y una línea, que es de donde sale la
limitación H19.

La prueba que cierra el paso arma la zona de la casa rural con sus DOS
sistemas internos desde la pantalla y comprueba que el riesgo sigue dando
el 2,506e-5 del Anexo E.2.
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

from calculate_risk.norma import casos, riesgos                    # noqa: E402
from calculate_risk.norma.modelo import SistemaInterno             # noqa: E402
from ventanas import campos, formularios, listas                   # noqa: E402

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
def lista(raiz):
    return listas.ListaDeFormularios(
        raiz, formularios.FormularioSistemaInterno, singular="sistema")


# ---------------------------------------------------------------------------
# Añadir, quitar y leer
# ---------------------------------------------------------------------------

def test_arranca_vacia(lista):
    assert lista.leer() == []
    assert lista.nombres() == []


def test_anadir_deja_el_nuevo_seleccionado(lista):
    lista.anadir()
    lista.anadir()

    assert len(lista.formularios) == 2
    assert lista.seleccionado() == 1


def test_los_nombres_salen_de_cada_formulario(lista):
    lista.anadir(SistemaInterno("potencia"))
    lista.anadir(SistemaInterno("telefonia"))

    assert lista.nombres() == ["potencia", "telefonia"]


def test_uno_sin_nombre_se_rotula_pero_no_rompe(lista):
    lista.anadir()

    assert lista.nombres() == ["(sistema sin nombre)"]


def test_quitar_saca_el_seleccionado(lista):
    for nombre in ("a", "b", "c"):
        lista.anadir(SistemaInterno(nombre))
    lista.lista.selection_clear(0, "end")
    lista.lista.selection_set(1)

    lista.quitar()

    assert lista.nombres() == ["a", "c"]


def test_quitar_sin_seleccion_no_hace_nada(lista):
    lista.anadir(SistemaInterno("a"))
    lista.lista.selection_clear(0, "end")

    lista.quitar()

    assert len(lista.formularios) == 1


def test_una_lista_con_minimo_no_se_queda_vacia(raiz):
    con_minimo = listas.ListaDeFormularios(
        raiz, formularios.FormularioSistemaInterno, singular="zona", minimo=1)
    con_minimo.anadir(SistemaInterno("unica"))

    with pytest.raises(campos.DatoFaltante, match="al menos 1 zona"):
        con_minimo.quitar()


def test_poner_reemplaza_todo_lo_que_haya(lista, caso):
    lista.anadir(SistemaInterno("se_va"))

    lista.poner(caso["zonas"][0].sistemas_internos)

    assert lista.nombres() == ["pot", "tel"]
    assert lista.leer() == caso["zonas"][0].sistemas_internos


def test_si_falta_algo_dice_en_cual_de_los_elementos(lista):
    lista.anadir(SistemaInterno("bueno", K_S3=1, U_W=2.5, P_DPS=1))
    lista.anadir()      # este queda sin nada

    with pytest.raises(campos.DatoFaltante) as fallo:
        lista.leer()

    mensaje = str(fallo.value)
    assert "Sistema 2" in mensaje
    assert "Sistema 1" not in mensaje


# ---------------------------------------------------------------------------
# Solo se ve el formulario del elemento seleccionado
# ---------------------------------------------------------------------------

def test_solo_se_ve_el_formulario_del_seleccionado(lista):
    primero = lista.anadir(SistemaInterno("a"))
    segundo = lista.anadir(SistemaInterno("b"))

    assert segundo.winfo_manager() == "grid"
    assert primero.winfo_manager() == ""      # grid_remove lo deja sin gestor


# ---------------------------------------------------------------------------
# La zona ya admite varios sistemas internos
# ---------------------------------------------------------------------------

def test_la_zona_tiene_su_lista_de_sistemas(raiz):
    zona = formularios.FormularioZona(raiz)

    assert isinstance(zona.sistemas, listas.ListaDeFormularios)
    assert zona.cuaderno.tab(4, "text") == "Sistemas internos"


def test_la_casa_rural_con_sus_dos_sistemas_da_el_riesgo_de_la_norma(raiz, caso):
    # Anexo E.2: R1 = 2,506e-5, con dos sistemas internos en la zona.
    original = caso["zonas"][0]
    zona = formularios.FormularioZona(raiz)
    zona.poner({1: original, 2: original, 3: original, 4: original})
    zona.pestanas[4].campos["L_F"].poner_llave("otros")

    assert zona.sistemas.nombres() == ["pot", "tel"]
    zona1 = zona.zonas_por_tipo()[1]
    assert len(zona1.sistemas_internos) == 2

    r = riesgos.evaluar(caso["estructura"], caso["lineas"], [zona1],
                        caso["N_G"], tipos=(1,))[1]
    assert r["total"] == approx(2.506e-5, rel=0.01)


def test_si_un_sistema_esta_a_medias_la_zona_lo_dice(raiz, caso):
    original = caso["zonas"][0]
    zona = formularios.FormularioZona(raiz)
    zona.poner({1: original, 2: original, 3: original, 4: original})
    zona.pestanas[4].campos["L_F"].poner_llave("otros")
    zona.sistemas.anadir()          # uno nuevo, vacío

    with pytest.raises(campos.DatoFaltante) as fallo:
        zona.zonas_por_tipo()

    assert "Sistemas internos" in str(fallo.value)
    assert "Sistema 3" in str(fallo.value)