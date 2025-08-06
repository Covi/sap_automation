# Fichero: data_models/mb52_models.py
# Descripción: Modelos de datos para la transacción MB52.

from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Mb52FormData(BaseModel):
    """Define la estructura y validación para el formulario MB52."""

    material: Optional[str] = Field(None, description="Código de material")
    centro: Optional[str] = Field(None, description="Código del centro")
    almacen: Optional[str] = Field(None, description="Código del almacén")

    @field_validator('centro')
    def validar_centro(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError("El código de centro debe ser alfanumérico")
        return v

    @field_validator('material')
    def validar_material(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("El código de material debe tener al menos 3 caracteres")
        return v