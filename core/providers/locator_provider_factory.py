# Fichero: core/providers/locator_provider_factory.py

from pathlib import Path
from typing import Sequence
from core.providers.locators.base_locator_provider import BaseLocatorProvider
from core.providers.locators.composite_locator_provider import CompositeLocatorProvider
from core.providers.locators.toml_locator_provider import TomlLocatorProvider

# ## XXX CABECERA: Factory AGNÓSTICA para locators.
class LocatorProviderFactory:
    """
    Crea CompositeLocatorProviders a partir de proveedores inyectados.
    Esta versión es completamente agnóstica y no conoce ficheros por sí misma.
    """

    def __init__(self, common_providers: Sequence[BaseLocatorProvider] | None = None):
        # Lista de providers "comunes" que se incluirán siempre
        self._common_providers = list(common_providers) if common_providers else []

    def create(self, specific_provider: BaseLocatorProvider) -> BaseLocatorProvider:
        """
        Construye un CompositeLocatorProvider que combina:
          - Un provider específico (inyección)
          - Los providers comunes (inyección)
        """
        all_providers = [specific_provider] + self._common_providers
        return CompositeLocatorProvider(all_providers)

