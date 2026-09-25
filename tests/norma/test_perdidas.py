"""
Paso 32b: pruebas propias de perdidas.py que el Anexo E no ejercita.

E.3/E.4/E.5 solo cubren L1 (vidas) y L4 (economico); aqui se prueban L2
(servicio publico), L3 (patrimonio cultural) y L_E (perdida adicional al
medioambiente, ec. C.14-C.15), con valores propios calculados a mano.
"""
from pytest import approx

from calculate_risk.norma import perdidas


# ---------------------------------------------------------------------------
# L2: perdida de servicio publico (ec. C.7, C.8)
# ---------------------------------------------------------------------------

def test_l_b2_dano_fisico_servicio_publico():
    # L_B = rp * rf * LF * (nz/nt) = 0,5 * 0,1 * 0,1 * (50/1000) = 2,5e-4
    assert perdidas.l_b2(rp=0.5, rf=0.1, LF=0.1, nz=50, nt=1000) == approx(2.5e-4)


def test_l_c2_falla_sistemas_servicio_publico():
    # L_C = LO * (nz/nt) = 0,01 * (200/1000) = 2e-3
    assert perdidas.l_c2(LO=0.01, nz=200, nt=1000) == approx(2e-3)


# ---------------------------------------------------------------------------
# L3: perdida de patrimonio cultural (ec. C.9) -- unica componente de L3
# ---------------------------------------------------------------------------

def test_l_b3_dano_fisico_patrimonio():
    # L_B = rp * rf * LF * (cz/ct) = 1 * 1 * 0,1 * (300000/1000000) = 0,03
    assert perdidas.l_b3(rp=1, rf=1, LF=0.1, cz=300000, ct=1000000) == approx(0.03)


def test_l_b3_es_cero_sin_valor_cultural_en_la_zona():
    assert perdidas.l_b3(rp=1, rf=1, LF=0.1, cz=0, ct=1000000) == 0


# ---------------------------------------------------------------------------
# L_E: perdida adicional al medioambiente (ec. C.14, C.15)
# ---------------------------------------------------------------------------

def test_l_ft_sin_riesgo_ambiental_es_igual_a_LF():
    # ce = 0 -> LE = 0 -> LFT = LF (caso normal, sin bienes peligrosos afuera)
    assert perdidas.l_ft(LF=0.2, LFE=1.0, ce=0.0, ct=100000) == approx(0.2)


def test_l_ft_suma_la_perdida_ambiental():
    # LE = LFE * ce/ct = 0,5 * 20000/100000 = 0,1 ; LFT = LF + LE = 0,1 + 0,1 = 0,2
    assert perdidas.l_ft(LF=0.1, LFE=0.5, ce=20000, ct=100000) == approx(0.2)


def test_l_ft_LFE_desconocido_se_asume_1_nota_2():
    # NOTA 2 de la norma: si LFE se desconoce, se asume LFE = 1
    assert perdidas.l_ft(LF=0.0, LFE=1.0, ce=100000, ct=100000) == approx(1.0)


# ---------------------------------------------------------------------------
# L_E integrado en L4 (riesgos.py): mismo caso, con y sin riesgo ambiental
# ---------------------------------------------------------------------------

def test_riesgo_ambiental_l4_aumenta_R_B_y_R_V():
    from calculate_risk.norma import riesgos
    from calculate_risk.norma.modelo import Estructura, Zona

    estructura = Estructura(L=10, W=10, H=5, C_D=1, c_t=100000)

    def zona(c_e):
        return Zona("Z1", r_p=1, r_f=1, L_F=0.1, c_b=50000, c_e=c_e, L_FE=0.5)

    sin_riesgo = riesgos.evaluar(estructura, [], [zona(c_e=0.0)], N_G=4.0, tipos=(4,))[4]
    con_riesgo = riesgos.evaluar(estructura, [], [zona(c_e=20000.0)], N_G=4.0, tipos=(4,))[4]

    # LFT pasa de 0,1 a 0,2 (se duplica) -> R_B y R_V tambien se duplican
    assert con_riesgo["R_B"] == approx(sin_riesgo["R_B"] * 2)
    assert con_riesgo["R_V"] == approx(sin_riesgo["R_V"] * 2)