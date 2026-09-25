"""
Paso 36b: un SistemaInterno con linea="" lo alimentan TODAS las lineas.

Antes, si el sistema interno no traia el nombre exacto de la linea, R_W y R_Z
usaban el valor por defecto P_DPS = 1 (como si no hubiera DPS coordinados) y
salian hasta 100 veces mas altos. El campo `linea` sirve para saber que C_LD
usar cuando hay varias lineas distintas; dejarlo vacio significa "no esta
atado a una linea en particular", no "no tiene DPS".

Esto hace falta para el adaptador de la pantalla vieja (Paso 36c): esa
pantalla tiene un solo juego de DPS para todo, sin nombres de linea.
"""
from pytest import approx

from calculate_risk.norma import riesgos
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona

N_G = 4.0


def _caso(nombre_linea_del_sistema):
    est = Estructura(L=20, W=10, H=6, C_D=1, n_t=1, riesgo_explosion_o_vital=True)
    linea = Linea("potencia", L_L=1000, C_I=1, P_EB=0.05)
    zona = Zona(
        "Z1", P_B=1, L_T=1e-2, L_F=1e-2, L_O=1e-3, n_z=1, t_z=8760,
        sistemas_internos=[
            SistemaInterno("todo", nombre_linea_del_sistema, K_S3=1.0, U_W=2.5, P_DPS=0.01)
        ],
    )
    return riesgos.evaluar(est, [linea], [zona], N_G, tipos=(1,))[1]


def test_sistema_sin_nombre_de_linea_conserva_sus_dps():
    sin_nombre = _caso("")
    con_nombre = _caso("potencia")

    assert sin_nombre["R_W"] == approx(con_nombre["R_W"])
    assert sin_nombre["R_Z"] == approx(con_nombre["R_Z"])


def test_zona_sin_sistemas_internos_sigue_sin_dps():
    # Si no hay ningun sistema interno, P_DPS = 1 (sin DPS coordinados).
    est = Estructura(L=20, W=10, H=6, C_D=1, n_t=1, riesgo_explosion_o_vital=True)
    linea = Linea("potencia", L_L=1000, C_I=1, P_EB=0.05)
    zona = Zona("Z1", P_B=1, L_T=1e-2, L_F=1e-2, L_O=1e-3, n_z=1, t_z=8760)

    r1 = riesgos.evaluar(est, [linea], [zona], N_G, tipos=(1,))[1]
    con_dps = _caso("potencia")

    assert r1["R_W"] == approx(con_dps["R_W"] * 100)