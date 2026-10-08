"""
Lo que la página web le pide al motor, sin nada de HTTP.

Recibe y devuelve datos simples (dict, bytes) para que api.py solo traduzca
peticiones y respuestas. Aquí no se calcula ningún riesgo: todo sale de
calculate_risk/, el mismo motor del programa de escritorio.
"""
import os
import tempfile
from dataclasses import MISSING, asdict, fields
from datetime import date
from pathlib import Path

from calculate_risk.norma import (casos, densidad, etiquetas, medidas, probabilidades,
                                  riesgos, tablas)
from calculate_risk.norma.modelo import (Emplazamiento, Estructura, Linea, SistemaInterno,
                                         Zona)

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_EJEMPLOS = RAIZ / "casos"

# Topes para que un caso no deje al servidor ocupado demasiado tiempo.
MAX_LINEAS = 10
MAX_ZONAS = 20
MAX_SISTEMAS_POR_ZONA = 10


class CasoInvalido(ValueError):
    """El JSON no describe un caso que el motor pueda evaluar; el mensaje dice por qué."""


# ---------------------------------------------------------------------------
# Del JSON a los casos del motor
# ---------------------------------------------------------------------------

def _revisar_tamano(datos: dict):
    if not isinstance(datos, dict):
        raise CasoInvalido("El caso tiene que ser un objeto JSON.")
    for llave in ("N_G", "estructura"):
        if llave not in datos:
            raise CasoInvalido(f"Falta la llave «{llave}».")
    lineas, zonas = datos.get("lineas", []), datos.get("zonas", [])
    if not isinstance(lineas, list) or not isinstance(zonas, list):
        raise CasoInvalido("«lineas» y «zonas» tienen que ser listas.")
    if len(lineas) > MAX_LINEAS:
        raise CasoInvalido(f"Máximo {MAX_LINEAS} líneas por caso.")
    if not zonas:
        raise CasoInvalido("El caso necesita al menos una zona.")
    if len(zonas) > MAX_ZONAS:
        raise CasoInvalido(f"Máximo {MAX_ZONAS} zonas por caso.")
    for zona in zonas:
        if len(zona.get("sistemas_internos", [])) > MAX_SISTEMAS_POR_ZONA:
            raise CasoInvalido(f"Máximo {MAX_SISTEMAS_POR_ZONA} sistemas internos por zona.")


def _con_n_g_de_coordenadas(datos: dict) -> dict:
    """Si el emplazamiento es por coordenadas, N_G se toma de la NASA aquí mismo:
    el informe dice de dónde salió N_G y el número tiene que ser ese."""
    empl = datos.get("emplazamiento")
    if not empl or empl.get("modo") != "coordenadas":
        return datos
    try:
        ficha = densidad.ficha_de(Emplazamiento(**empl))
    except TypeError as error:
        raise CasoInvalido(f"Emplazamiento: {error}") from error
    return {**datos, "N_G": ficha.N_G}


def leer_casos(datos: dict) -> dict:
    """{tipo: caso} a partir del JSON, con los mismos nombres de campo del
    programa de escritorio (casos/*.json). Lanza CasoInvalido si no se puede."""
    _revisar_tamano(datos)
    try:
        if datos.get("emplazamiento"):
            densidad.validar(Emplazamiento(**datos["emplazamiento"]))
        datos = _con_n_g_de_coordenadas(datos)
        por_tipo = casos.casos_desde_datos(datos)
    except CasoInvalido:
        raise
    except (TypeError, ValueError, KeyError, AttributeError) as error:
        raise CasoInvalido(str(error)) from error
    if not por_tipo:
        raise CasoInvalido("El caso no dice qué riesgos evaluar («tipos»).")
    if any(t not in (1, 2, 3, 4) for t in por_tipo):
        raise CasoInvalido("Los riesgos a evaluar son 1, 2, 3 o 4.")
    try:
        n_g = float(next(iter(por_tipo.values()))["N_G"])
    except (TypeError, ValueError) as error:
        raise CasoInvalido("N_G tiene que ser un número.") from error
    if not n_g > 0:
        raise CasoInvalido("N_G tiene que ser mayor que cero.")
    return por_tipo


