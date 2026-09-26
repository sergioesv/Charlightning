"""
Paso 51d: los casos que usan las pruebas del motor, ya en el modelo nuevo.

Antes salían de tests/datos_pantalla.py pasando por el adaptador, y las dos
cosas se retiran con la pantalla vieja. Aquí no hay traducción de nada: los
objetos del modelo se escriben directos.

  casa_rural()  -- el Anexo E.2, leído del JSON que ya trae el programa.
  edificio(tipo) -- un caso PROPIO de prueba, no sale de la norma.

El edificio existe para lo que el hospital del E.4 no puede: probar el
enganche del Anexo D dentro de medidas.explorar(), que necesita los objetos
del caso y no un resultado ya evaluado. No se distribuye como ejemplo porque
tiene valores que no son filas de las tablas (r_f = 1e-2 con K_S3 = 1,
P_LD = 0,4), y la pantalla nueva solo acepta filas.
"""
from calculate_risk.norma import casos
from calculate_risk.norma.modelo import Estructura, Linea, SistemaInterno, Zona

RUTA_CASA_RURAL = "casos/casa_rural.json"


def casa_rural() -> tuple:
    """(estructura, lineas, zonas, N_G) del Anexo E.2. R1 = 2,506e-5."""
    c = casos.cargar_caso(RUTA_CASA_RURAL)
    return c["estructura"], c["lineas"], c["zonas"], c["N_G"]


def _lineas_edificio() -> list:
    """Tres líneas: dos aéreas y una subterránea apantallada."""
    comun = dict(L_L=1000, C_T=1, C_E=0.5, U_W=2.5, C_LD=1, C_LI=1, P_LI=1,
                 P_EB=0.05)
    return [Linea("potencia_aerea", C_I=1, P_LD=1, **comun),
            Linea("servicio_aereo", C_I=1, P_LD=1, **comun),
            Linea("servicio_subterraneo", C_I=0.5, P_LD=0.4, **comun)]


def edificio(tipo) -> tuple:
    """Edificio de 20 x 10 x 6 m en zona suburbana, N_G = 10, con SPCR E = 0,9.

    Una sola zona, con las pérdidas del riesgo que se pida. Solo están
    armados L1 y L4, que son los que necesita el Anexo D.
    """
    if tipo not in (1, 4):
        raise ValueError("el edificio de prueba solo está armado para L1 y L4")

    estructura = Estructura(L=20, W=10, H=6, H_p=6, C_D=0.5, n_t=1, c_t=1,
                            riesgo_explosion_o_vital=True, hay_animales=True)
    interno = [SistemaInterno("sistemas_internos", "", K_S3=1, U_W=1, P_DPS=1)]
    comun = dict(nombre="edificio", P_B=0.1, r_t=1e-2, r_p=0.5, r_f=1e-2,
                 n_z=1, sistemas_internos=interno)

    if tipo == 1:
        zona = Zona(h_z=2, L_T=1e-4, L_F=2e-2, L_O=1e-3, **comun)
    else:
        zona = Zona(h_z=1, L_T=1e-2, L_F=2e-1, L_O=1e-3,
                    razones_l4_unitarias=True, **comun)

    return estructura, _lineas_edificio(), [zona], 10