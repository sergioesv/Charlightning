"""
Paso 32c: casos propios sobre reglas de modelado de lineas que el Anexo E no
ejercita (no son ecuaciones nuevas, sino COMO se arman los objetos Linea):

- C_I = 0,01 (Tabla A.2): linea enterrada bajo malla de tierra conectada.
- "Secciones mixtas": una misma linea fisica con tramos de distinto tipo
  (aerea + enterrada) -> se modela como VARIOS objetos Linea, uno por tramo,
  y sus componentes R_U/R_V/R_W/R_Z se SUMAN (regla del plan maestro).
- "Mismo trazado": dos lineas fisicas distintas que van por la misma
  canalizacion (un solo rayo las afecta a ambas a la vez) -> se modela con
  UN SOLO objeto Linea, el de la linea mas desfavorable; NO se suman, porque
  no son eventos independientes.
"""
from pytest import approx

from calculate_risk.norma import frecuencias, riesgos, tablas
from calculate_risk.norma.modelo import Estructura, Linea, Zona


# ---------------------------------------------------------------------------
# C_I = 0,01 (Tabla A.2): enterrada bajo malla de tierra
# ---------------------------------------------------------------------------

def test_c_i_bajo_malla_de_tierra_reduce_100_veces_frente_a_aerea():
    assert tablas.CI["subterranea_bajo_malla_puesta_a_tierra"] == 0.01

    n_l_malla = frecuencias.n_l(N_G=4.0, L_L=1000, ci=tablas.CI["subterranea_bajo_malla_puesta_a_tierra"], ce=1, ct=1)
    n_l_aerea = frecuencias.n_l(N_G=4.0, L_L=1000, ci=tablas.CI["aerea"], ce=1, ct=1)

    assert n_l_malla == approx(1.6e-3)
    assert n_l_aerea == approx(0.16)
    assert n_l_aerea == approx(n_l_malla * 100)


# ---------------------------------------------------------------------------
# Secciones mixtas de UNA linea fisica -> se suman
# ---------------------------------------------------------------------------

def _estructura_y_zona():
    estructura = Estructura(L=10, W=10, H=5, C_D=1, n_t=10)
    zona = Zona("Z1", P_TA=1, P_TU=1, P_B=1, L_T=1e-2, n_z=10, t_z=8760)
    return estructura, zona


def test_secciones_mixtas_se_suman_y_no_se_pueden_tratar_como_una_sola():
    estructura, zona = _estructura_y_zona()

    p_ld_aerea = tablas.PLD["sin_conectar_barra_equipotencial"][2.5]                         # 1
    p_ld_enterrada = tablas.PLD["conectada_barra_equipotencial"]["hasta_1_ohm_km"][2.5]       # 0,2

    # Linea real de 1000 m: 600 m aereos + 400 m enterrados con blindaje.
    aerea = Linea("potencia_aerea", L_L=600, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                  C_LD=1, C_LI=1, P_LD=p_ld_aerea, P_LI=1, P_EB=1)
    enterrada = Linea("potencia_enterrada", L_L=400, C_I=0.5, C_T=1, C_E=1, U_W=2.5,
                       C_LD=1, C_LI=1, P_LD=p_ld_enterrada, P_LI=1, P_EB=1)

    r_secciones = riesgos.evaluar(estructura, [aerea, enterrada], [zona], N_G=4.0, tipos=(1,))[1]
    assert r_secciones["R_U"] == approx(0.001024)

    # Si por error se tratan los 1000 m completos como si fueran aereos
    # (ignorando que 400 m estan enterrados y blindados), R_U sale 56 % mas
    # alto -- por eso el tramo enterrado no se puede omitir ni promediar.
    todo_aerea = Linea("todo_aerea_1000m", L_L=1000, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                        C_LD=1, C_LI=1, P_LD=p_ld_aerea, P_LI=1, P_EB=1)
    r_mal = riesgos.evaluar(estructura, [todo_aerea], [zona], N_G=4.0, tipos=(1,))[1]
    assert r_mal["R_U"] == approx(0.0016)
    assert r_mal["R_U"] > r_secciones["R_U"]


# ---------------------------------------------------------------------------
# Mismo trazado de DOS lineas fisicas -> solo la peor, no se suman
# ---------------------------------------------------------------------------

def test_mismo_trazado_solo_cuenta_la_linea_mas_desfavorable():
    estructura, zona = _estructura_y_zona()

    # Potencia y telecomunicacion van por la misma canalizacion: un rayo que
    # cae sobre ese trazado las afecta a las dos a la vez (no son eventos
    # independientes). La telecom esta bien blindada (P_LD menor); la
    # potencia no -> la potencia es la linea mas desfavorable.
    potencia = Linea("potencia", L_L=1000, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                      C_LD=1, C_LI=1, P_LD=1.0, P_LI=1, P_EB=1)
    telecom = Linea("telecom", L_L=1000, C_I=1.0, C_T=1, C_E=1, U_W=2.5,
                     C_LD=1, C_LI=1, P_LD=0.2, P_LI=1, P_EB=1)

    r_solo_peor = riesgos.evaluar(estructura, [potencia], [zona], N_G=4.0, tipos=(1,))[1]
    assert r_solo_peor["R_U"] == approx(0.0016)

    # Sumar las dos (tratandolas como independientes) es INCORRECTO aqui:
    # duplica una parte del mismo evento y sobreestima el riesgo un 20 %.
    r_sumando_mal = riesgos.evaluar(estructura, [potencia, telecom], [zona], N_G=4.0, tipos=(1,))[1]
    assert r_sumando_mal["R_U"] == approx(0.00192)
    assert r_sumando_mal["R_U"] > r_solo_peor["R_U"]