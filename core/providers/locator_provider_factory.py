# core/providers/locator_provider_factory.py

import config

from .locators.base_locator_provider import BaseLocatorProvider
from .locators.toml_locator_provider import TomlLocatorProvider
from .locators.composite_locator_provider import CompositeLocatorProvider

class LocatorProviderFactory:
    """
    Construye un provider compuesto bajo demanda para un fichero de localizadores específico.
    """
    def __init__(self):
        # La factory pre-carga el provider común
        self.common_provider = TomlLocatorProvider(config.COMMON_LOCATORS_PATH)

    def create(self, locator_filename: str) -> BaseLocatorProvider:
        """
        Crea un provider compuesto para un fichero de localizadores específico.

        Args:
            locator_filename: El nombre del fichero (ej: "login.toml", "mb52.toml").

        Returns:
            Un CompositeLocatorProvider que incluye los localizadores específicos y los comunes.
        """
        specific_path = config.LOCATORS_DIR / locator_filename
        specific_provider = TomlLocatorProvider(specific_path)
        
        # El proveedor compuesto ahora incluye el específico, el de los componentes y el común.
        return CompositeLocatorProvider([specific_provider, self.common_provider])