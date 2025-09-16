# Fichero: data_models/iq09_models.py
# Descripción: Modelos de datos para la transacción IQ09.

from pydantic import BaseModel, Field
from typing import Optional

class Iq09FormData(BaseModel):
    """
    Define la estructura y validación para el formulario de la transacción IQ09.
    Muestra el historial de números de serie.
    """
    material: Optional[str] = Field(None, description="Código de material")
    n_serie: Optional[str] = Field(None, description="Número de serie")
    centro: Optional[str] = Field(None, description="Código del centro")
    almacen: Optional[str] = Field(None, description="Código del almacén")

    # Aquí podrías añadir validadores en el futuro si los necesitas
    # ej: @field_validator('n_serie')