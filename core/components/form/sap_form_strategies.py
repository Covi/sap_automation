# core/components/form/sap_form_strategies.py

from abc import ABC, abstractmethod
from typing import Any
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
        locator = form_map[field]
        
        # Usa el objeto playwright_page del contexto para realizar la acción
        # de Playwright, en lugar de recibirlo como un parámetro suelto.
        locator.fill(str(value))

class RangeFillStrategy(FormFillingStrategy):
    """Estrategia para formularios de rango: un valor "desde,hasta", dos locators."""
    
    def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: Any):
        """
        Implementación concreta para rellenar campos de rango.
        """
        partes = str(value).split(',')
        desde_val = partes[0].strip()
        hasta_val = partes[1].strip() if len(partes) > 1 else ""

        locator_or_key = form_map[field]
        
        # Inyecta el proveedor de localizadores del contexto de la página
        locator_provider = sap_page._provider

        if isinstance(locator_or_key, str):
            locators = locator_provider.get(locator_or_key)
        elif isinstance(locator_or_key, list) and all(isinstance(loc, Locator) for loc in locator_or_key):
            locators = locator_or_key
        else:
            raise TypeError(
                f"Tipo de locator inesperado para el campo de rango '{field}'. "
                f"Se esperaba 'str' o una lista de 'Locator'."
            )
        
        # Usa el objeto playwright_page del contexto
        if desde_val:
            sap_page.playwright_page.locator(locators[0]).fill(desde_val)
        if hasta_val:
            sap_page.playwright_page.locator(locators[1]).fill(hasta_val)

# Aquí podrías añadir futuras estrategias más complejas, como...
# class DropdownFillStrategy(FormFillingStrategy):
#     def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: any):
#         # Lógica para seleccionar una opción en un dropdown
#         pass