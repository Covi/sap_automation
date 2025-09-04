# core/providers/locator_provider_factory.py

from typing import Tuple, Any

# CAMBIO: Importamos las constantes de configuración que acabamos de definir
import config

# Importamos la ABSTRACCIÓN del provider
from .locators.base_locator_provider import BaseLocatorProvider
# Importamos las IMPLEMENTACIONES CONCRETAS que esta factory va a construir
from .locators.toml_locator_provider import TomlLocatorProvider
from .locators.composite_locator_provider import CompositeLocatorProvider

class LocatorProviderFactory:
    """
    Construye los providers necesarios para una transacción.
    
    Esta clase implementa el patrón Factory y su única responsabilidad (SRP)
    es saber CÓMO construir los providers a partir de una configuración centralizada.
    """
    def __init__(self, recipe: Any):
        """
        Inicializa la factory con una "receta" de transacción.
        
        Args:
            recipe: El objeto receta que contiene la configuración de la transacción.
        """
        self.recipe = recipe
        # CAMBIO: Ya no necesita calcular la ruta raíz del proyecto.
        # Esa lógica está ahora centralizada en config.py.

    def create_providers(self) -> Tuple[BaseLocatorProvider, BaseLocatorProvider, BaseLocatorProvider]:
        """
        Crea y devuelve una tupla con los providers necesarios:
        1. Provider para la página de Login.
        2. Provider compuesto para la página Easy Access.
        3. Provider compuesto para la página específica de la transacción.
        """
        
        # 1. Construcción de la ruta al fichero de la transacción
        # Se une la ruta base del directorio de locators con el nombre de fichero específico de la receta.
        tx_locator_filename = self.recipe.config_class.LOCATOR_FILE
        tx_locators_path = config.LOCATORS_DIR / tx_locator_filename

        # 2. Creación de los providers usando las rutas desde el módulo config
        common_provider = TomlLocatorProvider(config.COMMON_LOCATORS_PATH)
        login_provider = TomlLocatorProvider(config.LOGIN_LOCATORS_PATH)
        easy_access_provider = TomlLocatorProvider(config.EASY_ACCESS_LOCATORS_PATH)
        tx_provider = TomlLocatorProvider(tx_locators_path)

        # 3. Composición de providers para añadir los locators comunes
        composite_easy_access = CompositeLocatorProvider([easy_access_provider, common_provider])
        composite_tx = CompositeLocatorProvider([tx_provider, common_provider])

        # 4. Devolvemos los providers que el builder necesitará
        return login_provider, composite_easy_access, composite_tx