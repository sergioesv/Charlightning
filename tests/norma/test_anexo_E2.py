"""
Paso 32 (Anexo E.2): reproduce el caso "casa rural" completo, con sus dos
escenarios de protección, usando calculate_risk/norma/.

Es el mismo caso que ya se validó a mano en el Paso 21 (H1-H4) pero ahora
construido con el modelo nuevo (Estructura/Linea/Zona/SistemaInterno) en vez
de la pantalla vieja. Sirve también para probar dos líneas reales al tiempo
(potencia + telecomunicación) con sus propios sistemas internos.
"""
from calculate_risk.norma import riesgos
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona

E5 = 1e-5
N_G = 4.0


def cercano(calculado: float, esperado: float, tol_rel: float = 0.03) -> bool:
    return abs(calculado - esperado) <= tol_rel * abs(esperado)


def casa_rural(P_B=1.0, P_EB=1.0):
    """Casa rural de 15 x 20 x 6 m, terreno llano, sin estructuras vecinas
    (Anexo E.2). P_B=0,2 simula el SPCR clase IV; P_EB=0,05 simula DPS NPR IV."""
    estructura = Estructura(L=15.0, W=20.0, H=6.0, C_D=1.0, n_t=5.0)

    potencia = Linea(
        "potencia", L_L=1000.0, C_I=0.5, C_T=1.0, C_E=1.0, U_W=2.5,
        C_LD=1.0, C_LI=1.0, P_LD=1.0, P_LI=0.3, P_EB=P_EB,
    )
    telecom = Linea(
        "telecomunicacion", L_L=1000.0, C_I=1.0, C_T=1.0, C_E=1.0, U_W=1.5,
        C_LD=1.0, C_LI=1.0, P_LD=1.0, P_LI=0.5, P_EB=P_EB,
    )

    zona = Zona(
        "Z2_interior", P_TA=1.0, P_TU=1.0, P_B=P_B, K_S1=1.0, K_S2=1.0,
        sistemas_internos=[
            SistemaInterno("pot", "potencia", K_S3=0.2, U_W=2.5),
            SistemaInterno("tel", "telecomunicacion", K_S3=1.0, U_W=1.5),
        ],
        r_t=1e-5, r_p=1.0, r_f=1e-3, h_z=1.0,
        L_T=1e-2, L_F=1e-1, L_O=0.0, n_z=5.0, t_z=8760.0,
    )
    return estructura, [potencia, telecom], [zona]


def test_casa_rural_sin_proteccion():
    est, lineas, zonas = casa_rural(P_B=1.0, P_EB=1.0)
    r1 = riesgos.evaluar(est, lineas, zonas, N_G, tipos=(1,))[1]

    assert cercano(r1["R_B"], 0.103e-5, 0.03)
    assert cercano(r1["R_V"], 2.40e-5, 0.01)
    assert cercano(r1["total"], 2.51e-5, 0.01)
    assert not r1["cumple"]


def test_casa_rural_solucion_a_dps_npr_iv():
    """(a) DPS coordinados NPR IV en la entrada de ambas líneas."""
    est, lineas, zonas = casa_rural(P_B=1.0, P_EB=0.05)
    r1 = riesgos.evaluar(est, lineas, zonas, N_G, tipos=(1,))[1]

    assert cercano(r1["total"], 0.223e-5, 0.03)
    assert r1["cumple"]


def test_casa_rural_solucion_b_spcr_mas_dps():
    """(b) SPCR clase IV + DPS."""
    est, lineas, zonas = casa_rural(P_B=0.2, P_EB=0.05)
    r1 = riesgos.evaluar(est, lineas, zonas, N_G, tipos=(1,))[1]

    assert cercano(r1["total"], 0.141e-5, 0.03)
    assert r1["cumple"]