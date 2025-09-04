# core/providers/base_provider.py
# Proveedor base para locators

from abc import ABC, abstractmethod

class BaseLocatorProvider(ABC):
    """
    Define la interfaz para cualquier proveedor de locators.
    Establece el contrato que todas las implementaciones deben seguir.
    """
    @abstractmethod
    def get(self, locator_key: str) -> str:
        """
        Obtiene un locator específico a través de su clave.
        """
        pass