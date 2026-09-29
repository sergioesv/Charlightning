"""
Paso 51a: la ventana de la pantalla nueva.

Junta el editor y el panel de resultados. Lo que se prueba es el
comportamiento de los botones, no el dibujo: que Calcular llene el panel,
que Abrir y Guardar pasen por un archivo de verdad, que el Informe escriba
la memoria, y sobre todo que **nada de eso calcule con datos que faltan**.

Los messagebox bloquean esperando un clic, así que se reemplazan por una
lista donde quedan anotados: además de no colgar la prueba, permite
comprobar QUÉ le dijo el programa al usuario.
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

from ventanas import principal_norma                                # noqa: E402

RUTA_CASA_RURAL = "casos/casa_rural.json"


@pytest.fixture
def avisos(monkeypatch):
    """Lo que el programa le habría dicho al usuario."""
    dichos = []
    monkeypatch.setattr(principal_norma.messagebox, "showinfo",
                        lambda **kwargs: dichos.append(kwargs.get("message", "")))
    return dichos


@pytest.fixture
def raiz():
    ventana = tkinter.Tk()
    yield ventana
    ventana.destroy()


@pytest.fixture
def pantalla(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.abrir(RUTA_CASA_RURAL)
    return p


# ---------------------------------------------------------------------------
# La ventana está armada
# ---------------------------------------------------------------------------

def test_tiene_los_seis_botones(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)

    assert sorted(p.botones) == ["Abrir caso", "Calcular", "Caso nuevo",
                                 "Guardar caso", "Informe", "Volver"]


def test_arranca_evaluando_solo_el_riesgo_de_vidas(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)

    assert p.tipos() == (1,)


def test_se_pueden_marcar_mas_riesgos(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.marcas[4].set(True)

    assert p.tipos() == (1, 4)


def test_sin_ningun_riesgo_marcado_evalua_r1(raiz, avisos):
    p = principal_norma.PrincipalNorma(raiz)
    p.marcas[1].set(False)

    assert p.tipos() == (1,)


# ---------------------------------------------------------------------------
# Calcular
# ---------------------------------------------------------------------------

def test_calcular_da_el_riesgo_de_la_norma_y_llena_el_panel(pantalla):
    resultado = pantalla.calcular()

    assert resultado[1]["total"] == approx(2.506e-5, rel=0.01)
    filas = pantalla.resultados.filas()
    assert filas[0][4] == "No cumple"
    assert filas[1][1] == "Z2_interior"


def test_calcular_con_datos_a_medias_avisa_y_no_deja_resultados(pantalla, avisos):
    pantalla.editor.zonas.anadir()          # una zona nueva, vacía

    assert pantalla.calcular() is None
    assert pantalla.resultados.filas() == []
    assert "Zona 2" in avisos[-1]

def test_un_riesgo_marcado_sin_perdidas_lo_dice_y_no_calcula(pantalla, avisos):
    # Bug 4 (28-sep): la casa rural solo trae pérdidas de R1. Marcar R2 daba
    # R2 = 0 y «Cumple» sin haber evaluado nada.
    pantalla.marcas[2].set(True)

    assert pantalla.calcular() is None
    assert pantalla.resultados.filas() == []
    assert "R2 no tiene pérdidas cargadas" in avisos[-1]
    assert "R2 Servicio público" in avisos[-1]


def test_con_las_perdidas_cargadas_el_riesgo_si_se_calcula(pantalla):
    pantalla.marcas[4].set(True)
    _cargar_perdidas_r4(pantalla)

    resultado = pantalla.calcular()

    assert resultado[4]["total"] > 0

def test_volver_a_calcular_no_acumula(pantalla):
    pantalla.calcular()
    antes = len(pantalla.resultados.filas())

    pantalla.calcular()

    assert len(pantalla.resultados.filas()) == antes

# ---------------------------------------------------------------------------
# Caso nuevo (Paso 55)
# ---------------------------------------------------------------------------

def test_caso_nuevo_deja_la_pantalla_en_cero(pantalla):
    pantalla.calcular()

    assert pantalla.nuevo(confirmado=True) is True

    assert pantalla.editor.zonas.formularios == []
    assert pantalla.editor.lineas.formularios == []
    assert pantalla.editor.N_G.entrada.get() == ""
    assert pantalla.resultados.filas() == []
    assert pantalla.ultimo_calculo is None


def test_caso_nuevo_pregunta_antes_de_borrar(pantalla, monkeypatch):
    preguntas = []
    monkeypatch.setattr(principal_norma.messagebox, "askyesno",
                        lambda **kwargs: preguntas.append(kwargs) or False)
    pantalla.calcular()

    assert pantalla.nuevo() is False

    assert preguntas, "borrarlo todo sin preguntar, no"
    assert pantalla.editor.lineas.nombres() == ["potencia", "telecomunicacion"]
    assert pantalla.resultados.filas()          # el resultado sigue ahí


def test_despues_de_caso_nuevo_el_informe_no_escribe_nada(pantalla, tmp_path,
                                                          avisos):
    pantalla.calcular()
    pantalla.nuevo(confirmado=True)
    ruta = tmp_path / "informe.pdf"

    assert pantalla.informe(ruta) is None
    assert not ruta.exists()
    assert "al menos 1 zona" in avisos[-1]

# ---------------------------------------------------------------------------
# Abrir y guardar
# ---------------------------------------------------------------------------

def test_abrir_carga_el_caso_y_borra_los_resultados_viejos(pantalla):
    pantalla.calcular()

    pantalla.abrir(RUTA_CASA_RURAL)

    assert pantalla.editor.lineas.nombres() == ["potencia", "telecomunicacion"]
    assert pantalla.resultados.filas() == []


def test_abrir_un_archivo_que_no_existe_avisa_en_vez_de_caerse(pantalla, avisos):
    assert pantalla.abrir("no_existe.json") is None
    assert avisos            # le dijo algo al usuario


def test_guardar_y_volver_a_abrir_deja_el_mismo_riesgo(pantalla, tmp_path):
    antes = pantalla.calcular()[1]["total"]
    ruta = tmp_path / "caso.json"

    pantalla.guardar(ruta)
    pantalla.abrir(ruta)

    assert pantalla.calcular()[1]["total"] == approx(antes)


def test_no_se_guarda_un_caso_incompleto(pantalla, tmp_path, avisos):
    pantalla.editor.zonas.anadir()
    ruta = tmp_path / "no.json"

    assert pantalla.guardar(ruta) is None
    assert not ruta.exists()
    assert avisos


def test_cancelar_el_dialogo_no_hace_nada(pantalla, monkeypatch):
    monkeypatch.setattr(principal_norma.filedialog, "asksaveasfilename",
                        lambda **kwargs: "")

    assert pantalla.guardar() is None


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def _informe_de_mentira(monkeypatch, recibido, falla=None):
    """generar_informe sin generar nada: anota con qué lo llamaron. Así las pruebas
    de la pantalla no tardan lo que tarda buscar medidas."""
    def falso(carpeta, casos, por_tipo, **nombrados):
        recibido.update(carpeta=carpeta, casos=casos, por_tipo=por_tipo, **nombrados)
        recibido["aviso_abierto"] = _ventanita_de(nombrados["avance"]).winfo_exists()
        nombrados["avance"]("Componiendo el PDF…")
        if falla:
            raise falla
        return principal_norma.generar.Informe(
            ruta=f"{carpeta}/{nombrados['nombre']}.pdf", paginas=7)
    monkeypatch.setattr(principal_norma.generar, "generar_informe", falso)


def _ventanita_de(metodo):
    """La ventanita a la que pertenece el método avance (AvisoDeTrabajo.decir)."""
    return metodo.__self__


def test_el_informe_entrega_el_pdf(pantalla, tmp_path, avisos):
    # Bug 5 del 28-sep: sin LaTeX en el PC, el botón dejaba un .tex y nada más.
    pantalla.calcular()
    ruta = tmp_path / "informe.pdf"

    assert pantalla.informe(ruta) == str(ruta)

    assert ruta.read_bytes()[:4] == b"%PDF"
    assert [p.name for p in tmp_path.iterdir()] == ["informe.pdf"]
    assert "Informe generado" in avisos[-1] and str(ruta) in avisos[-1]


def test_mientras_trabaja_hay_un_aviso_y_despues_se_cierra(pantalla, tmp_path,
                                                          avisos, monkeypatch):
    recibido = {}
    _informe_de_mentira(monkeypatch, recibido)

    pantalla.informe(tmp_path / "informe.pdf")

    assert recibido["aviso_abierto"]
    assert pantalla.aviso_de_trabajo.winfo_exists() == 0
    assert recibido["nombre"] == "informe"


def test_si_el_pdf_no_se_puede_escribir_lo_dice(pantalla, tmp_path, avisos, monkeypatch):
    # En Windows pasa cuando el PDF anterior sigue abierto en el lector.
    _informe_de_mentira(monkeypatch, {}, falla=PermissionError("Permiso denegado"))

    assert pantalla.informe(tmp_path / "informe.pdf") is None

    assert "No se pudo escribir el PDF" in avisos[-1]
    assert pantalla.aviso_de_trabajo.winfo_exists() == 0


def test_el_informe_calcula_el_solo(pantalla, tmp_path):
    # Sin haber pulsado Calcular, el Informe tiene que calcular por su cuenta.
    # Desde el Paso 53 recalcula SIEMPRE antes de escribir, para no sacar un
    # documento con las entradas nuevas y los riesgos viejos.
    ruta = tmp_path / "informe.pdf"

    pantalla.informe(ruta)

    assert pantalla.ultimo_calculo is not None
    assert ruta.exists()


def test_sin_datos_no_hay_informe(raiz, tmp_path, avisos):
    vacia = principal_norma.PrincipalNorma(raiz)
    ruta = tmp_path / "informe.pdf"

    assert vacia.informe(ruta) is None
    assert not ruta.exists()


# ---------------------------------------------------------------------------
# Ejemplos de la norma
# ---------------------------------------------------------------------------

def test_el_menu_trae_los_cuatro_ejemplos_del_anexo_E(pantalla):
    menu = pantalla.menu_ejemplos
    textos = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1)]

    assert len(textos) == 4
    assert textos[0].startswith("E.2")
    assert textos[3].startswith("E.5")


@pytest.mark.parametrize("archivo, publicado", [
    ("casa_rural.json", 2.506e-5),
    ("E3_oficinas.json", 9.65e-5),
    ("E4_hospital.json", 69.96e-5),
    ("E5_apartamentos.json", 8.364e-5),
])
def test_cada_ejemplo_se_abre_y_da_el_valor_publicado(pantalla, archivo, publicado):
    # Es el criterio 1 del Hito G y, de paso, la prueba de que los JSON que
    # reparte el programa son los del Anexo E y no una copia que se quedó atrás.
    pantalla.abrir_ejemplo(archivo)

    assert pantalla.calcular()[1]["total"] == approx(publicado, rel=0.011)


def test_los_ejemplos_no_dependen_de_donde_se_arranco_el_programa(
        pantalla, tmp_path, monkeypatch):
    # La carpeta se busca al lado del código: desde cualquier directorio.
    monkeypatch.chdir(tmp_path)

    assert pantalla.abrir_ejemplo("E5_apartamentos.json") is not None
    assert len(pantalla.editor.zonas.formularios) == 1


def test_un_ejemplo_que_faltara_avisa_en_vez_de_caerse(pantalla, avisos):
    assert pantalla.abrir_ejemplo("no_existe.json") is None
    assert avisos

# ---------------------------------------------------------------------------
# De dónde viene el riesgo
# ---------------------------------------------------------------------------

def test_el_boton_del_desglose_se_enciende_al_calcular(pantalla):
    assert str(pantalla.resultados.boton_desglose.cget("state")) == "disabled"

    pantalla.calcular()

    assert str(pantalla.resultados.boton_desglose.cget("state")) == "normal"


def test_sin_calcular_no_hay_desglose(pantalla):
    assert pantalla.de_donde_viene() is None


def _cargar_perdidas_r4(pantalla):
    """La casa rural solo trae R1; con L_F «otros» tiene R4, y R4 cumple."""
    for formulario in pantalla.editor.zonas.formularios:
        formulario.pestanas[4].campos["L_F"].poner_llave("otros")


def test_el_desglose_abre_el_riesgo_elegido_en_el_panel(pantalla):
    pantalla.marcas[4].set(True)
    _cargar_perdidas_r4(pantalla)
    pantalla.calcular()
    pantalla.resultados.arbol.selection_set("R4")

    pantalla.de_donde_viene()

    assert pantalla.ventana_desglose.tipo == 4


def test_sin_elegir_nada_el_desglose_va_al_que_no_cumple(pantalla):
    pantalla.marcas[4].set(True)      # R4 de la casa rural cumple; R1 no
    _cargar_perdidas_r4(pantalla)
    pantalla.calcular()
  
    aportes = pantalla.de_donde_viene()

    assert pantalla.ventana_desglose.tipo == 1
    assert aportes[0].componente == "R_V"


def test_el_desglose_no_trabaja_con_un_riesgo_viejo(pantalla):
    pantalla.calcular()
    pantalla.editor.N_G.poner(0.01)      # ahora cumple

    pantalla.de_donde_viene()

    assert pantalla.ultimo_calculo[1]["cumple"] is True
    assert "Cumple" in pantalla.ventana_desglose.titulo.cget("text")
    

# ---------------------------------------------------------------------------
# Los datos del proyecto llegan al informe
# ---------------------------------------------------------------------------

def test_los_datos_del_proyecto_van_al_informe(pantalla, tmp_path, avisos, monkeypatch):
    principal_norma.papo["proyecto"] = "Casa rural del Anexo E.2"
    principal_norma.papo["descripcion"] = "Prueba de la descripción"
    recibido = {}
    _informe_de_mentira(monkeypatch, recibido)
    pantalla.calcular()

    pantalla.informe(tmp_path / "m.pdf")

    assert recibido["proyecto"]["Proyecto"] == "Casa rural del Anexo E.2"
    assert recibido["proyecto"]["Descripción"] == "Prueba de la descripción"