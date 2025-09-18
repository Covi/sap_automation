# Fichero: core/providers/locator_provider_factory.py

from typing import List

# Se importa la ruta base desde la configuración
from config.settings import LOCATORS_DIR
from .locators.base_locator_provider import BaseLocatorProvider
from .locators.toml_locator_provider import TomlLocatorProvider
from .locators.composite_locator_provider import CompositeLocatorProvider


class LocatorProviderFactory:
    """
    Construye un provider compuesto. Recibe una lista de providers comunes
    y los combina con el provider específico solicitado.
    """
    # El constructor ahora declara explícitamente su dependencia.
    # Acepta una lista de providers, lo que lo hace más flexible.
    def __init__(self, common_providers: List[BaseLocatorProvider]):
        """
        Inicializa la fábrica con los providers comunes que se usarán en cada composición.

        Args:
            common_providers: Una lista de instancias de BaseLocatorProvider (ej: [TomlLocatorProvider(...)])
        """
        self.common_providers = common_providers

    def create(self, locator_filename: str) -> BaseLocatorProvider:
        """
        Crea un provider compuesto para un fichero de localizadores específico.

        Args:
            locator_filename: El nombre del fichero (ej: "login.toml").

        Returns:
            Un CompositeLocatorProvider que une el provider específico y los comunes.
        """
        specific_path = LOCATORS_DIR / locator_filename
        specific_provider = TomlLocatorProvider(specific_path)

        # CAMBIO 3: Se usa el operador splat (*) para expandir la lista de providers comunes.
        return CompositeLocatorProvider(providers=[specific_provider, *self.common_providers])