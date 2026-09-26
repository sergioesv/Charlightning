"""
Paso 43: los campos reutilizables de la pantalla nueva.

Los widgets se construyen de verdad, pero sin abrir ventana: Tk() sin
mainloop basta para crearlos y leerlos. Si la máquina no tiene pantalla
gráfica (ni Xvfb), las pruebas se saltan en vez de fallar.
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

from ventanas import campos            # noqa: E402  (después del skipif)


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


# ---------------------------------------------------------------------------
# CampoNumero: el que impide el error de la casilla vacía
# ---------------------------------------------------------------------------

def test_una_casilla_vacia_avisa_en_vez_de_devolver_cero(raiz):
    # Es EL error de la pantalla vieja: con la DDT vacía calculaba con 0.
    campo = campos.CampoNumero(raiz, "Densidad de descargas", fila=0)

    with pytest.raises(campos.DatoFaltante, match="Falta Densidad"):
        campo.valor()


def test_el_texto_que_no_es_numero_tambien_avisa(raiz):
    campo = campos.CampoNumero(raiz, "Altura", fila=0, valor="tres metros")

    with pytest.raises(campos.DatoFaltante, match="no es un número"):
        campo.valor()


def test_acepta_coma_como_separador_decimal(raiz):
    campo = campos.CampoNumero(raiz, "Altura", fila=0, valor="2,5")

    assert campo.valor() == 2.5


def test_respeta_el_minimo_y_el_maximo(raiz):
    largo = campos.CampoNumero(raiz, "Longitud", fila=0, valor=0, minimo=0.001)
    prob = campos.CampoNumero(raiz, "Probabilidad", fila=1, valor=2, maximo=1)

    with pytest.raises(campos.DatoFaltante, match="menor que"):
        largo.valor()
    with pytest.raises(campos.DatoFaltante, match="mayor que"):
        prob.valor()


def test_el_rotulo_se_pone_rojo_y_se_limpia_al_corregir(raiz):
    campo = campos.CampoNumero(raiz, "Ancho", fila=0)

    with pytest.raises(campos.DatoFaltante):
        campo.valor()
    assert campo.en_error

    campo.poner(10)
    assert not campo.en_error
    assert campo.valor() == 10


# ---------------------------------------------------------------------------
# CampoTabla: el valor sale de tablas.py, nunca de la pantalla
# ---------------------------------------------------------------------------

def test_la_lista_muestra_las_filas_de_la_tabla(raiz):
    campo = campos.CampoTabla(raiz, "CE", fila=0)

    assert list(campo.combo.cget("values")) == [
        campos.CampoTabla.SIN_ELEGIR,
        "Rural", "Suburbano", "Urbano", "Urbano con edificios altos"]


def test_sin_elegir_avisa_igual_que_una_casilla_vacia(raiz):
    # Si arrancara en la primera fila, la Tabla A.1 dejaría C_D = 0,25 puesto
    # solo: la fila más favorable, cuatro veces menos N_D que la casa rural.
    campo = campos.CampoTabla(raiz, "CD", fila=0)

    with pytest.raises(campos.DatoFaltante, match="Falta elegir"):
        campo.valor()
    assert campo.en_error


def test_elegir_una_fila_devuelve_el_valor_de_esa_fila(raiz):
    from calculate_risk.norma import tablas

    campo = campos.CampoTabla(raiz, "CE", fila=0)
    for indice, llave in enumerate(campo.llaves):
        campo.combo.current(indice + 1)     # el 0 es "— elegir —"

        assert campo.valor() == tablas.CE[llave]
        assert campo.llave() == llave

def test_el_urbano_con_edificios_altos_vale_lo_que_dice_la_tabla(raiz):
    # La pantalla vieja ponía 0 aquí y anulaba N_L y N_I.
    campo = campos.CampoTabla(raiz, "CE", fila=0, inicial="urbano_edificios_altos")

    assert campo.valor() == 0.01


def test_cld_cli_entrega_los_dos_factores(raiz):
    campo = campos.CampoTabla(raiz, "CLD_CLI", fila=0,
                              inicial="potencia_multi_puesta_a_tierra_neutro")

    assert campo.valor() == {"CLD": 1, "CLI": 0.2}


def test_se_puede_reponer_desde_el_valor_guardado(raiz):
    # Al abrir un caso guardado solo se tiene el valor, no la fila.
    campo = campos.CampoTabla(raiz, "HZ", fila=0)
    campo.poner_valor(5)

    assert campo.llave() == "panico_medio_o_dificultad_evacuacion"


def test_un_valor_que_no_esta_en_la_tabla_avisa(raiz):
    # La pantalla vieja ofrecía h_z = 20 y 50, que no son filas de la C.6.
    campo = campos.CampoTabla(raiz, "HZ", fila=0)

    with pytest.raises(campos.DatoFaltante, match="Tabla C.6"):
        campo.poner_valor(20)


def test_el_rotulo_por_defecto_sale_del_nombre_de_la_tabla(raiz):
    campo = campos.CampoTabla(raiz, "RF", fila=0)

    assert campo.etiqueta == "Riesgo de incendio o de explosión"


# ---------------------------------------------------------------------------
# CampoSiNo y recoger()
# ---------------------------------------------------------------------------

def test_la_casilla_de_verificacion_va_y_viene(raiz):
    campo = campos.CampoSiNo(raiz, "Hay animales", fila=0)

    assert campo.valor() is False
    campo.poner(True)
    assert campo.valor() is True


def test_recoger_devuelve_todo_junto(raiz):
    grupo = {
        "L": campos.CampoNumero(raiz, "Longitud", fila=0, valor=20),
        "C_D": campos.CampoTabla(raiz, "CD", fila=1, inicial="aislada"),
        "animales": campos.CampoSiNo(raiz, "Hay animales", fila=2, valor=True),
    }

    assert campos.recoger(grupo) == {"L": 20.0, "C_D": 1, "animales": True}


def test_recoger_reporta_TODO_lo_que_falta_de_una_vez(raiz):
    grupo = {
        "L": campos.CampoNumero(raiz, "Longitud", fila=0),
        "W": campos.CampoNumero(raiz, "Ancho", fila=1),
        "H": campos.CampoNumero(raiz, "Altura", fila=2, valor=5),
    }

    with pytest.raises(campos.DatoFaltante) as fallo:
        campos.recoger(grupo)

    mensaje = str(fallo.value)
    assert "Falta Longitud" in mensaje and "Falta Ancho" in mensaje
    assert "Altura" not in mensaje
    assert grupo["L"].en_error and not grupo["H"].en_error