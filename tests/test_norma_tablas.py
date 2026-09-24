import math

from calculate_risk.norma.tablas import (
    RT,
    area_equivalente_estructura,
    area_equivalente_protrusion,
)


def test_riesgo_tolerable_ntc_4552_2_2023():
    assert RT["L1"] == 1e-5
    assert RT["L2"] == 1e-3
    assert RT["L3"] == 1e-4
    assert RT["L4"] == 1e-3


def test_area_equivalente_estructura():
    L = 15
    W = 20
    H = 6

    esperado = (
        L * W
        + 6 * H * (L + W)
        + 9 * math.pi * H**2
    )

    assert math.isclose(
        area_equivalente_estructura(L, W, H),
        esperado,
        rel_tol=1e-12,
    )


def test_area_equivalente_protrusion():
    H = 6

    esperado = math.pi * (3 * H) ** 2

    assert math.isclose(
        area_equivalente_protrusion(H),
        esperado,
        rel_tol=1e-12,
    )