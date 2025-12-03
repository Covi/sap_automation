# config/__init__.py

import sys
from pathlib import Path
from .loader import ConfigLoader

# 1. Definimos las rutas CONSTANTES del sistema (relativas a este archivo)
#    Esto es robusto: subimos un nivel (..) desde config/ para llegar a la raíz.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TOML_PATH = _PROJECT_ROOT / "config" / "config.toml"
_ENV_PATH = _PROJECT_ROOT / ".env"

# 2. Instanciamos el Loader (El Obrero)
_loader = ConfigLoader(_TOML_PATH, _ENV_PATH)

# 3. Intentamos Cargar la Configuración (Singleton)
try:
    settings = _loader.load()
except Exception as e:
    # FAIL FAST: Si la configuración está mal, no dejamos arrancar el programa.
    # Imprimimos el error en rojo (stderr) y salimos.
    sys.stderr.write(f"\nCRITICAL CONFIGURATION ERROR:\n{e}\n\n")
    sys.exit(1)

# 4. Exponemos lo que el resto del programa necesita ver
#    Esto define la "API Pública" de tu paquete de configuración.
__all__ = ["settings", "PROJECT_ROOT", "LOCATORS_DIR"]

# Constantes útiles para otros módulos
PROJECT_ROOT = _PROJECT_ROOT
LOCATORS_DIR = _PROJECT_ROOT / "locators"