# Fichero: data_models/zsin_ordenes_models.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional

class ZsinOrdenesFormData(BaseModel):
    """
    Define la estructura de datos para la transacción ZSIN_ORDENES.
    No realiza transformaciones de formato, solo valida la existencia de campos.
    """
    
    # --- Campos del Formulario con Valores por Defecto ---
    status: Optional[str] = Field(default='SE,')
    clase: Optional[str] = Field(default='ZR04,ZR05')
    cliente: Optional[str] = Field(default=None)
    mecanico: Optional[str] = Field(default=None)
    fechainicio: Optional[str] = Field(default=None)
    fechatope: Optional[str] = Field(default=None)
    fechacreacion: Optional[str] = Field(default=None)

    # --- Flags de Comportamiento ---
    imprimir: bool = False
    reenviar: bool = False
    
    # --- Parámetro de Ejecución ---
    output: Optional[str] = Field(default=None)

    @model_validator(mode='after')
    def validar_al_menos_un_filtro(self) -> 'ZsinOrdenesFormData':
        """Asegura que al menos un campo de filtrado tenga un valor."""
        campos_de_filtro = [
            self.status,
            self.clase,
            self.cliente,
            self.mecanico,
            self.fechainicio,
            self.fechatope,
            self.fechacreacion
        ]

        if not any(campos_de_filtro):
            raise ValueError(
                "La ejecución fue bloqueada: se debe proporcionar al menos un criterio de búsqueda."
            )
        
        return self