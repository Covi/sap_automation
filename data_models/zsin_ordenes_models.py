# Fichero: data_models/zsin_ordenes_models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from utils.date_utils import DateUtils

class ZsinOrdenesFormData(BaseModel):
    """
    Define la estructura y validación de datos para la transacción ZSIN_ORDENES.
    No conoce sus valores por defecto; solo su forma y reglas.
    """
    
    # --- Campos del Formulario (sin valores por defecto de negocio) ---
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
    output: Optional[str] = Field(default=None)

    # --- VALIDATORS (sin cambios) ---
    @field_validator("fechainicio", "fechatope", "fechacreacion", mode="before")
    def formatear_fechas_a_formato_sap(cls, valor: Optional[str]) -> Optional[str]:
        if not valor or not valor.strip():
            return None
        fecha_dt = DateUtils.parsear_fecha(valor)
        if not fecha_dt:
            raise ValueError(f"El formato de fecha '{valor}' no es válido.")
        return fecha_dt.strftime("%d.%m.%Y")

    @model_validator(mode='after')
    def validar_al_menos_un_filtro(self) -> 'ZsinOrdenesFormData':
        campos_de_filtro = [
            self.status, self.clase, self.cliente, self.mecanico,
            self.fechainicio, self.fechatope, self.fechacreacion
        ]
        if not any(campos_de_filtro):
            raise ValueError(
                "La ejecución fue bloqueada: se debe proporcionar al menos un criterio de búsqueda."
            )
        return self