# Fichero: data_models/zsin_ordenes_models.py

# 1. Se importa 'field_validator' en lugar de 'validator'
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from utils.date_utils import DateUtils

class ZsinOrdenesFormData(BaseModel):
    """
    Define la estructura de datos para la transacción ZSIN_ORDENES,
    incluyendo validación y formateo automático de campos con sintaxis Pydantic V2.
    """
    
    # --- Campos del Formulario ---
    status: Optional[str] = Field(default=None)
    clase: Optional[str] = Field(default=None)
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

    # --- VALIDATORS ---
    @field_validator("fechainicio", "fechatope", "fechacreacion", mode="before")
    def formatear_fechas_a_formato_sap(cls, valor: Optional[str]) -> Optional[str]:
        """
        Toma una fecha en formato flexible y la convierte al que SAP espera ('dd.mm.YYYY').
        """
        if not valor or not valor.strip():
            return None
        
        fecha_dt = DateUtils.parsear_fecha(valor)
        if not fecha_dt:
            raise ValueError(f"El formato de fecha '{valor}' no es válido.")
            
        return fecha_dt.strftime("%d.%m.%Y")