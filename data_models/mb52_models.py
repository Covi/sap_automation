# Fichero: data_models/mb52_models.py
# Descripción: Modelos de datos para la transacción MB52.

from dataclasses import dataclass
from typing import Optional

@dataclass
class Mb52FormData:
    """Define la estructura de datos para el formulario de la MB52."""
    material: Optional[str] = None
    centro: Optional[str] = None
    almacen: Optional[str] = None