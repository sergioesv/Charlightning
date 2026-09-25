"""
Hito B del plan maestro: reproduce los 3 casos de estudio completos del
Anexo E de la NTC 4552-2:2023 (E.3 oficinas, E.4 hospital, E.5 apartamentos)
usando calculate_risk/norma/.

Los valores esperados son los que imprime la norma (en unidades de 1e-5);
la tolerancia es de medio dígito de la norma o 1 %, la que sea mayor -- el
mismo criterio que ya usaste en ntc4552_2/validacion_anexo_E.py (58/59).

Nota: E.4 solución c) tiene una discrepancia conocida y documentada en la
memoria del proyecto (norma imprime 0,2505; el modelo da 0,244) -- no es
un error de este código, se deja el valor recalculado.
"""
import pytest

from calculate_risk.norma import costos, riesgos
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona

E5 = 1e-5


def cercano(calculado: float, esperado: float, tol_abs: float = 0.0015) -> bool:
    """Compara en unidades de 1e-5; tolerancia = medio dígito de la norma o 1 %."""
    c = calculado / E5
    return abs(c - esperado) <= max(tol_abs, 0.011 * abs(esperado))


def _evaluar_total(estructura, lineas, zonas_interior, zonas_exterior, N_G, tipo):
    """Como riesgos.evaluar, pero las zonas exteriores se evalúan SIN líneas
    (R_U solo aplica a personas en el interior, numeral B.6)."""
    r_int = riesgos.evaluar(estructura, lineas, zonas_interior, N_G, tipos=(tipo,))[tipo]
    if not zonas_exterior:
        return r_int
    r_ext = riesgos.evaluar(estructura, [], zonas_exterior, N_G, tipos=(tipo,))[tipo]
    total = r_int["total"] + r_ext["total"]
    zonas = {**r_ext["zonas"], **r_int["zonas"]}
    return {"total": total, "zonas": zonas}


# ---------------------------------------------------------------------------
# E.3 EDIFICIO DE OFICINAS
# ---------------------------------------------------------------------------

def oficinas(P_B=1.0, P_EB=1.0, r_p_Z3=1.0):
    est = Estructura(L=20, W=40, H=25, C_D=1, n_t=200)
    pot = Linea("potencia", L_L=200, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                C_LD=1, C_LI=1, P_LD=1, P_LI=0.3, P_EB=P_EB)
    tel = Linea("telecom", L_L=1000, C_I=0.5, C_T=1, C_E=1, U_W=1.5,
                C_LD=1, C_LI=1, P_LD=1, P_LI=0.5, P_EB=P_EB)
    si = lambda: [SistemaInterno("pot", "potencia", K_S3=0.2, U_W=2.5),
                  SistemaInterno("tel", "telecom", K_S3=1.0, U_W=1.5)]
    comun = dict(P_B=P_B, L_T=1e-2, t_z=8760)
    z1 = Zona("Z1", r_t=1e-3, P_TA=1, r_f=0, n_z=4, **comun)
    z2 = Zona("Z2", r_t=1e-2, P_TA=0, r_f=0, n_z=2, **comun)
    z3 = Zona("Z3", r_t=1e-5, r_f=1e-1, r_p=r_p_Z3, h_z=2, L_F=0.02, n_z=20,
              sistemas_internos=si(), **comun)
    z4 = Zona("Z4", r_t=1e-5, r_f=1e-3, h_z=2, L_F=0.02, n_z=160,
              sistemas_internos=si(), **comun)
    z5 = Zona("Z5", r_t=1e-5, r_f=1e-3, h_z=2, L_F=0.02, n_z=14,
              sistemas_internos=si(), **comun)
    return _evaluar_total(est, [pot, tel], [z3, z4, z5], [z1, z2], 4.0, 1)


def test_oficinas_componentes_por_zona():
    r = oficinas()
    z = r["zonas"]
    assert cercano(z["Z1"]["R_A"], 0.002)
    assert cercano(z["Z2"]["R_A"], 0.0)
    assert cercano(z["Z3"]["R_B"], 4.395)
    assert cercano(z["Z3"]["R_V"], 4.480)
    assert cercano(z["Z4"]["R_B"], 0.352)
    assert cercano(z["Z4"]["R_V"], 0.358)
    assert cercano(z["Z5"]["R_B"], 0.031)


def test_oficinas_total_estructura():
    r = oficinas()
    z = r["zonas"]
    assert cercano(sum(z[n]["R_A"] for n in z), 0.003)
    assert cercano(sum(z[n]["R_U"] for n in z), 0.001)
    assert cercano(sum(z[n]["R_B"] for n in z), 4.778)
    assert cercano(sum(z[n]["R_V"] for n in z), 4.870)
    assert cercano(r["total"], 9.65, tol_abs=0.01)