TITULOS_PESTANA = {1: "R1 Vidas humanas", 2: "R2 Servicio público",
                   3: "R3 Patrimonio", 4: "R4 Económica"}

# El mismo texto de ventanas/editor_caso.py: un riesgo sin pérdidas no se calcula.
SIN_PERDIDAS = ("R{tipo} no tiene pérdidas cargadas en ninguna zona ({zonas}): daría 0 y "
                "«Cumple» sin haber evaluado nada. Carga las pérdidas en la pestaña "
                "«{pestana}» de cada zona, o desmarca R{tipo} arriba.")


def _evaluar_casos(por_caso: dict) -> tuple:
    """(resultados, avisos), igual que EditorCaso.evaluar de la pantalla."""
    vacios = [SIN_PERDIDAS.format(tipo=t, pestana=TITULOS_PESTANA[t],
                                  zonas=", ".join(z.nombre for z in c["zonas"]))
              for t, c in sorted(por_caso.items()) if riesgos.sin_perdidas(c["zonas"], t)]
    if vacios:
        raise CasoInvalido("\n\n".join(vacios))
    resultados, avisos = {}, []
    for tipo, caso in sorted(por_caso.items()):
        try:
            resultados[tipo] = riesgos.evaluar(caso["estructura"], caso["lineas"],
                                               caso["zonas"], caso["N_G"], tipos=(tipo,))[tipo]
        except (TypeError, ValueError, KeyError, ZeroDivisionError) as error:
            raise CasoInvalido(f"R{tipo}: {error}") from error
    avisos += riesgos.avisos_sin_spcr(next(iter(por_caso.values()))["zonas"])
    return resultados, avisos


# ---------------------------------------------------------------------------
# Lo que devuelve la API
# ---------------------------------------------------------------------------

def _componentes(r: dict) -> dict:
    return {c: r[c] for c in riesgos.COMPONENTES}


def _resultado_publico(resultado: dict) -> dict:
    return {
        "total": resultado["total"],
        "R_T": resultado["R_T"],
        "cumple": resultado["cumple"],
        "componentes": _componentes(resultado),
        "zonas": {nombre: {"total": z["total"], "componentes": _componentes(z)}
                  for nombre, z in resultado["zonas"].items()},
    }


def evaluar(datos: dict) -> dict:
    """{"N_G", "riesgos": {"1": {...}}, "avisos": [...]} para el JSON de un caso."""
    por_caso = leer_casos(datos)
    resultados, avisos = _evaluar_casos(por_caso)
    return {
        "N_G": next(iter(por_caso.values()))["N_G"],
        "riesgos": {str(t): _resultado_publico(r) for t, r in resultados.items()},
        "avisos": avisos,
    }


def densidad_en(lat: float, lon: float, fraccion_nube_tierra: float = None) -> dict:
    """N_G en un punto, con su procedencia (la ficha de la NASA)."""
    fraccion = densidad.FACTOR_LIS_A_NG if fraccion_nube_tierra is None else fraccion_nube_tierra
    try:
        ficha = densidad.ficha_desde_lat_lon(lat, lon, fraccion)
    except ValueError as error:
        raise CasoInvalido(str(error)) from error
    datos = asdict(ficha)
    datos["relacion_ic_cg"] = ficha.relacion_ic_cg
    return datos


