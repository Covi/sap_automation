# core/providers/locators/toml_locator_provider.py

import toml
from pathlib import Path
from typing import Dict, Any, List
from .base_locator_provider import BaseLocatorProvider

class TomlLocatorProvider(BaseLocatorProvider):
    """
    Implementación concreta que lee locators desde un fichero TOML.
    """
    def __init__(self, file_path: str | Path):
        path_obj = Path(file_path)
        try:
            self._locators: Dict[str, Any] = toml.load(path_obj)
        except FileNotFoundError:
            raise FileNotFoundError(f"El fichero de locators no se encontró en la ruta: {path_obj}")
        except Exception as e:
            raise IOError(f"Error al leer o parsear el fichero TOML {path_obj}: {e}")

    def get(self, locator_key: str) -> str | List[str]:
        """
        Obtiene un locator o una lista de locators usando una clave anidada.
        Ejemplo: get('form.material') -> str
                 get('form.status')  -> List[str]
        """
        keys = locator_key.split('.')
        value = self._locators
        try:
            for key in keys:
                value = value[key]
            
            # --- CORRECCIÓN ---
            # Ahora se permite que el valor sea un string O una lista.
            if not isinstance(value, (str, list)):
                raise TypeError(f"El locator para '{locator_key}' no es una cadena de texto ni una lista.")
            
            return value
        except KeyError:
            raise KeyError(f"El locator '{locator_key}' no se encontró en el fichero.")
        except TypeError:
            raise KeyError(f"Clave inválida o estructura incorrecta al buscar '{locator_key}'.")