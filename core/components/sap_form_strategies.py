# Fichero: core/components/form_strategies.py

from playwright.sync_api import Page, Locator
from abc import ABC, abstractmethod
from typing import Any
from core.providers.base_provider import BaseLocatorProvider

class FormFillingStrategy(ABC):
    """Interfaz para definir una estrategia de rellenado de formulario."""
    def fill(self, page: Page, locator_provider: BaseLocatorProvider, form_map: dict, field: str, value: Any):
        pass

class SimpleFillStrategy(FormFillingStrategy):
    """Estrategia para formularios simples: un valor, un locator."""
    def fill(self, page: Page, locator_provider: BaseLocatorProvider, form_map: dict, field: str, value: Any):
        locator_or_key = form_map[field]
        
        if isinstance(locator_or_key, str):
            # Si se pasa una clave de texto, se busca el selector
            locator_str = locator_provider.get(locator_or_key)
            page.locator(locator_str).fill(str(value))
        elif isinstance(locator_or_key, Locator):
            # Si se pasa un objeto Locator, se usa directamente
            locator_or_key.fill(str(value))
        else:
            raise TypeError(
                f"Tipo de locator inesperado para el campo '{field}'. Se esperaba 'str' o 'Locator'."
            )

class RangeFillStrategy(FormFillingStrategy):
    """Estrategia para formularios de rango: un valor "desde,hasta", dos locators."""
    def fill(self, page: Page, locator_provider: BaseLocatorProvider, form_map: dict, field: str, value: Any):
        partes = str(value).split(',')
        desde_val = partes[0].strip()
        hasta_val = partes[1].strip() if len(partes) > 1 else ""

        locator_or_key = form_map[field]
        
        if isinstance(locator_or_key, str):
            locators = locator_provider.get(locator_or_key)
        elif isinstance(locator_or_key, list) and all(isinstance(loc, Locator) for loc in locator_or_key):
            locators = locator_or_key
        else:
            raise TypeError(
                f"Tipo de locator inesperado para el campo de rango '{field}'. "
                f"Se esperaba 'str' o una lista de 'Locator'."
            )
        
        if desde_val:
            page.locator(locators[0]).fill(desde_val)
        if hasta_val:
            page.locator(locators[1]).fill(hasta_val)