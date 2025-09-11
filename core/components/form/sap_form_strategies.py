# core/components/form/sap_form_strategies.py

from abc import ABC, abstractmethod
from typing import Any, List

# La estrategia ahora también depende de la abstracción de la página.
from pages.sap_page_base import SAPPageBase, Locator

class FormFillingStrategy(ABC):
    """
    Interfaz para diferentes estrategias de rellenado de formularios.
    Define el contrato que todas las estrategias concretas deben seguir.
    """
    @abstractmethod
    def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: Any):
        """
        Define cómo rellenar un campo específico del formulario.

        Args:
            sap_page: El objeto de página SAP que proporciona el contexto.
            form_map: El diccionario que mapea nombres de campo a locators.
            field: El nombre del campo a rellenar.
            value: El valor a introducir en el campo.
        """
        pass

class SimpleFillStrategy(FormFillingStrategy):
    """
    Una estrategia simple que localiza un campo y le introduce un valor.
    """
    def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: Any):
        """
        Implementación concreta del rellenado simple.
        """
        # Obtiene el locator del mapa
        locator: Locator = form_map[field]
        
        # Usa el objeto playwright_page del contexto para realizar la acción
        # de Playwright, en lugar de recibirlo como un parámetro suelto.
        locator.fill(str(value))

class RangeFillStrategy(FormFillingStrategy):
    """Estrategia para formularios de rango: un valor "desde,hasta", dos locators."""
    
    def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: Any):
        """
        Implementación concreta y estricta para rellenar campos de rango.
        """
        # 1. Valida que el valor de entrada tenga formato de rango.
        if ',' not in str(value):
            raise ValueError(
                f"El valor para el campo de rango '{field}' es inválido. "
                f"Se esperaba un formato 'desde,hasta', pero se recibió '{value}'."
            )

        # 2. Valida que el mapa de locators sea una lista de 2 elementos.
        locators: List[Locator] = form_map[field]
        if not isinstance(locators, list) or len(locators) != 2:
            raise TypeError(
                f"La estrategia de rango para el campo '{field}' esperaba una lista de 2 Locators."
            )

        # 3. Procesa los valores y los asigna a los locators.
        partes = str(value).split(',', 1)
        desde_val = partes[0].strip()
        hasta_val = partes[1].strip()

        if desde_val:
            locators[0].fill(desde_val)
        if hasta_val:
            locators[1].fill(hasta_val)

# Aquí podrías añadir futuras estrategias más complejas, como...
# class DropdownFillStrategy(FormFillingStrategy):
#     def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: any):
#         # Lógica para seleccionar una opción en un dropdown
#         pass