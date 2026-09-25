"""
Paso 36a: bandera `razones_l4_unitarias` de la Zona.

Nota "a" de la Tabla C.11 (pag. 51 de la norma): las razones c_a/c_t,
(c_a+c_b+c_c+c_s)/c_t y c_s/c_t solo se usan si la evaluacion se hace con el
Anexo D (costo-beneficio). Si R4 se compara contra el valor representativo de
la Tabla 4 (R_T4 = 1e-3), "las relaciones son reemplazadas por el valor de 1".

Con los campos c_a/c_b/c_c/c_s eso no se puede expresar: para que c_a/c_t = 1
y c_s/c_t = 1 hace falta c_a = c_s = c_t, pero entonces la suma de la ec.
(C.12) da (c_a+c_b+c_c+c_s)/c_t = 2 o mas, no 1. Por eso la bandera.
"""
from pytest import approx

from calculate_risk.norma import areas, frecuencias, riesgos
from calculate_risk.norma.modelo import Estructura, SistemaInterno, Zona

N_G = 4.0


def _estructura():
    return Estructura(L=20, W=10, H=6, C_D=1, c_t=1.0, hay_animales=True)


def _zona(razones_unitarias):
    return Zona(
        "Z1",
        r_t=1e-2, r_p=0.5, r_f=1e-2,
        L_T=1e-2, L_F=0.2, L_O=1e-3,
        sistemas_internos=[SistemaInterno("pot", "", K_S3=1.0, U_W=2.5)],
        razones_l4_unitarias=razones_unitarias,
    )


def test_razones_unitarias_dan_las_perdidas_sin_ninguna_razon():
    est = _estructura()
    r4 = riesgos.evaluar(est, [], [_zona(True)], N_G, tipos=(4,))[4]

    N_D = frecuencias.n_d(N_G, areas.area_estructura_completa(20, 10, 6), 1)
    N_M = frecuencias.n_m(N_G, 20, 10)

    # L_A = r_t * L_T ; L_B = r_p * r_f * L_F ; L_C = L_O  (todas las razones = 1)
    assert r4["R_A"] == approx(N_D * 1.0 * (1e-2 * 1e-2))
    assert r4["R_B"] == approx(N_D * 1.0 * (0.5 * 1e-2 * 0.2))
    # P_M = P_DPS * P_MS = 1 * min((1*1*1*(1/2.5))**2, 1) = 0,16
    assert r4["R_M"] == approx(N_M * 0.16 * 1e-3)


def test_sin_la_bandera_las_razones_valen_cero_si_no_se_dan_los_valores():
    # Por defecto c_a = c_b = c_c = c_s = 0, asi que todas las razones son 0
    # y R4 sale 0: es la señal de que ese caso necesita o los valores del
    # Anexo D, o la bandera.
    est = _estructura()
    r4 = riesgos.evaluar(est, [], [_zona(False)], N_G, tipos=(4,))[4]

    assert r4["total"] == 0.0