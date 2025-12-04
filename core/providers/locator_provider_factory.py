# core/providers/locator_provider_factory.py

# CAMBIO: Importamos la constante válida definida en tu __init__.py
from config import LOCATORS_DIR
from .locators.base_locator_provider import BaseLocatorProvider
from .locators.toml_locator_provider import TomlLocatorProvider
from .locators.composite_locator_provider import CompositeLocatorProvider

class LocatorProviderFactory:
    """
    Construye un provider compuesto bajo demanda para un fichero de localizadores específico.
    """

    # FIXME: [DIP Violation] Acoplamiento fuerte con configuración global.
    # FECHA: 2025-12-04
    # PROBLEMA: La factory importa 'config.LOCATORS_DIR' directamente, impidiendo testear
    #           con rutas falsas o reutilizar la clase en otros contextos.
    # SOLUCIÓN PROPUESTA:
    #   1. Eliminar 'from config import ...'.
    #   2. Inyectar 'common_path' y 'locators_dir' en el __init__.
    #   3. Mover la responsabilidad de proveer las rutas al Composition Root (main.py).
    def __init__(self):
        # CAMBIO: Construimos la ruta dinámicamente usando la base del SSOT.
        # Asumimos que el archivo común se llama 'common.toml' y está en la raíz de locators.
        common_path = LOCATORS_DIR / "common.toml"

        # La factory pre-carga el provider común
        self.common_provider = TomlLocatorProvider(common_path)

    def create(self, locator_filename: str) -> BaseLocatorProvider:
        """
        Crea un provider compuesto para un fichero de localizadores específico.

        Args:
            locator_filename: El nombre del fichero (ej: "login.toml", "mb52.toml").

        Returns:
            Un CompositeLocatorProvider que incluye los localizadores específicos y los comunes.
        """
        specific_path = LOCATORS_DIR / locator_filename
        specific_provider = TomlLocatorProvider(specific_path)
        
        # El proveedor compuesto ahora incluye el específico, el de los componentes y el común.
        return CompositeLocatorProvider([specific_provider, self.common_provider])

    """
    # FIXME TODO: FUTURO REFACTOR (No hacer hoy)
    class LocatorProviderFactory:
        def __init__(self, common_path: Path, locators_dir: Path):
            # Inyección pura: La factory no sabe de dónde vienen las rutas
            self.common_provider = TomlLocatorProvider(common_path)
            self.locators_dir = locators_dir

        def create(self, filename: str):
            # Usa las rutas inyectadas
            return CompositeLocatorProvider(...)

    # En main.py luego: 
    factory = LocatorProviderFactory(
        common_path=settings.paths.common_locators, # Aquí inyectas la config
        locators_dir=settings.paths.locators_dir
    )
    """