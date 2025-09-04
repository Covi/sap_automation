# core/components/sap_form_strategies.py

from abc import ABC, abstractmethod
from typing import Any
# La estrategia ahora también depende de la abstracción de la página.
from pages.sap_page_base import SAPPageBase

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

# Aquí podrías añadir futuras estrategias más complejas, como...
# class DropdownFillStrategy(FormFillingStrategy):
#     def fill(self, sap_page: SAPPageBase, form_map: dict, field: str, value: any):
#         # Lógica para seleccionar una opción en un dropdown
#         pass