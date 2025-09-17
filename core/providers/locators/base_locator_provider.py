# core/providers/base_provider.py
# Proveedor base para locators

from abc import ABC, abstractmethod
from typing import Any


class BaseLocatorProvider(ABC):
    """
    Contrato base para cualquier proveedor de localizadores.
    """

    @abstractmethod
    def get(self, locator_key: str) -> Any:
        """
        Devuelve el localizador asociado a la clave.
        Lanza KeyError si no existe.
        """
        pass
