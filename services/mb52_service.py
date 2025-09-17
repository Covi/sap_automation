# Fichero: services/mb52_service.py

import logging
from pathlib import Path

# ## XXX CAMBIO 1: Se eliminan las importaciones de configuración concretas.

# ## XXX CAMBIO 2: Importamos los 'tipos' para el type hinting, no las implementaciones.
from pydantic import BaseModel
from config.settings import TransactionConfig
from services.transaction_service import TransactionService
from core.builders.sap_payload_builder import SapPayloadBuilder

from pages.mb52_page import MB52Page, Error

log = logging.getLogger(__name__)


class DownloadFailureError(Exception):
    pass

class MB52Service:
    """
    Servicio específico para la lógica de la transacción MB52.
    Recibe todas sus dependencias en el constructor.
    """
    # ## XXX CAMBIO 3: El constructor ahora recibe TODAS sus dependencias.
    def __init__(
        self,
        transaction_service: TransactionService,
        page: MB52Page,
        config: TransactionConfig,
        payload_builder: SapPayloadBuilder
    ):
        self._transaction_service = transaction_service
        self._page = page
        self.config = config
        self._payload_builder = payload_builder

    def run(self, form_data: BaseModel):
        """
        Orquesta el flujo completo de la transacción MB52.
        Ahora no necesita los parámetros 'path' y 'filename', los obtiene de su config.
        """
        try:
            # ## XXX CAMBIO 4: Usa la configuración y el builder inyectados.
            self._transaction_service.run_transaction(self.config.transaction_code)
            self.generar_informe(form_data)

            # Define la ruta de salida a partir de la configuración.
            downloads_dir = Path(self.config.download_dir)
            downloads_dir.mkdir(parents=True, exist_ok=True)
            output_file = downloads_dir / self.config.export_filename

            self.descargar_informe(output_file)

        except Exception as e:
            log.error(f"Error en {self.config.transaction_code}: {e}", exc_info=True)
            raise

    def generar_informe(self, form_data: BaseModel):
        """Genera el informe utilizando el payload builder inyectado."""
        # ## XXX CAMBIO 5: Usa la INSTANCIA del payload builder.
        payload = self._payload_builder.build_payload(form_data)
        self._page.rellenar_formulario(payload)
        self._page.ejecutar()

    def descargar_informe(self, fichero_de_salida_path: Path):
        """Descarga el informe generado."""
        if not self._page.is_results_table_visible():
            raise RuntimeError("No se puede descargar. La tabla de resultados no está visible.")
        log.info(f"Descargando informe en: {fichero_de_salida_path}")

        try:
            # ## XXX CAMBIO 6: El nombre del fichero ya no es un parámetro, viene de la ruta.
            download = self._page.descargar_hoja_calculo(fichero_de_salida_path.name)
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado.") from e