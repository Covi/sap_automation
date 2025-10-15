from abc import ABC, abstractmethod
from pages.sap_page_base import Locator

class ComponentWithLocator(ABC):
    """Interfaz mínima para cualquier componente que pueda ser decorado."""

    @property
    @abstractmethod
    def component_locator(self) -> Locator:
        pass