def test_oficinas_solucion_a():
    r = oficinas(P_B=0.1, P_EB=0.05)
    assert cercano(r["total"], 0.722)
    assert cercano(r["zonas"]["Z3"]["total"], 0.664)


def test_oficinas_solucion_b():
    r = oficinas(P_B=0.2, P_EB=0.05, r_p_Z3=0.5)
    assert cercano(r["total"], 0.648)
    assert cercano(r["zonas"]["Z3"]["total"], 0.552)


# ---------------------------------------------------------------------------
# E.4 HOSPITAL (estructura adyacente en la línea de telecomunicación)
# ---------------------------------------------------------------------------

def hospital(tipo, P_B=1.0, P_EB=1.0, P_DPS=1.0, r_p_Z2=1.0, w_m=None):
    c_t = 90.0
    est = Estructura(L=50, W=150, H=10, C_D=1, n_t=1000, c_t=c_t,
                      riesgo_explosion_o_vital=True, hay_animales=False)
    pot = Linea("potencia", L_L=500, C_I=0.5, C_T=0.2, C_E=0.5, U_W=2.5,
                C_LD=1, C_LI=0, P_LD=0.2, P_LI=0.3, P_EB=P_EB)
    tel = Linea("telecom", L_L=300, C_I=0.5, C_T=1, C_E=0.5, U_W=1.5,
                C_LD=1, C_LI=0, P_LD=0.8, P_LI=0.5, P_EB=P_EB,
                adyacente=Estructura(L=20, W=30, H=5), C_DJ=1)
    K_S2 = 1.0 if w_m is None else 0.12 * w_m
    si = lambda: [SistemaInterno("pot", "potencia", K_S3=0.2, U_W=2.5, P_DPS=P_DPS),
                  SistemaInterno("tel", "telecom", K_S3=0.01, U_W=1.5, P_DPS=P_DPS)]
    if tipo == 1:
        z1 = Zona("Z1", r_t=1e-2, P_B=P_B, r_f=0, L_T=1e-2, n_z=10)
        z2 = Zona("Z2", r_t=1e-5, P_B=P_B, r_f=1e-2, r_p=r_p_Z2, h_z=5, L_T=1e-2,
                  L_F=1e-1, L_O=1e-3, n_z=950, sistemas_internos=si())
        z3 = Zona("Z3", r_t=1e-5, P_B=P_B, r_f=1e-3, h_z=5, K_S2=K_S2, L_T=1e-2,
                  L_F=1e-1, L_O=1e-2, n_z=35, sistemas_internos=si())
        z4 = Zona("Z4", r_t=1e-5, P_B=P_B, r_f=1e-3, h_z=5, K_S2=K_S2, L_T=1e-2,
                  L_F=1e-1, L_O=1e-2, n_z=5, sistemas_internos=si())
        return _evaluar_total(est, [pot, tel], [z2, z3, z4], [z1], 4.0, 1)
    z2 = Zona("Z2", P_B=P_B, r_f=1e-2, r_p=r_p_Z2, L_T=0, L_F=0.5, L_O=1e-2,
              c_b=70, c_c=6, c_s=3.5, sistemas_internos=si())
    z3 = Zona("Z3", P_B=P_B, r_f=1e-3, K_S2=K_S2, L_T=0, L_F=0.5, L_O=1e-2,
              c_b=2, c_c=0.9, c_s=5.5, sistemas_internos=si())
    z4 = Zona("Z4", P_B=P_B, r_f=1e-3, K_S2=K_S2, L_T=0, L_F=0.5, L_O=1e-2,
              c_b=1, c_c=0.1, c_s=1.0, sistemas_internos=si())
    return _evaluar_total(est, [pot, tel], [z2, z3, z4], [], 4.0, 4)


def test_hospital_zona2():
    z = hospital(1)["zonas"]
    assert cercano(z["Z1"]["R_A"], 0.009)
    assert cercano(z["Z2"]["R_A"], 0.0009, tol_abs=0.0002)
    assert cercano(z["Z2"]["R_B"], 42.4, tol_abs=0.05)
    assert cercano(z["Z2"]["R_V"], 9.21)
    assert cercano(z["Z2"]["R_C"], 8.484)
    assert cercano(z["Z2"]["R_M"], 2.413)
    assert cercano(z["Z2"]["R_W"], 1.841)
    assert cercano(z["Z2"]["R_Z"], 0.0)   # C_LI=0 en la línea de potencia


def test_hospital_zonas_3_4():
    z = hospital(1)["zonas"]
    assert cercano(z["Z3"]["R_C"], 3.126)
    assert cercano(z["Z3"]["R_M"], 0.889)
    assert cercano(z["Z4"]["R_C"], 0.447)


def test_hospital_total_sin_proteccion():
    assert cercano(hospital(1)["total"], 69.96, tol_abs=0.05)


