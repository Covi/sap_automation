# schemas/zsin_ordenes.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Tuple
from datetime import date
from pathlib import Path
from utils.date_utils import DateUtils
from utils.range_parser import RangeParser

class ZsinOrdenesCriteria(BaseModel):
    """
    Define los CRITERIOS DE BÚSQUEDA para la transacción ZSIN_ORDENES.
    Su única responsabilidad es validar y almacenar los filtros del formulario.
    """
    status: Optional[Tuple[Optional[str], Optional[str]]] = Field(default=('SE', ''))
    clase: Optional[Tuple[Optional[str], Optional[str]]] = Field(default=('ZR04', 'ZR05'))
    cliente: Optional[Tuple[Optional[str], Optional[str]]] = None
    mecanico: Optional[Tuple[Optional[str], Optional[str]]] = None
    fechainicio: Optional[Tuple[Optional[date], Optional[date]]] = None
    fechatope: Optional[Tuple[Optional[date], Optional[date]]] = None
    fechacreacion: Optional[Tuple[Optional[date], Optional[date]]] = None

    @field_validator("status", "clase", "cliente", "mecanico", mode="before")
    @classmethod
    def validar_rangos_texto(cls, valor: Optional[str]) -> Optional[Tuple[Optional[str], Optional[str]]]:
        if valor is None: return None
        return RangeParser.parse(valor)

    @field_validator("fechainicio", "fechatope", "fechacreacion", mode="before")
    @classmethod
    def validar_rangos_fecha(cls, valor: Optional[str]) -> Optional[Tuple[Optional[date], Optional[date]]]:
        if valor is None: return None
        desde_str, hasta_str = RangeParser.parse(valor)
        desde_date = DateUtils.parsear_fecha(desde_str)
        hasta_date = DateUtils.parsear_fecha(hasta_str)
        return (desde_date, hasta_date)

    @model_validator(mode="after")
    def validar_al_menos_un_filtro(self) -> "ZsinOrdenesCriteria":
        campos = [self.status, self.clase, self.cliente, self.mecanico, self.fechainicio, self.fechatope, self.fechacreacion]
        if not any(campos):
            raise ValueError("Se debe proporcionar al menos un criterio de búsqueda.")
        return self


class ZsinOrdenesExecutionOptions(BaseModel):
    """
    Define las OPCIONES DE EJECUCIÓN para el servicio ZSIN_ORDENES.
    Su única responsabilidad es definir la ESTRUCTURA de las opciones.
    """
    imprimir: bool = False
    reenviar: bool = False

    output_path: Path
    output_filename: str
    wait_after_results: bool = False