def informe_pdf(datos: dict, proyecto: dict = None, buscar_medidas: bool = True,
                verificaciones=None) -> tuple:
    """(bytes del PDF, avisos, registro). El PDF se arma en una carpeta temporal que se borra.

    Con `verificaciones` (ver web/verificaciones.py) la memoria se registra ANTES de
    dibujarla y el PDF sale con su código y su QR. Si no se pudo registrar, sale sin ellos
    y el aviso lo dice: un QR que no se pudiera verificar sería peor que no tenerlo.
    `registro` es el que quedó guardado (o None).
    """
    from calculate_risk.informe import generar, verificacion     # matplotlib y reportlab solo aquí

    por_caso = leer_casos(datos)
    resultados, avisos = _evaluar_casos(por_caso)
    proyecto = {str(k)[:40]: str(v)[:1000] for k, v in (proyecto or {}).items()}
    registro = None
    if verificaciones is not None:
        revision = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")[:7]
        candidato = verificacion.registro_de(por_caso, resultados, revision=revision)
        try:
            verificaciones.guardar(candidato)
            registro = candidato
        except Exception as error:       # base caída, volumen lleno...
            avisos.append("No se pudo registrar la memoria para verificarla en línea, así que "
                          f"el PDF sale sin código QR ({type(error).__name__}).")
    with tempfile.TemporaryDirectory(prefix="charlightning_web_") as carpeta:
        informe = generar.generar_informe(carpeta, por_caso, resultados,
                                          proyecto=proyecto, fecha=date.today(),
                                          buscar_medidas=buscar_medidas, verificacion=registro)
        contenido = Path(informe.ruta).read_bytes()
    return contenido, avisos + list(informe.avisos), registro


# ---------------------------------------------------------------------------
# Lo que necesitan los formularios de la calculadora
# ---------------------------------------------------------------------------

def _por_defecto(clase) -> dict:
    """Los valores por defecto de la dataclass, como en ventanas/formularios.py."""
    salida = {}
    for campo in fields(clase):
        if campo.default is not MISSING:
            salida[campo.name] = campo.default
        elif campo.default_factory is not MISSING:
            salida[campo.name] = campo.default_factory()
    return salida


def esquema() -> dict:
    """Las listas de la norma para armar los formularios en el navegador.

    Los textos salen de etiquetas.py y los valores de tablas.py, igual que en
    las listas desplegables del programa de escritorio: el navegador no lleva
    ni un número de la norma escrito a mano.
    """
    simples = {
        tabla: {
            "nombre": etiquetas.nombre_de(tabla),
            "opciones": [{"llave": llave, "texto": texto, "valor": valor}
                         for llave, (texto, valor) in zip(etiquetas.llaves(tabla),
                                                          etiquetas.opciones(tabla))],
        }
        for tabla in etiquetas.SIMPLES
    }
    tensiones = probabilidades.tensiones_soportadas()
    doble = {
        "PLD": {
            "nombre": etiquetas.nombre_de("PLD"),
            "opciones": [{"llave": b, "texto": etiquetas.texto("PLD", b),
                          "valores": {str(u): probabilidades.p_ld(b, u) for u in tensiones}}
                         for b in probabilidades.BLINDAJES],
        },
        "PLI": {
            "nombre": etiquetas.nombre_de("PLI"),
            "opciones": [{"llave": t, "texto": etiquetas.texto("PLI", t),
                          "valores": {str(u): probabilidades.p_li(t, u) for u in tensiones}}
                         for t in probabilidades.TIPOS_DE_LINEA],
        },
    }
    return {
        "tablas": simples,
        "doble_entrada": doble,
        "tensiones": tensiones,
        "constantes": {"LT_L1": tablas.LT_L1, "LF_L3": tablas.LF_L3, "LT_L4": tablas.LT_L4,
                       "FACTOR_MALLA": probabilidades.FACTOR_MALLA,
                       "LIMITE_DE_LATITUD": densidad.LIMITE_DE_LATITUD},
        "tolerables": {str(t): tablas.RT[f"L{t}"] for t in (1, 2, 3, 4)},
        "por_defecto": {
            "Estructura": _por_defecto(Estructura),
            "Linea": {k: v for k, v in _por_defecto(Linea).items() if k != "adyacente"},
            "SistemaInterno": _por_defecto(SistemaInterno),
            "Zona": _por_defecto(Zona),
            "Emplazamiento": _por_defecto(Emplazamiento),
        },
        "componentes": dict(etiquetas.COMPONENTES),
    }


