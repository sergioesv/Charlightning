"""
Paso 61b: el informe en PDF con una sola llamada.

    generar_informe(carpeta, casos, por_tipo, ...)  ->  Informe(ruta, paginas, avisos, figuras)

Junta las piezas de la Fase 7: la ficha de N_G (si salió de coordenadas), las medidas de
cada riesgo que NO cumple, las cuatro figuras y el dibujante. No calcula ningún riesgo:
recibe `por_tipo`, los mismos números que muestra el panel, y armado.armar() solo los
escribe.

Nada de lo opcional tumba el informe. Sin matplotlib, sin netCDF4 o sin el archivo de la
NASA el PDF sale igual, sin la figura que no se pudo hacer, y la lista `avisos` dice qué
faltó y por qué. Así el botón Informe nunca deja a nadie sin su PDF.

Las figuras se dibujan en una carpeta temporal: el PDF las lleva adentro, y en la carpeta
de quien lo pidió queda un solo archivo.
"""
import math
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from calculate_risk.informe import armado, pdf
from calculate_risk.norma import medidas, tablas


@dataclass
class Informe:
    ruta: str                       # el PDF
    paginas: int
    avisos: list = field(default_factory=list)     # lo que faltó, en palabras
    figuras: tuple = ()             # las que sí salieron: "mapa", "area", "aporte", "veredicto"


def _nada(_mensaje):
    pass


# ---------------------------------------------------------------------------
# De dónde sale N_G
# ---------------------------------------------------------------------------

def ficha_del_sitio(emplazamiento, avisos: list):
    """La FichaNG si N_G salió de coordenadas; None si se declaró o si no se pudo leer."""
    if emplazamiento is None or emplazamiento.modo != "coordenadas":
        return None
    try:
        from calculate_risk.norma import densidad
        return densidad.ficha_de(emplazamiento)
    except (ImportError, OSError) as error:
        avisos.append("No se pudo leer el archivo de la NASA, así que el informe no trae "
                      f"la ficha del dato de N_G ({error}).")
    except ValueError as error:          # fuera de cobertura o coordenadas inválidas
        avisos.append(f"Sin ficha del dato de N_G: {error}")
    return None


# ---------------------------------------------------------------------------
# Medidas: solo para los riesgos que no cumplen
# ---------------------------------------------------------------------------

def buscar_soluciones(casos: dict, por_tipo: dict, precios=None, avance=_nada) -> dict:
    """{riesgo: soluciones} de cada riesgo que NO cumple. Los que cumplen no se exploran:
    recorrer el catálogo tarda unos segundos por riesgo y no diría nada."""
    catalogo = medidas.catalogo(costos=precios)
    soluciones = {}
    for t in sorted(por_tipo):
        if por_tipo[t]["cumple"]:
            continue
        avance(f"Buscando medidas de protección para R{t}…")
        caso = casos[t]
        soluciones[t] = medidas.explorar(caso["estructura"], caso["lineas"], caso["zonas"],
                                         caso["N_G"], tipo=t, catalogo_medidas=catalogo)
    return soluciones


# ---------------------------------------------------------------------------
# Figuras: cada una por su lado, y la que falle no arrastra a las demás
# ---------------------------------------------------------------------------

def _saliente_gobierna(estructura) -> bool:
    """True si A_D sale del saliente del techo (ec. A.3) y no de la ec. A.2."""
    if estructura.H_p <= 0:
        return False
    return (tablas.area_equivalente_protrusion(estructura.H_p)
            > tablas.area_equivalente_estructura(estructura.L, estructura.W, estructura.H))


def _una_figura(figuras: dict, clave, nombre: str, hacerla, avisos: list):
    try:
        figuras[clave] = hacerla()
    except ImportError:
        avisos.append(f"Sin la figura «{nombre}»: falta la librería matplotlib o netCDF4.")
    except (OSError, ValueError) as error:
        avisos.append(f"Sin la figura «{nombre}»: {error}")


