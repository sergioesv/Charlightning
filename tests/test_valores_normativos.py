from variables.variable_generales import VAR


def test_valores_normativos_paso_21():
    assert VAR["L_t1"] == 1e-2
    assert VAR["R_T3"] == 1e-4