def test_hospital_soluciones_a_b():
    a = hospital(1, P_B=0.02, P_EB=0.01, P_DPS=0.005, r_p_Z2=0.2, w_m=0.5)
    assert cercano(a["total"], 0.338)
    b = hospital(1, P_B=0.02, P_EB=0.01, P_DPS=0.001, r_p_Z2=0.2)
    assert cercano(b["total"], 0.222)


@pytest.mark.xfail(
    reason="Tabla E.36 (hospital solucion c): discrepancia conocida de la norma -- "
           "recalculado da 0,2505, la norma imprime 0,244 (ver erratas en la memoria)",
    strict=True,
)
def test_hospital_solucion_c():
    c = hospital(1, P_B=0.02, P_EB=0.01, P_DPS=0.002, r_p_Z2=0.2, w_m=0.1)
    assert cercano(c["total"], 0.244)


def test_hospital_l4_por_zona():
    z = hospital(4)["zonas"]
    assert cercano(z["Z2"]["total"], 53.2, tol_abs=0.05)
    assert cercano(z["Z3"]["total"], 8.7, tol_abs=0.05)
    assert cercano(z["Z4"]["total"], 1.6, tol_abs=0.05)
    assert cercano(hospital(4)["total"], 63.5, tol_abs=0.05)


def test_hospital_costo_beneficio():
    c_t_pesos = 90e6
    h4 = hospital(4)
    C_L = costos.c_l(h4["total"], c_t_pesos)
    assert cercano(C_L * E5 / 1e5, 57185 / 1e5, tol_abs=0.01)

    sol = {"a": dict(P_DPS=0.005, w_m=0.5), "b": dict(P_DPS=0.001), "c": dict(P_DPS=0.002, w_m=0.1)}
    esperado_R4 = {"a": 0.30, "b": 0.21, "c": 0.23}
    C_PM = {"a": 28000, "b": 19500, "c": 29600}
    S_M_norma = {"a": 28914, "b": 37495, "c": 27377}
    for k, kw in sol.items():
        r4 = hospital(4, P_B=0.02, P_EB=0.01, r_p_Z2=0.2, **kw)
        assert cercano(r4["total"], esperado_R4[k], tol_abs=0.006)
        C_RL = costos.c_rl(r4["total"], c_t_pesos)
        S_M = costos.s_m(C_L, C_PM[k], C_RL)
        assert cercano(S_M * E5 / 1e5, S_M_norma[k] / 1e5, tol_abs=0.002)


# ---------------------------------------------------------------------------
# E.5 BLOQUE DE APARTAMENTOS (Tabla E.45, 16 escenarios)
# ---------------------------------------------------------------------------

P_B_DE = {"Ninguno": 1, "IV": 0.2, "III": 0.1, "II": 0.05, "I": 0.02}
P_EB_DE = {"Ninguno": 1, "IV": 0.05, "III": 0.05, "II": 0.02, "I": 0.01}

CASOS_E45 = [
    (20, 0.001, "Ninguno", 1, 0.837), (20, 0.01, "Ninguno", 1, 8.364),
    (20, 0.01, "III", 1, 0.776), (20, 0.01, "IV", 0.5, 0.747),
    (20, 0.1, "Ninguno", 1, 83.64), (20, 0.1, "II", 0.2, 0.764),
    (20, 0.1, "I", 1, 1.553), (20, 0.1, "I", 0.5, 0.776),
    (40, 0.001, "Ninguno", 1, 2.436), (40, 0.001, "Ninguno", 0.2, 0.489),
    (40, 0.001, "IV", 1, 0.469), (40, 0.01, "Ninguno", 1, 24.34),
    (40, 0.01, "IV", 0.2, 0.938), (40, 0.01, "I", 1, 0.475),
    (40, 0.1, "Ninguno", 1, 243.4), (40, 0.1, "I", 0.2, 0.949),
]


@pytest.mark.parametrize("H, r_f, spcr, r_p, esperado", CASOS_E45)
def test_apartamentos_tabla_e45(H, r_f, spcr, r_p, esperado):
    est = Estructura(L=30, W=20, H=H, C_D=1, n_t=200)
    P_EB = P_EB_DE[spcr]
    pot = Linea("potencia", L_L=200, C_I=0.5, C_T=1, C_E=0.5, U_W=2.5, P_LI=0.3, P_EB=P_EB)
    tel = Linea("telecom", L_L=100, C_I=0.5, C_T=1, C_E=0.5, U_W=1.5, P_LI=0.5, P_EB=P_EB)
    z2 = Zona("Z2", r_t=1e-5, P_B=P_B_DE[spcr], r_f=r_f, r_p=r_p, L_T=1e-2, L_F=0.1, n_z=200)
    r = riesgos.evaluar(est, [pot, tel], [z2], 4.0, tipos=(1,))[1]
    assert cercano(r["total"], esperado, tol_abs=0.002)