def dibujar_figuras(carpeta, casos, por_tipo, tipo, ficha, soluciones, proyecto,
                    avisos: list) -> dict:
    """{"mapa", "area", "aporte", "veredicto"} -> ruta PNG. "veredicto" es {riesgo: ruta}."""
    from calculate_risk.informe import figuras as f   # necesita matplotlib

    carpeta = Path(carpeta)
    caso = casos[tipo]
    estructura = caso["estructura"]
    resultado = por_tipo[tipo]
    hechas = {}

    if ficha is not None:
        nombre_del_sitio = str(proyecto.get("Proyecto", "")).strip() or "Sitio"
        _una_figura(hechas, "mapa", "mapa del sitio", lambda: f.mapa_del_sitio(
            ficha.lat, ficha.lon, nombre_del_sitio, str(carpeta / "mapa.png"),
            fraccion_nube_tierra=ficha.fraccion_nube_tierra), avisos)

    zona = next(iter(resultado["zonas"].values()))
    _una_figura(hechas, "area", "área de captación", lambda: f.area_de_captacion(
        estructura.L, estructura.W, estructura.H, zona["_detalle"]["A_D"],
        str(carpeta / "area.png"), lineas=[ln.nombre for ln in caso["lineas"]],
        saliente_gobierna=_saliente_gobierna(estructura)), avisos)

    aportes = [(f"$R_{{{c[2:]}}}$", v) for c, v, _ in armado.aportes_de(resultado)]
    if aportes:
        _una_figura(hechas, "aporte", "de dónde viene el riesgo",
                    lambda: f.aporte_de_componentes(aportes, str(carpeta / "aporte.png"),
                                                    tipo=tipo), avisos)

    veredictos = {}
    for t, lista in soluciones.items():
        if not lista:
            continue
        base, mejor = por_tipo[t]["total"], lista[0].riesgo
        if base <= 0 or mejor <= 0 or math.isclose(base, mejor):
            continue
        _una_figura(veredictos, t, f"R{t} contra el tolerable",
                    lambda t=t, base=base, mejor=mejor: f.riesgo_contra_tolerable(
                        [("Sin medidas", base), ("Con la primera combinación", mejor)],
                        por_tipo[t]["R_T"], str(carpeta / f"veredicto_R{t}.png"), tipo=t),
                    avisos)
    if veredictos:
        hechas["veredicto"] = veredictos
    return hechas


# ---------------------------------------------------------------------------
# Todo junto
# ---------------------------------------------------------------------------

def generar_informe(carpeta, casos: dict, por_tipo: dict, proyecto: dict = None,
                    nombre: str = "Memoria de calculo", tipo: int = None, precios=None,
                    fecha=None, buscar_medidas: bool = True, avance=None) -> Informe:
    """Escribe <carpeta>/<nombre>.pdf y devuelve qué salió y qué no.

    casos, por_tipo: lo que devuelven EditorCaso.casos_por_tipo() y EditorCaso.evaluar().
    tipo: el riesgo que se desarrolla paso a paso; por omisión, el más bajo de los evaluados.
    precios: {nombre de la medida: costo}; sin precios las medidas se ordenan por cantidad.
    buscar_medidas: False para no explorar el catálogo (el informe dice que no se buscaron).
    avance: una función que recibe un texto corto en cada etapa, para que la pantalla
        pueda decir «Buscando medidas…» mientras trabaja.
    """
    avance = avance or _nada
    proyecto = proyecto or {}
    tipos = sorted(por_tipo)
    tipo = tipos[0] if tipo is None else tipo
    avisos = []

    avance("Leyendo el dato de N_G…")
    ficha = ficha_del_sitio(casos[tipo].get("emplazamiento"), avisos)

    soluciones = (buscar_soluciones(casos, por_tipo, precios, avance)
                  if buscar_medidas else None)

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.pdf"
    with tempfile.TemporaryDirectory(prefix="charlightning_") as temporal:
        avance("Dibujando las figuras…")
        try:
            figuras = dibujar_figuras(temporal, casos, por_tipo, tipo, ficha,
                                      soluciones or {}, proyecto, avisos)
        except ImportError:
            figuras = {}
            avisos.append("El informe sale sin figuras: falta la librería matplotlib.")

        avance("Componiendo el PDF…")
        documento = armado.armar(casos, por_tipo, proyecto=proyecto, ficha=ficha,
                                 soluciones=soluciones, figuras=figuras, tipo=tipo,
                                 fecha=fecha)
        resultado = pdf.dibujar(documento, str(ruta))

    return Informe(ruta=resultado.ruta, paginas=resultado.paginas,
                   avisos=avisos + list(resultado.advertencias),
                   figuras=tuple(figuras))