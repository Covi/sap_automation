from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Tuple
from datetime import date

# --- Se importan las dos utilidades especializadas ---
from utils.date_utils import DateUtils
from utils.range_parser import RangeParser


class ZsinOrdenesFormData(BaseModel):
    """
    Define la estructura de datos para la transacción ZSIN_ORDENES.
    Valida la entrada de todos los campos como rangos y la almacena en tipos de datos puros (tuplas).
    """

    # --- Campos del Formulario (Todos son rangos) ---
    # Los valores por defecto se definen como tuplas para cumplir con Pydantic
    status: Optional[Tuple[Optional[str], Optional[str]]] = Field(default=('SE', ''))
    clase: Optional[Tuple[Optional[str], Optional[str]]] = Field(default=('ZR04', 'ZR05'))
    cliente: Optional[Tuple[Optional[str], Optional[str]]] = None
    mecanico: Optional[Tuple[Optional[str], Optional[str]]] = None
    fechainicio: Optional[Tuple[Optional[date], Optional[date]]] = None
    fechatope: Optional[Tuple[Optional[date], Optional[date]]] = None
    fechacreacion: Optional[Tuple[Optional[date], Optional[date]]] = None

    # --- Flags de Comportamiento (No son rangos) ---
    imprimir: bool = False
    reenviar: bool = False

    # --- Parámetro de Ejecución ---
    output: Optional[str] = None

    # --- Validadores ---
    @field_validator("status", "clase", "cliente", "mecanico", mode="before")
    @classmethod
    def validar_rangos_texto(cls, valor: Optional[str]) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Usa RangeParser para convertir un string en una tupla de strings.
        """
        if valor is None:
            return None
        return RangeParser.parse(valor)

    @field_validator("fechainicio", "fechatope", "fechacreacion", mode="before")
    @classmethod
    def validar_rangos_fecha(cls, valor: Optional[str]) -> Optional[Tuple[Optional[date], Optional[date]]]:
        """
        Orquesta el parseo de un rango de fechas:
        1. Usa RangeParser para separar el string.
        2. Usa DateUtils para parsear cada parte a un objeto date.
        """
        if valor is None:
            return None

        desde_str, hasta_str = RangeParser.parse(valor)

        desde_date = DateUtils.parsear_fecha(desde_str)
        hasta_date = DateUtils.parsear_fecha(hasta_str)

        return (desde_date, hasta_date)

    @model_validator(mode="after")
    def validar_al_menos_un_filtro(self) -> "ZsinOrdenesFormData":
        """
        Valida que al menos un campo de filtro tenga valor.
        """
        campos = [
            self.status,
            self.clase,
            self.cliente,
            self.mecanico,
            self.fechainicio,
            self.fechatope,
            self.fechacreacion,
        ]
        if not any(campos):
            raise ValueError("Se debe proporcionar al menos un criterio de búsqueda.")
        return self
