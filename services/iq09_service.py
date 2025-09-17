# Fichero: services/iq09_service.py

import logging
from pathlib import Path
from pydantic import BaseModel

# ## XXX CAMBIO 1: Se eliminan las importaciones antiguas y se añaden los tipos necesarios.
from config.settings import TransactionConfig
from services.transaction_service import TransactionService
from pages.iq09_page import Iq09Page
from core.builders.sap_payload_builder import SapPayloadBuilder

log = logging.getLogger(__name__)

class IQ09Service:
    """
    Servicio específico para la lógica de la transacción IQ09.
    """
    # ## XXX CAMBIO 2: El constructor recibe todas sus dependencias.
    def __init__(
        self,
        transaction_service: TransactionService,
        page: Iq09Page,
        config: TransactionConfig,
        payload_builder: SapPayloadBuilder
    ):
        self._transaction_service = transaction_service
        self._page = page
        self.config = config
        self._payload_builder = payload_builder

    def run(self, form_data: BaseModel, path: Path, filename: str):
        """
        Orquesta el flujo completo de la transacción IQ09.
        """
        # ## XXX CAMBIO 3: Utiliza las dependencias inyectadas.
        log.info(f"Ejecutando servicio para la transacción {self.config.transaction_code}")
        self._transaction_service.run_transaction(self.config.transaction_code)

        payload = self._payload_builder.build_payload(form_data)
        
        # Esta es una implementación de ejemplo, ajústala a tu lógica real
        self._page.rellenar_formulario(payload)
        self._page.execute()
        self._page.descargar_informe()