# core/providers/toml_locator_provider.py
# Proveedor de locators que lee desde un fichero TOML

import toml
from pathlib import Path
from typing import Dict, Any
from .base_locator_provider import BaseLocatorProvider

class TomlLocatorProvider(BaseLocatorProvider):
    """
    Implementación concreta que lee locators desde un fichero TOML.
    """
    def __init__(self, file_path: str | Path):
        """
        Inicializa el provider con la ruta a un fichero TOML.
        Acepta tanto una cadena de texto (str) como un objeto Path.
        """
        path_obj = Path(file_path)
        
        try:
            # Usamos el objeto Path directamente, ya que toml lo soporta.
            self._locators: Dict[str, Any] = toml.load(path_obj)
        except FileNotFoundError:
            raise FileNotFoundError(f"El fichero de locators no se encontró en la ruta: {path_obj}")
        except Exception as e:
            raise IOError(f"Error al leer o parsear el fichero TOML {path_obj}: {e}")

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