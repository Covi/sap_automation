# builders/sap_payload_builder.py

from datetime import date
from pydantic import BaseModel
from typing import Any, Dict, Callable, Tuple

# FIXME a ver si esto se inyecta o qué
from config import ZsinOrdenesConfig
config = ZsinOrdenesConfig()

from . import formatters


class SapPayloadBuilder:
    """
    Genera payloads específicos para la UI de SAP.
    Convierte tipos de datos puros del modelo (ej: date, bool, tuple)
    en los strings que la UI de SAP necesita.
    """
    # Formato de fecha configurable desde el builder
    DATE_FORMAT = config.DATE_FORMAT

    @classmethod
    def build_payload(cls, form_data: BaseModel) -> dict:
        """
        Toma un modelo Pydantic y lo convierte en un diccionario listo
        para la UI, aplicando la lógica de formato correcta para cada tipo de dato.
        """
        payload = form_data.model_dump()

        for key, value in payload.items():
            if value is None:
                continue

            # Caso 1: El valor es una tupla (rango)
            if isinstance(value, tuple):
                payload[key] = formatters.format_tuple(
                    value, date_formatter=lambda d: formatters.format_date(d, cls.DATE_FORMAT)
                )
            # Caso 2: El valor es un tipo simple
            elif isinstance(value, date):
                payload[key] = formatters.format_date(value, cls.DATE_FORMAT)
            elif isinstance(value, bool):
                payload[key] = formatters.format_bool(value)
            else:
                payload[key] = str(value)

        return payload
