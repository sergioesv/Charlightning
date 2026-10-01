"""
Límite de peticiones por cliente, en memoria.

Sirve para un solo proceso (el servicio de Railway). Si algún día hay varias
réplicas, esta misma interfaz se puede cumplir con Redis o Supabase.
"""
import time
from collections import defaultdict, deque


class Limite:
    """Deja pasar `maximo` peticiones por cliente en cada ventana de `segundos`."""

    def __init__(self, maximo: int, segundos: float, reloj=time.monotonic):
        self.maximo = maximo
        self.segundos = segundos
        self._reloj = reloj
        self._llamadas = defaultdict(deque)

    def permitir(self, cliente: str) -> bool:
        ahora = self._reloj()
        if len(self._llamadas) > 10_000:
            self._olvidar_viejos(ahora)
        llamadas = self._llamadas[cliente]
        while llamadas and ahora - llamadas[0] >= self.segundos:
            llamadas.popleft()
        if len(llamadas) >= self.maximo:
            return False
        llamadas.append(ahora)
        return True

    def _olvidar_viejos(self, ahora: float):
        """Borra los clientes sin llamadas en la ventana, para no crecer sin fin."""
        for cliente in [c for c, ll in self._llamadas.items()
                        if not ll or ahora - ll[-1] >= self.segundos]:
            del self._llamadas[cliente]
