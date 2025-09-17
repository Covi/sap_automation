# core/providers/composite_locator_provider.py
# Composite Provider para combinar múltiples proveedores de localizadores

from typing import Sequence, Any
from .base_locator_provider import BaseLocatorProvider


class CompositeLocatorProvider(BaseLocatorProvider):
    """
    Un proveedor que se compone de otros proveedores.
    Busca un locator en sus proveedores, en orden,
    y devuelve la primera coincidencia que encuentre.
    """

    def __init__(self, providers: Sequence[BaseLocatorProvider]):
        self._providers = providers

    def get(self, locator_key: str) -> Any:
        """
        Busca la clave en los proveedores en el orden en que fueron pasados.
        """
        for provider in self._providers:
            try:
                return provider.get(locator_key)
            except KeyError:
                continue

        raise KeyError(f"El locator '{locator_key}' no se encontró en ninguno de los proveedores.")