def abrir(datos: dict) -> dict:
    """{tipo: caso} de un JSON en cualquiera de los dos formatos de casos/, con
    las dataclasses ya convertidas en dict, para llenar los formularios."""
    por_tipo = leer_casos(datos)
    salida = {}
    for tipo, caso in por_tipo.items():
        empl = caso.get("emplazamiento")
        salida[str(tipo)] = {
            "N_G": caso["N_G"],
            "emplazamiento": asdict(empl) if empl is not None else None,
            "estructura": asdict(caso["estructura"]),
            "lineas": [asdict(ln) for ln in caso["lineas"]],
            "zonas": [asdict(z) for z in caso["zonas"]],
        }
    # Con coordenadas, leer_casos ya puso el N_G de la NASA; el original se
    # devuelve aparte por si no coincide (la pantalla lo avisa).
    filas = datos.get("filas")
    proyecto = datos.get("proyecto")
    if isinstance(proyecto, dict):
        proyecto = {str(k)[:40]: str(v)[:1000] for k, v in proyecto.items()}
    else:
        proyecto = None
    return {"por_tipo": salida, "N_G_guardado": datos.get("N_G"),
            "filas": filas if isinstance(filas, dict) else None, "proyecto": proyecto}


def desglose(datos: dict, tipo: int) -> dict:
    """«¿De dónde viene el riesgo?»: cada componente y las medidas que lo bajan."""
    por_caso = leer_casos(datos)
    if tipo not in por_caso:
        raise CasoInvalido(f"R{tipo} no está entre los riesgos del caso.")
    resultados, _ = _evaluar_casos({tipo: por_caso[tipo]})
    caso = por_caso[tipo]
    aportes = medidas.de_donde_viene(caso["estructura"], caso["lineas"], caso["zonas"],
                                     caso["N_G"], tipo=tipo)
    return {
        "tipo": tipo,
        "total": resultados[tipo]["total"],
        "R_T": resultados[tipo]["R_T"],
        "cumple": resultados[tipo]["cumple"],
        "aportes": [{
            "componente": a.componente,
            "texto": etiquetas.texto_de_componente(a.componente),
            "valor": a.valor,
            "fraccion": a.fraccion,
            "rebajas": [{"medida": etiquetas.texto_de_medida(r.medida.nombre),
                         "componente": r.componente, "total": r.total,
                         "cumple": r.cumple} for r in a.rebajas],
        } for a in aportes],
    }


# ---------------------------------------------------------------------------
# Ejemplos y validación contra el Anexo E
# ---------------------------------------------------------------------------

# R1 sin protección que imprime la NTC 4552-2:2023 (en unidades de 1e-5), el
# mismo valor que comprueban tests/norma/test_anexo_E*.py.
VALIDACION = (
    ("casa_rural", "E.2 Casa rural", 2.51),
    ("E3_oficinas", "E.3 Edificio de oficinas", 9.65),
    ("E4_hospital", "E.4 Hospital", 69.96),
    ("E5_apartamentos", "E.5 Bloque de apartamentos", 8.364),
)


def ejemplos() -> list:
    """Nombres de los casos de ejemplo que trae el repositorio."""
    return sorted(p.stem for p in CARPETA_EJEMPLOS.glob("*.json"))


def ejemplo(nombre: str) -> dict:
    """El JSON de un ejemplo por su nombre (solo los de casos/)."""
    import json
    if nombre not in ejemplos():
        raise KeyError(nombre)
    return json.loads((CARPETA_EJEMPLOS / f"{nombre}.json").read_text(encoding="utf-8"))


def validacion() -> list:
    """Cada ejemplo del Anexo E evaluado en vivo, al lado de lo que imprime la norma."""
    filas = []
    for archivo, titulo, norma in VALIDACION:
        calculado = evaluar(ejemplo(archivo))["riesgos"]["1"]["total"] / 1e-5
        filas.append({
            "caso": titulo,
            "archivo": f"casos/{archivo}.json",
            "norma": norma,
            "charlightning": round(calculado, 4),
            "diferencia_pct": round(100 * (calculado - norma) / norma, 2),
        })
    return filas
