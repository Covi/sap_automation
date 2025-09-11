# services/zsin_ordenes_service.py

import logging
import subprocess
from pathlib import Path
from datetime import datetime

from data_models.zsin_ordenes_models import ZsinOrdenesFormData
from services.transaction_service import TransactionService
from pages.zsin_ordenes_page import ZsinOrdenesPage
from config import ZsinOrdenesConfig

log = logging.getLogger(__name__)

class ZsinOrdenesService:
    def __init__(self, transaction_service: TransactionService, page: ZsinOrdenesPage):
        self._transaction_service = transaction_service
        self._page = page
        self._config = ZsinOrdenesConfig()

    def run(self, form_data: ZsinOrdenesFormData, path: Path, filename: str):
        """Orquesta el flujo completo de la transacción ZSIN_ORDENES."""
        try:
            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)
            self._page.rellenar_formulario(form_data)
            self._page.ejecutar_busqueda()
            if not self._page.hay_resultados():
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return

            self._page.seleccionar_todas_las_ordenes()

            if form_data.reenviar:
                log.info("Ejecutando acción: Reenviar órdenes.")
                self._page.reenviar_ordenes()

            if form_data.imprimir:
                log.info("Ejecutando acción: Imprimir órdenes.")
                pdf_bytes = self._page.decargar_pdf(self._config.EXPORT_FILENAME)

                # El servicio se encarga de la lógica de guardado y nombrado del fichero
                directorio_descarga = path.parent
                directorio_descarga.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"{path.stem}_{timestamp}.pdf"
                pdf_path = directorio_descarga / pdf_filename
                
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                log.info(f"✅ PDF guardado con éxito en: {pdf_path.resolve()}")
                
                self._enviar_a_impresora(pdf_path)

        except Exception as e:
            log.error(f"Ha ocurrido un error en el servicio ZSIN_ORDENES: {e}", exc_info=True)
            raise

    def _enviar_a_impresora(self, ruta_fichero: Path):
        """Envía el fichero especificado a la cola de impresión del sistema (Linux/macOS)."""
        if not ruta_fichero.exists():
            log.error(f"El fichero {ruta_fichero} no existe. No se puede imprimir.")
            return

        try:
            log.info(f"Enviando '{ruta_fichero.name}' a la cola de impresión...")
            subprocess.run(['lp', str(ruta_fichero)], check=True, capture_output=True, text=True)
            log.info("✅ El fichero se ha enviado a la cola de impresión correctamente.")
        except FileNotFoundError:
            log.error("El comando 'lp' no se encontró. Asegúrate de estar en un sistema Linux/macOS o tener CUPS instalado.")
        except subprocess.CalledProcessError as e:
            log.error(f"Error al ejecutar el comando de impresión 'lp': {e.stderr}")