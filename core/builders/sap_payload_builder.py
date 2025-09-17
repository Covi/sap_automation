# Fichero: builders/sap_payload_builder.py

from datetime import date
from pydantic import BaseModel
from typing import Any

# 1. Importamos la 'abstracción' de la que dependeremos: nuestra dataclass.
#    Ya no importamos una configuración específica.
from config.settings import TransactionConfig

# 2. Importamos los formatters como antes.
from . import formatters


class SapPayloadBuilder:
    """
    Genera payloads específicos para la UI de SAP.
    Convierte tipos de datos puros del modelo en los strings que la UI necesita.
    Ahora es una clase que se instancia.
    """
    # 3. El constructor recibe la configuración (Inyección de Dependencias).
    def __init__(self, config: TransactionConfig):
        """
        Inicializa el builder con una configuración de transacción específica.
        """
        self.config = config

    # 4. El método ahora es de instancia (usa 'self' en lugar de 'cls').
    def build_payload(self, form_data: BaseModel) -> dict:
        """
        Toma un modelo Pydantic y lo convierte en un diccionario listo
        para la UI, usando la configuración inyectada.
        """
        payload = form_data.model_dump(exclude_none=True)

        for key, value in payload.items():
            # 5. Se usa la configuración de la instancia: self.config
            date_format = self.config.date_format

            if isinstance(value, tuple):
                payload[key] = formatters.format_tuple(
                    value, date_formatter=lambda d: formatters.format_date(d, date_format)
                )
            elif isinstance(value, date):
                payload[key] = formatters.format_date(value, date_format)
            elif isinstance(value, bool):
                payload[key] = formatters.format_bool(value)
            else:
                payload[key] = str(value)

        return payload