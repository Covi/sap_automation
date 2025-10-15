# core/components/form/sap_form_strategies.py

from abc import ABC, abstractmethod
from typing import Any, List

class FormFillingStrategy(ABC):
    """
    Interfaz para estrategias de rellenado de formularios.
    """

    @abstractmethod
    def fill(self, form_map: dict, field: str, value: Any):
        pass


class SimpleFillStrategy(FormFillingStrategy):
    """Rellena un solo locator con un valor simple."""
    def fill(self, form_map: dict, field: str, value: Any):
        locator = form_map[field]
        if isinstance(locator, list):
            locator = locator[0]
        locator.fill(str(value))


class RangeFillStrategy(FormFillingStrategy):
    """Rellena un campo de rango (desde,hasta)."""
    def fill(self, form_map: dict, field: str, value: Any):
        locators: List = form_map[field]
        if not isinstance(locators, list) or len(locators) != 2:
            raise TypeError(f"La estrategia de rango espera 2 locators para '{field}'")

        desde_val, hasta_val = str(value).split(',', 1)
        if desde_val.strip():
            locators[0].fill(desde_val.strip())
        if hasta_val.strip():
            locators[1].fill(hasta_val.strip())


class ListFillStrategy(FormFillingStrategy):
    """Rellena múltiples locators a partir de una lista de valores."""
    def fill(self, form_map: dict, field: str, value: Any):
        locators: List = form_map[field]
        if not isinstance(locators, list):
            locators = [locators]

        for i, val in enumerate(value):
            if i < len(locators):
                locators[i].fill(str(val))


# Aquí podrías añadir futuras estrategias más complejas, como...
# class DropdownFillStrategy(FormFillingStrategy):
#     def fill(self, form_map: dict, field: str, value: any):
#         # Lógica para seleccionar una opción en un dropdown
#         pass