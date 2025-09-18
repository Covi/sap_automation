# core/providers/composite_locator_provider.py
# Composite Provider para combinar múltiples proveedores de localizadores

from typing import List, Any
from .base_locator_provider import BaseLocatorProvider

class CompositeLocatorProvider(BaseLocatorProvider):
    """
    Un proveedor que se compone de otros proveedores.
    Busca un locator en su lista de proveedores, en orden,
    y devuelve la primera coincidencia que encuentra.
    """
    def __init__(self, providers: List[BaseLocatorProvider]):
        self._providers = providers

    def get(self, locator_key: str) -> Any:
        """
        Busca la clave en los proveedores en el orden en que fueron pasados.
        """
        for provider in self._providers:
            try:
                # Intenta obtener el locator del provider actual
                return provider.get(locator_key)
            except KeyError:
                # Si no lo encuentra, no hace nada y pasa al siguiente
                continue
        
        # Si después de recorrer todos los providers no lo encuentra, lanza un error
        raise KeyError(f"El locator '{locator_key}' no se encontró en ninguno de los proveedores.")