# core/providers/toml_locator_provider.py
# Proveedor de locators que lee desde un fichero TOML

import toml
from typing import Dict, Any
from .base_locator_provider import BaseLocatorProvider

class TomlLocatorProvider(BaseLocatorProvider):
    """
    Implementación concreta que lee locators desde un fichero TOML.
    """
    def __init__(self, file_path: str):
        try:
            self._locators: Dict[str, Any] = toml.load(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"El fichero de locators no se encontró en la ruta: {file_path}")
        except Exception as e:
            raise IOError(f"Error al leer o parsear el fichero TOML {file_path}: {e}")

    def get(self, locator_key: str) -> str:
        """
        Obtiene un locator específico usando una clave anidada con puntos.
        Ejemplo: get('form.material')
        """
        keys = locator_key.split('.')
        value = self._locators
        try:
            for key in keys:
                value = value[key]
            if not isinstance(value, str):
                raise TypeError(f"El locator para '{locator_key}' no es una cadena de texto.")
            return value
        except KeyError:
            raise KeyError(f"El locator '{locator_key}' no se encontró en el fichero.")
        except TypeError:
            raise KeyError(f"Clave inválida o estructura incorrecta al buscar '{locator_key}'.")