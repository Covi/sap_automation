# Fichero: data_models/zsin_ordenes_models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any
from utils.date_utils import DateUtils

class ZsinOrdenesFormData(BaseModel):
    """
    Define la estructura de datos para la transacción ZSIN_ORDENES,
    incluyendo validación, formateo y valores por defecto.
    """
    
    # --- Campos del Formulario con Valores por Defecto ---
    # Si no se proporciona un valor, se usarán estos para ejecuciones desatendidas.
    status: Optional[str] = Field(default='SE')
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

    # --- VALIDATORS ---
    @field_validator("fechainicio", "fechatope", "fechacreacion", mode="before")
    def formatear_fechas_a_formato_sap(cls, valor: Optional[str]) -> Optional[str]:
        if not valor or not valor.strip():
            return None
        
        fecha_dt = DateUtils.parsear_fecha(valor)
        if not fecha_dt:
            raise ValueError(f"El formato de fecha '{valor}' no es válido.")
            
        return fecha_dt.strftime("%d.%m.%Y")

    # --- NUEVO: Validador de Modelo (root_validator en Pydantic v1) ---
    @model_validator(mode='after')
    def validar_al_menos_un_filtro(self) -> 'ZsinOrdenesFormData':
        """
        Asegura que al menos un campo de filtrado tenga un valor
        para evitar ejecuciones demasiado amplias o sin sentido.
        """
        campos_de_filtro = [
            self.status,
            self.clase,
            self.cliente,
            self.mecanico,
            self.fechainicio,
            self.fechatope,
            self.fechacreacion
        ]

        # La función 'any' comprueba si al menos un valor de la lista es "verdadero"
        # (no es None ni una cadena vacía).
        if not any(campos_de_filtro):
            raise ValueError(
                "La ejecución fue bloqueada: se debe proporcionar al menos un criterio de búsqueda "
                "(status, clase, cliente, mecanico o alguna fecha)."
            )
        
        return self